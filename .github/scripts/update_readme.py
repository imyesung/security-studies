import os
import re
from datetime import datetime
from pathlib import Path

def get_all_md_files():
    files = []
    for file in Path('.').glob('**/*.md'):
        if 'README.md' in str(file) or 'z-note-template.md' in str(file):
            continue
        if any(part.startswith('.') for part in file.parts):
            continue
        if any(part in {'drafts', 'fleeting-note'} for part in file.parts):
            continue
        files.append(file)
    return files

def get_recent_changes(files, max_items=5):
    entries = [(file, file.stat().st_mtime) for file in files]
    entries.sort(key=lambda x: x[1], reverse=True)

    result = ""
    for file, mtime in entries[:max_items]:
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        result += f"- [{file.name}]({file}) - {mod_time}\n"
    return result

def get_full_note_list(files):
    entries = [(file, file.stat().st_mtime) for file in files]
    entries.sort(key=lambda x: x[1], reverse=True)

    result = "" 
    result += "| 파일 | 수정일 |\n"
    result += "|------|--------|\n"
    for file, mtime in entries:
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        result += f"| [{file.name}]({file}) | {mod_time} |\n"
    return result

def update_readme():
    try:
        readme_path = "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        files = get_all_md_files()

        # 최근 수정된 파일 목록 변경
        recent_section = get_recent_changes(files)
        content = re.sub(
            r"<!-- RECENT_CHANGES -->.*?<!-- RECENT_CHANGES_END -->",
            f"<!-- RECENT_CHANGES -->\n{recent_section}\n<!-- RECENT_CHANGES_END -->",
            content,
            flags=re.DOTALL,
        )

        # 전체 노트 TOC 업데이트
        toc_section = get_full_note_list(files)
        content = re.sub(
            r"<!-- RESEARCH_AREAS -->.*?<!-- RESEARCH_AREAS_END -->",
            f"<!-- RESEARCH_AREAS -->\n{toc_section}\n<!-- RESEARCH_AREAS_END -->",
            content,
            flags=re.DOTALL,
        )

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("README.md 업데이트 완료")

    except Exception as e:
        print(f"README 업데이트 오류: {e}")

if __name__ == "__main__":
    update_readme()
