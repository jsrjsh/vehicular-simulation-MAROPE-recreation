# Task for AG (Antigravity)
Workspace: see MANIFEST.json "workspace". Build: pdflatex main.tex; bibtex main; pdflatex x2 (no latexmk; algpseudocode.sty not installed, keep `algorithmic`).
Constraints: <=15 pages, 0 LaTeX errors, 0 Overfull \hbox. Layout/bib/build ONLY. Do not edit numbers, table values, equation meaning, claims or disclaimers. Don't touch unrelated uncommitted deletions in the parent repo.

1. `haq2026` undefined (introduction.tex l.15, related_work.tex l.37). No bib entry exists. Find the real paper (earlier drafts, bib files, web); add ONLY if authors/title/venue/year/DOI verified. Otherwise do not invent: report back and propose removing \cite{haq2026} (keep wu2021).
2. Placeholder DOIs "xxxxx" in references.bib (~lines 10, 41, 52, 71, 174, 186, incl. xiong2021). Look up the real DOI and metadata; if an entry can't be verified as a real paper, list it for the user and leave it unchanged. Don't delete cited entries.
3. Visual pass over all 15 pages (pdftoppm): tables spilling or tiny after \resizebox, captions split from floats, widows/orphans, big gaps, ugly justification (e.g. "Architecture:" paragraph in algorithm_design.tex), unreadable figure labels. Also add a one-line definition for c_ref and n_ref (renamed from completed_on_time_ref/total_tasks_ref) next to the DRR algorithm in methodology.tex.
4. Confirm 0 "[?]" in `pdftotext main.pdf -`. Write outbox/AG_CHANGELOG.md listing every edit, final page count, and anything unverified. Record vendor/name, evidence, uncertainty.
