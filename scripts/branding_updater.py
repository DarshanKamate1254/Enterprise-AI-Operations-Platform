import os
import re

replacements = [
    (re.compile(r'AI_OOPS Pvt\. Ltd\.', re.IGNORECASE), 'BIA Pvt. Ltd.'),
    (re.compile(r'AI_OOPS Solutions Pvt\. Ltd\.', re.IGNORECASE), 'BIA Solutions Pvt. Ltd.'),
    (re.compile(r'aioops-solutions\.com', re.IGNORECASE), 'bia-solutions.com'),
    (re.compile(r'ai-oops\.com', re.IGNORECASE), 'bia.com'),
    (re.compile(r'ai_oops', re.IGNORECASE), 'bia'),
    (re.compile(r"AI_OOPS's", re.IGNORECASE), "BIA's"),
    (re.compile(r'AI_OOPS', re.IGNORECASE), 'BIA'),

    (re.compile(r'NovaTech Solutions Pvt\. Ltd\.', re.IGNORECASE), 'BIA Pvt. Ltd.'),
    (re.compile(r'NovaTech Solutions', re.IGNORECASE), 'BIA'),
    (re.compile(r'NovaTech Ops', re.IGNORECASE), 'BIA'),
    (re.compile(r'NovaTech', re.IGNORECASE), 'BIA'),
    (re.compile(r'novatech-solutions\.com', re.IGNORECASE), 'bia-solutions.com'),
    (re.compile(r'novatech\.com', re.IGNORECASE), 'bia.com'),
    (re.compile(r'Novatech', re.IGNORECASE), 'BIA'),
]

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

exclude_dirs = {'.git', 'node_modules', 'dist', '.venv', 'site-packages', 'venv', '__pycache__', '.pytest_cache'}
exclude_files = {'branding_updater.py'}
extensions = {'.py', '.md', '.html', '.css', '.json', '.ts', '.tsx', '.sql', '.txt', '.csv'}

print("Starting branding refactoring...")
updated_count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Prune excluded directories
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    
    for filename in filenames:
        if filename in exclude_files:
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in extensions:
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content
                for pattern, repl in replacements:
                    new_content = pattern.sub(repl, new_content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {os.path.relpath(filepath, root_dir)}")
                    updated_count += 1
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print(f"Refactoring complete! Updated branding in {updated_count} files.")
