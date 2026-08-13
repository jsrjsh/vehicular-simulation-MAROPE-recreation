import os
import re

replacements = {
    'related_work.tex': [('example-image-a', 'figures/image1.png'), ('example-image-b', 'figures/image2.png')],
    'system_model.tex': [('example-image-a', 'figures/image3.png')],
    'algorithm_design.tex': [('example-image-a', 'figures/image4.png')],
    'results_part1.tex': [
        ('example-image-a', 'figures/image5.png', 1), # first instance
        ('example-image-b', 'figures/image6.png', 1),
        ('example-image-c', 'figures/image7.png', 1),
        ('example-image-a', 'figures/image8.png', 1), # second instance
        ('example-image-b', 'figures/image9.png', 1),
        ('example-image-c', 'figures/image10.png', 1),
        ('example-image-a', 'figures/image11.png', 1),
        ('example-image-b', 'figures/image12.png', 1),
    ],
    'results_part2.tex': [
        ('example-image-a', 'figures/image13.png', 1),
        ('example-image-b', 'figures/image14.png', 1),
        ('example-image-c', 'figures/image15.png', 1),
        ('example-image-a', 'figures/image16.png', 1),
    ]
}

base_dir = 'MA_ROPE/MASTER/MA_ROPE_MASTER_v21/sections/'

# For related_work, system_model, algorithm_design, simple replace is enough
for file, reps in replacements.items():
    if file not in ['results_part1.tex', 'results_part2.tex']:
        with open(os.path.join(base_dir, file), 'r') as f:
            text = f.read()
        for old, new in reps:
            text = text.replace(old, new)
        with open(os.path.join(base_dir, file), 'w') as f:
            f.write(text)

# For results_part1 and part2, we need sequential replacement
for file in ['results_part1.tex', 'results_part2.tex']:
    with open(os.path.join(base_dir, file), 'r') as f:
        text = f.read()
    for old, new, _ in replacements[file]:
        text = text.replace(old, new, 1)
    with open(os.path.join(base_dir, file), 'w') as f:
        f.write(text)

print("Figures replaced successfully.")
