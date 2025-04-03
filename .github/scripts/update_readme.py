#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

# --- Configuration ---
README_PATH = Path("README.md")
RECENT_NOTES_TAG_START = "<!-- RECENT_NOTES_START -->"  # 수정!
RECENT_NOTES_TAG_END = "<!-- RECENT_NOTES_END -->"      # 수정!
TOC_TAG_START = "<!-- TOC_START -->"                    # 수정!
TOC_TAG_END = "<!-- TOC_END -->"                        # 수정!

EXCLUDE_FILES = {'README.md', 'z-note-template.md'}
EXCLUDE_DIRS_LOWER = {'drafts', 'fleeting-note', '.git', '.github', '.venv', '.vscode', 'images'}
MAX_RECENT_NOTES = 5
# --- End Configuration ---

def get_last_commit_date(file_path_str: str) -> str:
    """Gets the last commit date (YYYY-MM-DD) for a file using git log."""
    try:
        cmd = ['git', 'log', '-1', '--format=%cs', '--', file_path_str]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        commit_date = result.stdout.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', commit_date):
            return commit_date
        else:
            print(f"Warning: Unexpected git log format for {file_path_str}: '{commit_date}'.", file=sys.stderr)
            return "N/A"
    except subprocess.CalledProcessError as e:
        # Usually means file is not tracked or has no commits yet
        # print(f"Debug: git log failed for {file_path_str}: {e}", file=sys.stderr)
        return "N/A"
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed?", file=sys.stderr)
        return "Error"
    except Exception as e:
        print(f"Error getting commit date for {file_path_str}: {e}", file=sys.stderr)
        return "Error"

def get_markdown_files_data() -> list[tuple[Path, str]]:
    """Finds markdown files, gets their last commit dates, and sorts them."""
    files_data = []
    repo_root = Path('.')
    for file_path in repo_root.glob('**/*.md'):
        # Check exclusion lists
        if file_path.name in EXCLUDE_FILES:
            continue
        if any(part.startswith('.') for part in file_path.parts):
            continue
        is_in_excluded_dir = False
        # Check parent directories (case-insensitive)
        for parent in file_path.parents:
            if parent.name.lower() in EXCLUDE_DIRS_LOWER:
                is_in_excluded_dir = True
                break
        if is_in_excluded_dir:
            continue

        # Get commit date
        commit_date = get_last_commit_date(str(file_path))
        files_data.append((file_path, commit_date))

    # Sort by date (descending), handle N/A or Error dates by putting them last
    def sort_key(item):
        date_str = item[1]
        if date_str in ["N/A", "Error"]:
            return "0000-00-00" # Sort errors/N/A to the end
        return date_str

    files_data.sort(key=sort_key, reverse=True)
    print(f"Found and processed {len(files_data)} markdown files.")
    return files_data

def generate_recent_notes_md(files_data: list[tuple[Path, str]]) -> str:
    """Generates markdown list for recent notes."""
    lines = []
    for file_path, commit_date in files_data[:MAX_RECENT_NOTES]:
        link_path = urllib.parse.quote(str(file_path).replace("\\", "/"))
        link_text = file_path.stem # Filename without extension
        lines.append(f"- [{link_text}]({link_path}) - {commit_date}")
    return "\n".join(lines)

def generate_toc_md(files_data: list[tuple[Path, str]]) -> str:
    """Generates markdown table for TOC."""
    lines = []
    lines.append("| 파일명 | 최종 수정일 |") # Korean header
    lines.append("|--------|-------------|")
    for file_path, commit_date in files_data:
        link_path = urllib.parse.quote(str(file_path).replace("\\", "/"))
        link_text = file_path.stem
        lines.append(f"| [{link_text}]({link_path}) | {commit_date} |")
    return "\n".join(lines)

def replace_content_between_tags(content: str, start_tag: str, end_tag: str, new_inner_content: str) -> tuple[str, bool]:
    """Replaces content between start and end tags. Returns (new_content, changed_flag)."""
    start_index = content.find(start_tag)
    if start_index == -1:
        print(f"Error: Start tag '{start_tag}' not found.", file=sys.stderr)
        return content, False

    end_index = content.find(end_tag, start_index + len(start_tag))
    if end_index == -1:
        print(f"Error: End tag '{end_tag}' not found after start tag.", file=sys.stderr)
        return content, False

    # Construct the new content
    new_content = (
        content[:start_index + len(start_tag)] + # Keep start tag
        "\n" + new_inner_content + "\n" +         # Add newline, new content, newline
        content[end_index:]                       # Keep end tag and rest of file
    )
    
    # Check if content actually changed (ignoring potential whitespace differences initially added)
    # A more robust check might compare the core inner content before/after
    original_inner_content_start = start_index + len(start_tag)
    original_inner_content_end = end_index
    original_inner_content = content[original_inner_content_start:original_inner_content_end].strip()
    
    changed = original_inner_content != new_inner_content.strip()
    
    return new_content, changed


def main():
    """Main function to update the README."""
    if not README_PATH.is_file():
        print(f"Error: {README_PATH} not found!", file=sys.stderr)
        sys.exit(1)

    print("Processing notes...")
    files_data = get_markdown_files_data()

    print("Generating new sections...")
    recent_notes_section = generate_recent_notes_md(files_data)
    toc_section = generate_toc_md(files_data)

    print(f"Reading {README_PATH}...")
    try:
        original_content = README_PATH.read_text(encoding='utf-8')
        content = original_content # Start with original content
    except Exception as e:
        print(f"Error reading {README_PATH}: {e}", file=sys.stderr)
        sys.exit(1)

    print("Updating Recent Notes section...")
    content, changed1 = replace_content_between_tags(content, RECENT_NOTES_TAG_START, RECENT_NOTES_TAG_END, recent_notes_section)

    print("Updating TOC section...")
    content, changed2 = replace_content_between_tags(content, TOC_TAG_START, TOC_TAG_END, toc_section)

    if changed1 or changed2:
        print(f"Changes detected. Writing updated content to {README_PATH}...")
        try:
            README_PATH.write_text(content, encoding='utf-8')
            print("README.md successfully updated.")
        except Exception as e:
            print(f"Error writing to {README_PATH}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No changes needed in README.md.")

if __name__ == "__main__":
    main()
