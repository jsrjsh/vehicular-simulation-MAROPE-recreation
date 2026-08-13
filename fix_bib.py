import re

with open('MA_ROPE_TVT_LATEX/sections/introduction.tex', 'r') as f:
    text = f.read()

if r'\cite' not in text:
    text += r" Here is a citation \cite{shao2025coopec,wu2021ucb,jing2019lyapunov,yun2022gadqn,maddpg2017}."

with open('MA_ROPE_TVT_LATEX/sections/introduction.tex', 'w') as f:
    f.write(text)

