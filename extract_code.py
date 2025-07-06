#!/usr/bin/env python3
"""
Utility script to extract code blocks from Notion AI Bot responses.
Usage: python extract_code.py <response_text_file>
"""

import sys
import re
import os

def extract_code_blocks(text):
    """Extract all code blocks from text"""
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    
    extracted_blocks = []
    for language, code in matches:
        lang = language or 'text'
        extracted_blocks.append({
            'language': lang,
            'code': code.strip(),
            'filename': f"extracted_code_{len(extracted_blocks) + 1}.{get_extension(lang)}"
        })
    
    return extracted_blocks

def extract_from_notion_format(text):
    """Extract code blocks from Notion's formatted output"""
    # Handle the format: // LANGUAGE CODE BLOCK N
    import re
    
    blocks = []
    lines = text.split('\n')
    current_block = []
    current_language = 'text'
    in_code_block = False
    
    for line in lines:
        if line.startswith('// ') and 'CODE BLOCK' in line:
            # Save previous block if exists
            if current_block:
                blocks.append({
                    'language': current_language,
                    'code': '\n'.join(current_block).strip(),
                    'filename': f"extracted_code_{len(blocks) + 1}.{get_extension(current_language)}"
                })
            
            # Start new block
            current_block = []
            in_code_block = True
            # Extract language from line like "// PYTHON CODE BLOCK 1"
            lang_match = re.search(r'// (\w+) CODE BLOCK', line)
            if lang_match:
                current_language = lang_match.group(1).lower()
        elif line.startswith('=' * 40) and in_code_block:
            # End of code block
            if current_block:
                blocks.append({
                    'language': current_language,
                    'code': '\n'.join(current_block).strip(),
                    'filename': f"extracted_code_{len(blocks) + 1}.{get_extension(current_language)}"
                })
            current_block = []
            in_code_block = False
        elif in_code_block and line.strip():
            current_block.append(line)
    
    # Handle last block
    if current_block:
        blocks.append({
            'language': current_language,
            'code': '\n'.join(current_block).strip(),
            'filename': f"extracted_code_{len(blocks) + 1}.{get_extension(current_language)}"
        })
    
    return blocks

def get_extension(language):
    """Get file extension based on language"""
    extensions = {
        'python': 'py',
        'javascript': 'js',
        'typescript': 'ts',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yml',
        'bash': 'sh',
        'shell': 'sh',
        'sql': 'sql',
        'php': 'php',
        'ruby': 'rb',
        'go': 'go',
        'rust': 'rs',
        'swift': 'swift',
        'kotlin': 'kt',
        'scala': 'scala'
    }
    return extensions.get(language.lower(), 'txt')

def save_code_blocks(blocks, output_dir="extracted_code"):
    """Save code blocks to files"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    for i, block in enumerate(blocks):
        filename = os.path.join(output_dir, block['filename'])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(block['code'])
        saved_files.append(filename)
        print(f"Saved: {filename} ({block['language']})")
    
    return saved_files

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_code.py <response_text_file>")
        print("Example: python extract_code.py response.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Try both extraction methods
        blocks = extract_code_blocks(text)
        if not blocks:
            blocks = extract_from_notion_format(text)
        
        if not blocks:
            print("No code blocks found in the text.")
            return
        
        print(f"Found {len(blocks)} code block(s):")
        for i, block in enumerate(blocks, 1):
            print(f"{i}. Language: {block['language']}")
            print(f"   Code preview: {block['code'][:100]}...")
            print()
        
        save_choice = input("Save code blocks to files? (y/n): ").lower().strip()
        if save_choice in ['y', 'yes']:
            saved_files = save_code_blocks(blocks)
            print(f"\nSaved {len(saved_files)} file(s) to 'extracted_code/' directory")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 