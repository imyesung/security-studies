#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path

EXCLUDE_DIRS = {"drafts", "fleeting-note"}
EXCLUDE_FILES = {"README.md", "z-note-template.md"}

def get_file_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
    except Exception:
        pass
    return None

def is_valid_note(file: Path):
    if file.name in EXCLUDE_FILES:
        return False
    if not file.suffix == ".md":
        return False
    if any(part.startswith('.') for part in file.parts):
        return False
    if any(part in EXCLUDE_DIRS for part in file.parts):
        return False
    return True

def get_recent_changes(max_items=5):
    files = []
    for file in Path('.').glob('**/*.md'):
        if not is_valid_note(file):
            continue
        files.append({
            'path': str(file),
            'mtime': file.stat().st_mtime,
            'title': get_file_title(file)
        })
    files.sort(key=lambda x: x['mtime'], reverse=True)
    result = "### 최근 업데이트 파일\n\n"
    for file in files[:max_items]:
        date = datetime.fromtimestamp(file['mtime']).strftime('%Y-%m-%d')
        label = file['title'] or file['path']
        result += f"- [{label}]({file['path']}) - {date}\n"
    return result

def get_research_areas():
    areas = {}
    for file in Path('.').glob('**/*.md'):
        if not is_valid_note(file):
            continue
        area = file.parts[0] if len(file.parts) > 1 else "기타"
        if area not in areas:
            areas[area] = []
        areas[area].append({
            'path': str(file),
            'title': get_file_title(file)
        })
    result = "### 연구 영역\n\n"
    for area, files in sorted(areas.items()):
        result += f"#### {area.capitalize()}\n\n"
        for file in files:
            label = file['title'] or file['path']
            result += f"- [{label}]({file['path']})\n"
        result += "\n"
    return result

def update_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(
            r'<!-- RECENT_CHANGES -->.*?<!-- RECENT_CHANGES_END -->',
            f'<!-- RECENT_CHANGES -->\n{get_recent_changes()}\n<!-- RECENT_CHANGES_END -->',
            content, flags=re.DOTALL
        )

        content = re.sub(
            r'<!-- RESEARCH_AREAS -->.*?<!-- RESEARCH_AREAS_END -->',
            f'<!-- RESEARCH_AREAS -->\n{get_research_areas()}\n<!-- RESEARCH_AREAS_END -->',
            content, flags=re.DOTALL
        )

        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ README.md 자동 업데이트 완료")

    except Exception as e:
        print(f"🚨 README 업데이트 오류: {e}")

if __name__ == "__main__":
    update_readme()
