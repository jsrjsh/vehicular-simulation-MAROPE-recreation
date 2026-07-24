import os
import re
import sys

def check_anonymity(directory):
    print(f"[*] Scanning {directory} for anonymity leaks...")
    
    # Simple regexes to catch obvious personal markers
    # In a real tool this would be more robust.
    forbidden_patterns = [
        r"aryaveersingh",
        r"@gmail\.com",
        r"university",
        r"/Users/",
        r"C:\\Users\\"
    ]
    
    issues_found = 0
    for root, _, files in os.walk(directory):
        if ".git" in root or "archive" in root or "venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            # Check text files only
            if file.endswith((".py", ".md", ".yaml", ".yml", ".json", ".txt", ".sh", ".cff")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            for pattern in forbidden_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    # Ignore the check script itself and the audit log which mentions the path
                                    if "check_anonymity.py" in filepath or "REPOSITORY_AUDIT.md" in filepath or "implementation_plan.md" in filepath:
                                        continue
                                    print(f"[!] Leak found in {filepath}:{i+1} -> matched '{pattern}'")
                                    issues_found += 1
                except Exception as e:
                    pass
                    
    if issues_found > 0:
        print(f"[-] FAILED: Found {issues_found} potential anonymity leaks.")
        sys.exit(1)
    else:
        print("[+] SUCCESS: No obvious anonymity leaks found.")
        sys.exit(0)

if __name__ == "__main__":
    check_anonymity(".")
