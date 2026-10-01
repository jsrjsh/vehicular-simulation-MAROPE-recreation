import os
import re

sections_dir = 'sections'
tables_dir = 'tables'
os.makedirs(tables_dir, exist_ok=True)

table_counter = 1

for filename in os.listdir(sections_dir):
    if not filename.endswith('.tex'):
        continue
    
    filepath = os.path.join(sections_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Regex to find \begin{table} ... \end{table}
    # non-greedy match to ensure we get individual tables
    # we need to handle both \begin{table} and \begin{table*}
    pattern = re.compile(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', re.DOTALL)
    
    def replacer(match):
        global table_counter
        table_content = match.group(0)
        
        # Try to find a label or caption to name the file
        label_match = re.search(r'\\label\{tab:(.*?)\}', table_content)
        if label_match:
            name = label_match.group(1).replace('-', '_')
        else:
            name = f"extracted_{table_counter}"
            
        table_filename = f"table_{table_counter:02d}_{name}.tex"
        table_filepath = os.path.join(tables_dir, table_filename)
        
        with open(table_filepath, 'w') as tf:
            tf.write(table_content + "\n")
            
        replacement = f"\\input{{{tables_dir}/{table_filename.replace('.tex', '')}}}"
        table_counter += 1
        return replacement

    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filename}")

print(f"Extracted {table_counter - 1} tables.")
