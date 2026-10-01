"""
preprocess_for_pandoc.py (v26 rebuild)

Turns the IEEEtran LaTeX source (main.tex + sections/*.tex) into a single,
pandoc-digestible .tex file: strips \\resizebox and \\subequations wrappers
pandoc chokes on, converts algorithm/algorithmic environments to plain nested
lists, resolves \\Cref{} to literal "Table N"/"Fig. N"/"Eq. (Na)" text via
hardcoded maps built from the document's actual current section order and
\\label placement (re-derived fresh for v26 -- the maps are NOT reused from
v25 since a new table (tab:ns3_validation) was inserted), resolves \\cite{}
to numbered brackets by first-appearance order, and injects a plain-text
bibliography built from references.bib for only the keys actually cited.

Run from this directory: python3 preprocess_for_pandoc.py
"""
import os
import re

SRC_DIR = "/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/MA_ROPE/MASTER/MA_ROPE_MASTER_v21"
OUT_PATH = os.path.join(os.path.dirname(__file__), "pandoc_ready.tex")

# Document order per main.tex's actual \input list (methodology.tex and
# results.tex exist on disk but are NOT \input anywhere -- excluded).
SECTION_ORDER = [
    "abstract", "introduction", "related_work", "system_model",
    "algorithm_design", "experiments", "results_part1", "results_part2",
    "conclusion",
]

# ---- Figure/table/equation numbering maps, built from document order ----
FIG_NUM = {
    "fig:gap_matrix": 1, "fig:waterfall": 2, "fig:architecture": 3,
    "fig:mdp_formulation": 4, "fig:utility_speed": 5,
    "fig:prr_speed": 6, "fig:queue_loss": 7, "fig:system_utility": 8,
    "fig:fleet_otr": 9, "fig:queue_contention": 10, "fig:jakes_fading": 11,
    "fig:dqn_rat_dist": 12, "fig:training_convergence": 13,
}
TAB_NUM = {
    "tab:literature": 1, "tab:rat_physical": 2, "tab:dual_utility": 3,
    "tab:packet_stats": 4, "tab:deadline_analysis": 5,
    "tab:full_performance": 6, "tab:safety_task": 7, "tab:why_marope_wins": 8,
    "tab:dqn_inference": 9, "tab:action_space": 10, "tab:env_step": 11,
    "tab:multi_rat": 12, "tab:ns3_validation": 13,
}
# Equation numbers, with subequations groups getting letter suffixes.
EQ_NUM = {
    "eq:sinr": "1", "eq:prr": "2",
    "eq:latency_all": "3", "eq:ltotal_base": "3a", "eq:ltotal_partial": "3b", "eq:otr": "3c",
    "eq:utility_all": "4", "eq:uprr": "4a", "eq:uotr": "4b", "eq:z": "4c",
    "eq:state": "5", "eq:rho_final": "6", "eq:ddqn": "7", "eq:fedavg": "8",
    "eq:drr": "9",
}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]


def to_roman(n):
    return ROMAN[n - 1] if 1 <= n <= len(ROMAN) else str(n)


# ---- citation order: first appearance, scanning sections in document order ----
def build_citation_order():
    order = []
    seen = set()
    for name in SECTION_ORDER:
        path = os.path.join(SRC_DIR, "sections", f"{name}.tex")
        if not os.path.exists(path):
            continue
        text = open(path).read()
        for m in re.finditer(r"\\cite\{([^}]*)\}", text):
            for key in m.group(1).split(","):
                key = key.strip()
                if key and key not in seen:
                    seen.add(key)
                    order.append(key)
    return order


def parse_bib(bib_path):
    text = open(bib_path).read()
    entries = {}
    for m in re.finditer(r"@(\w+)\{(\w+),(.*?)\n\}", text, re.DOTALL):
        etype, key, body = m.group(1), m.group(2), m.group(3)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n", body, re.DOTALL):
            fields[fm.group(1)] = re.sub(r"\s+", " ", fm.group(2)).strip()
        entries[key] = fields
    return entries


def format_ref(key, fields):
    author = fields.get("author", "")
    title = fields.get("title", "")
    journal = fields.get("journal") or fields.get("booktitle", "")
    year = fields.get("year", "")
    vol = fields.get("volume", "")
    num = fields.get("number", "")
    pages = fields.get("pages", "")
    parts = [f"{author}, \u201c{title},\u201d"]
    if journal:
        parts.append(f"{journal},")
    if vol:
        v = f"vol. {vol}"
        if num:
            v += f", no. {num}"
        parts.append(v + ",")
    if pages:
        parts.append(f"pp. {pages},")
    if year:
        parts.append(f"{year}.")
    return " ".join(parts)


def strip_resizebox(text):
    # \resizebox{\columnwidth}{!}{% ... }\n  -- remove the wrapper, keep content.
    # The opening call is always on its own line ending in "{%"; the matching
    # close is the lone "}" line immediately before \end{tabular}'s next "}".
    text = re.sub(r"\\resizebox\{\\columnwidth\}\{!\}\{%\n", "", text)
    # Remove the now-orphaned closing "}%" or "}" line that paired with it --
    # heuristic: a line containing only "}" or "}%" right after \end{tabular}.
    text = re.sub(r"(\\end\{tabular\}%?\n)\}%?\n", r"\1", text)
    return text


def strip_subequations(text):
    text = text.replace("\\begin{subequations}", "")
    text = text.replace("\\end{subequations}", "")
    # The subequations group label (e.g. \label{eq:latency_all}) has no
    # standalone rendered equation to attach to -- drop it, the individual
    # \label{eq:ltotal_base} etc. inside still resolve via EQ_NUM.
    for group_label in ["eq:latency_all", "eq:utility_all"]:
        text = text.replace(f"\\label{{{group_label}}}\n", "")
    return text


def strip_braced_macro(text, macro, replacement_fmt="{}"):
    """Removes \\macro{...} respecting nested braces (e.g. \\Cref{x} inside
    the comment text), replacing with replacement_fmt.format(inner)."""
    tag = "\\" + macro + "{"
    out = []
    i = 0
    while True:
        j = text.find(tag, i)
        if j == -1:
            out.append(text[i:])
            break
        out.append(text[i:j])
        depth = 1
        k = j + len(tag)
        while k < len(text) and depth > 0:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        inner = text[j + len(tag):k - 1]
        out.append(replacement_fmt.format(inner))
        i = k
    return "".join(out)


def convert_algorithm(text):
    """Converts \\begin{algorithmic} to nested LaTeX itemize lists (not
    Markdown ** / - syntax -- this whole document is parsed with pandoc's
    LaTeX reader, which does not interpret Markdown emphasis/list markers
    and would render them as literal asterisks and hyphens)."""
    def repl(m):
        body = m.group(1)
        body = strip_braced_macro(body, "COMMENT", " ({})")
        lines = ["\\begin{itemize}"]
        depth = 1
        for raw in body.split("\n"):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("\\REQUIRE"):
                lines.append(r"\item \textbf{Require:} " + line[len("\\REQUIRE"):].strip())
            elif line.startswith("\\STATE"):
                lines.append(r"\item " + line[len("\\STATE"):].strip())
            elif line.startswith("\\FOR"):
                cond = re.search(r"\\FOR\{(.*)\}", line)
                lines.append(r"\item \textbf{for} " + (cond.group(1) if cond else "") + ":")
                lines.append("\\begin{itemize}")
                depth += 1
            elif line.startswith("\\ENDFOR"):
                if depth > 1:
                    lines.append("\\end{itemize}")
                    depth -= 1
            elif line.startswith("\\IF"):
                cond = re.search(r"\\IF\{(.*)\}", line)
                lines.append(r"\item \textbf{if} " + (cond.group(1) if cond else "") + ":")
                lines.append("\\begin{itemize}")
                depth += 1
            elif line.startswith("\\ENDIF"):
                if depth > 1:
                    lines.append("\\end{itemize}")
                    depth -= 1
            elif line.startswith("\\COMMENT"):
                continue
            else:
                lines.append(r"\item " + line)
        while depth > 0:
            lines.append("\\end{itemize}")
            depth -= 1
        return "\n" + "\n".join(lines) + "\n"

    text = re.sub(
        r"\\begin\{algorithmic\}\[?\d?\]?\n(.*?)\\end\{algorithmic\}",
        repl, text, flags=re.DOTALL,
    )
    # Pull the algorithm caption out as a bold line, drop the float wrapper.
    def alg_wrap(m):
        inner = m.group(1)
        cap = re.search(r"\\caption\{(.*?)\}", inner)
        cap_text = cap.group(1) if cap else "Algorithm"
        inner = re.sub(r"\\caption\{.*?\}\n?", "", inner)
        inner = re.sub(r"\\label\{alg:[^}]*\}\n?", "", inner)
        return f"\n\\textbf{{Algorithm 1: {cap_text}}}\n{inner}\n"

    text = re.sub(r"\\begin\{algorithm\}\[?[a-z]*\]?\n(.*?)\\end\{algorithm\}",
                   alg_wrap, text, flags=re.DOTALL)
    return text


def resolve_cref(text):
    def repl(m):
        label = m.group(1)
        if label in FIG_NUM:
            return f"Fig. {FIG_NUM[label]}"
        if label in TAB_NUM:
            return f"Table {to_roman(TAB_NUM[label])}" if False else f"Table {TAB_NUM[label]}"
        if label in EQ_NUM:
            return f"Eq. ({EQ_NUM[label]})"
        return f"[UNRESOLVED:{label}]"
    return re.sub(r"\\Cref\{([^}]*)\}", repl, text)


def resolve_cite(text, cite_num):
    def repl(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        nums = [str(cite_num[k]) for k in keys if k in cite_num]
        return "[" + "], [".join(nums) + "]"
    return re.sub(r"\\cite\{([^}]*)\}", repl, text)


def inject_caption_numbers(text):
    # \caption{...} immediately preceded (within the same float) by a table
    # or figure -- distinguish by scanning backward isn't needed since we
    # process table/figure blocks separately with their own regex.
    def tab_repl(m):
        block = m.group(0)
        lbl = re.search(r"\\label\{(tab:[^}]*)\}", block)
        if not lbl or lbl.group(1) not in TAB_NUM:
            return block
        n = TAB_NUM[lbl.group(1)]
        return re.sub(r"\\caption\{(.*?)\}", lambda cm: f"\\caption{{Table {n}: {cm.group(1)}}}", block, count=1)

    def fig_repl(m):
        block = m.group(0)
        lbl = re.search(r"\\label\{(fig:[^}]*)\}", block)
        if not lbl or lbl.group(1) not in FIG_NUM:
            return block
        n = FIG_NUM[lbl.group(1)]
        return re.sub(r"\\caption\{(.*?)\}", lambda cm: f"\\caption{{Fig. {n}: {cm.group(1)}}}", block, count=1)

    text = re.sub(r"\\begin\{table\}.*?\\end\{table\}", tab_repl, text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", fig_repl, text, flags=re.DOTALL)
    return text


def main():
    cite_order = build_citation_order()
    cite_num = {key: i + 1 for i, key in enumerate(cite_order)}
    bib_entries = parse_bib(os.path.join(SRC_DIR, "references.bib"))

    body_parts = []
    for name in SECTION_ORDER:
        path = os.path.join(SRC_DIR, "sections", f"{name}.tex")
        text = open(path).read()
        body_parts.append(text)
    body = "\n\n".join(body_parts)

    # Order matters: caption numbers before Cref resolution (both read
    # \label, neither depends on the other's output) but resizebox/subeq
    # stripping before caption injection is safe since captions live outside
    # the resizebox wrapper.
    body = strip_resizebox(body)
    body = strip_subequations(body)
    body = convert_algorithm(body)
    body = inject_caption_numbers(body)
    body = resolve_cref(body)
    body = resolve_cite(body, cite_num)

    # \IEEEkeywords isn't meaningful outside IEEEtran -- render as a plain
    # paragraph so pandoc doesn't choke on the unknown environment.
    body = body.replace("\\begin{IEEEkeywords}", "\n\\textbf{Index Terms---}")
    body = body.replace("\\end{IEEEkeywords}", "\n")
    body = body.replace("\\begin{abstract}", "\\textbf{Abstract---}")
    body = body.replace("\\end{abstract}", "")

    # Bibliography, plain numbered list in citation order.
    bib_lines = ["\\section*{References}"]
    for key in cite_order:
        n = cite_num[key]
        fields = bib_entries.get(key, {})
        bib_lines.append(f"\n[{n}] {format_ref(key, fields)}")
    bib_text = "\n".join(bib_lines)

    full = (
        "\\title{MA-ROPE: Multi-RAT Privacy-Preserving Federated Deep "
        "Reinforcement Learning for V2X Task Offloading}\n"
        "\\author{Anonymous Authors}\n"
        "\\date{}\n\n"
        + body + "\n\n" + bib_text + "\n"
    )

    with open(OUT_PATH, "w") as f:
        f.write(full)
    print(f"Wrote {OUT_PATH} ({len(full)} chars)")
    print(f"Citations resolved: {len(cite_order)}")
    unresolved = re.findall(r"\[UNRESOLVED:[^\]]*\]", full)
    if unresolved:
        print(f"WARNING: {len(unresolved)} unresolved \\Cref labels: {set(unresolved)}")
    else:
        print("All \\Cref labels resolved.")


if __name__ == "__main__":
    main()
