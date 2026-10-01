with open('sections/algorithm_design.tex', 'r') as f:
    alg = f.read()

img_block = """\\begin{figure}[htbp]
\\centering
\\includegraphics[width=0.45\\textwidth]{figures/image4.png}
\\caption{MA-ROPE MDP Formulation: 12-dimensional state space and 11-action implementation.}
\\label{fig:mdp_formulation}
\\end{figure}"""

alg = alg.replace(img_block + "\n\n", "")
alg = alg.replace(img_block + "\n", "")
alg = alg.replace(img_block, "")

with open('sections/algorithm_design.tex', 'w') as f:
    f.write(alg)

with open('sections/methodology.tex', 'r') as f:
    meth = f.read()

target = "\\subsection{State, Action, and Reward Formulation}\n"
meth = meth.replace(target, target + "\n" + img_block + "\n")

with open('sections/methodology.tex', 'w') as f:
    f.write(meth)
