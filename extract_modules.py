#!/usr/bin/env python3
"""
Extract and modularize JavaScript from SmartCart index.html
"""

import re
from pathlib import Path

def extract_js_from_html(html_path):
    """Read and extract the JavaScript section from HTML"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the <script> section
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("No script section found!")
        return None
    
    return script_match.group(1)

def save_module(module_name, content):
    """Save a module to js/ directory"""
    output_path = Path('js') / f'{module_name}.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {output_path}")

# Read the HTML file
html_path = Path('index.html')
js_content = extract_js_from_html(html_path)

if not js_content:
    print("Failed to extract JavaScript")
    exit(1)

print(f"✓ Extracted {len(js_content)} characters of JavaScript")

# Now we have the JS content, we can start extracting modules
print("\nNOTE: This is a helper script. The actual modularization will be done manually")
print("      to ensure all dependencies are properly handled.")
