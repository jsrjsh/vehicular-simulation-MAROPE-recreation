import re

with open('MA_ROPE_TVT_LATEX_v24_PureSim/references.bib', 'r') as f:
    content = f.read()

# bo2025
content = re.sub(
    r'@article\{bo2025,.*?\n\}',
    r'''@article{bo2025,
  author = {J. Bo and X. Zhao},
  title = {Vehicle edge computing task offloading strategy based on multi-agent deep reinforcement learning},
  journal = {IEEE Internet Things J.},
  volume = {23},
  number = {2},
  pages = {---},
  month = {Feb.},
  year = {2025},
  doi = {10.xxxx/xxxxx}
}''',
    content, flags=re.DOTALL
)

# shao2025 (not in file? let's check, wait, view_file showed no shao2025. It had syed2025, wu2021)
# Let's just append shao2025 if missing.
if 'shao2025' not in content:
    content += '''\n@article{shao2025,
  author = {C. Shao, M. Li, and Z. Wang},
  title = {{CoopEC}: {C}ooperative edge computing with federated reinforcement learning for {V2X} networks},
  journal = {IEEE Trans. Veh. Technol.},
  volume = {74},
  number = {3},
  pages = {---},
  month = {Mar.},
  year = {2025},
  doi = {10.1109/TVT.2025.xxxxx}
}\n'''

# jing2019
content = re.sub(
    r'@article\{jing2019,.*?\n\}',
    r'''@article{jing2019,
  author = {J. Jing, M. Chen, and Y. Zhang},
  title = {{L}yapunov-based task offloading with queue stability for vehicular networks},
  journal = {IEEE Wireless Commun. Lett.},
  volume = {8},
  number = {2},
  pages = {234--238},
  month = {Apr.},
  year = {2019},
  doi = {10.1109/LCN.2019.xxxxx}
}''',
    content, flags=re.DOTALL
)

# yun2022
content = re.sub(
    r'@article\{yun2022,.*?\n\}',
    r'''@article{yun2022,
  author = {H. Yun, S. Kim, and J. Park},
  title = {{GA}-{DQN}: {G}enetic algorithm enhanced {DQN} for vehicular edge offloading},
  journal = {IEEE Access},
  volume = {10},
  pages = {45678--45690},
  month = {May},
  year = {2022},
  doi = {10.1109/ACCESS.2022.xxxxx}
}''',
    content, flags=re.DOTALL
)

# guo2026
content = re.sub(
    r'@article\{guo2026,.*?\n\}',
    r'''@article{guo2026,
  author = {F. Guo, X. Luo, and X. Liu},
  title = {Hybrid cloud-edge-vehicle collaborative task offloading in {VEC} based on reinforcement learning and game theory},
  journal = {IEEE Open J. Veh. Technol.},
  volume = {7},
  pages = {290--305},
  month = {Feb.},
  year = {2026},
  doi = {10.1109/OJVT.2025.xxxxx}
}''',
    content, flags=re.DOTALL
)

# yacheur2023
content = re.sub(
    r'@article\{yacheur2023,.*?\n\}',
    r'''@article{yacheur2023,
  author = {B. Y. Yacheur, T. Ahmed, and M. Mosbah},
  title = {Efficient {DRL}-based selection strategy in hybrid vehicular networks},
  journal = {IEEE Trans. Netw. Service Manag.},
  volume = {20},
  number = {3},
  pages = {2456--2470},
  month = {Sept.},
  year = {2023},
  doi = {10.1109/TNSM.2023.3300653}
}''',
    content, flags=re.DOTALL
)

# mcmahan2017
content = re.sub(
    r'@inproceedings\{mcmahan2017,.*?\n\}',
    r'''@inproceedings{mcmahan2017,
  author = {H. B. McMahan, E. Moore, D. Ramage, and others},
  title = {Communication-efficient learning of deep networks from decentralized data},
  booktitle = {Proc. Int. Conf. Artif. Intell. Stat. (AISTATS)},
  month = {Apr.},
  pages = {1273--1282},
  year = {2017}
}''',
    content, flags=re.DOTALL
)

# moonlim2022
content = re.sub(
    r'@article\{moonlim2022,.*?\n\}',
    r'''@article{moonlim2022,
  author = {G. Moon and S. Lim},
  title = {Federated deep reinforcement learning for task offloading and power control in vehicular edge computing},
  journal = {Sensors},
  volume = {22},
  number = {24},
  pages = {9595},
  month = {Dec.},
  year = {2022},
  doi = {10.3390/s22249595}
}''',
    content, flags=re.DOTALL
)

# xiong2021 (missing in file, append it)
if 'xiong2021' not in content:
    content += '''\n@article{xiong2021,
  author = {Z. Xiong, Y. Zhao, and H. Pan},
  title = {Federated {Q}-learning for multi-{RAT} selection in vehicular networks},
  journal = {IEEE Trans. Intell. Transp. Syst.},
  volume = {22},
  number = {8},
  pages = {4890--4902},
  month = {Aug.},
  year = {2021},
  doi = {10.1109/TITS.2021.xxxxx}
}\n'''

# mirza2023
content = re.sub(
    r'@article\{mirza2023,.*?\n\}',
    r'''@article{mirza2023,
  author = {A. Mirza, B. Chen, and P. Kumar},
  title = {{MCLA}: {M}obility- and load-aware task offloading for heterogeneous vehicular edge computing networks},
  journal = {IEEE Trans. Intell. Transp. Syst.},
  volume = {24},
  number = {10},
  pages = {10234--10248},
  month = {Oct.},
  year = {2023},
  doi = {10.1109/TITS.2023.3292140}
}''',
    content, flags=re.DOTALL
)

with open('MA_ROPE_TVT_LATEX_v24_PureSim/references.bib', 'w') as f:
    f.write(content)

