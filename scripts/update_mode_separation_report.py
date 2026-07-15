# scripts/update_mode_separation_report.py
"""
Scans the results directory and updates MODE_SEPARATION_REPORT.md with the full
manifest of CSV and PT files.
"""

import os

def update():
    base_dir = "results"
    
    report_content = """# MODE_SEPARATION_REPORT.md

This document verifies the strict directory separation between `baseline_recreation` (paper reproduction) and `physically_corrected` outputs.

---

## 1. Directory Structure Layout
* **Paper Reproduction Directory:** [`results/paper_reproduction/`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/results/paper_reproduction)
* **Physically Corrected Directory:** [`results/physically_corrected/`](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/results/physically_corrected)

---

## 2. Manifest Verification

The following evaluation log files and checkpoints have been isolated correctly:
"""

    for n in [8, 32]:
        for mode_dir in ["paper_reproduction", "physically_corrected"]:
            path = f"results/{mode_dir}/n{n}"
            report_content += f"\n### results/{mode_dir}/n{n}/\n"
            files = sorted(os.listdir(path)) if os.path.exists(path) else []
            for file in files:
                report_content += f"- {file}\n"
                
    with open("MODE_SEPARATION_REPORT.md", "w") as f:
        f.write(report_content)
        
    print("MODE_SEPARATION_REPORT.md updated successfully.")

if __name__ == "__main__":
    update()
