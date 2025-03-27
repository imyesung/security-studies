#!/usr/bin/env python3

from pathlib import Path
import os
import re
from datetime import datetime

# 설정
EXCLUDE_DIRS = {"drafts", "fleeting-note", ".github"}
EXCLUDE_FILES = {"README.md", "z-note-template.md"}
README_PATH = "README.md"
MAX_RECENT = 5

def is_valid_note(file: Path) -> bool:
    return (
        file.suffix == ".md"
        and file.name not in EXCLUDE_FILES
        and not any(part in EXCLUDE_DIRS for part in file.parts)
    )

def get_recent_changes(files: list[Path]) -> str:
    entries = [(file, file.stat().st_mtime) for file in files]
    entries.sort(key=lambda x: x[1], reverse=True)

    result = "### 최근 업데이트 파일\n\n"
    for file, mtime in entries[:MAX_RECENT]:
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        result += f"- [{file.name}]({file}) - {mod_time}\n"
    return result

def get_research_areas(files: list[Path]) -> str:
    areas = {}
    for file in files:
        area = file.parts[0] if len(file.parts) > 1 else "기타"
        areas.setdefault(area, []).append(file)

    result = "### 연구 영역\n\n"
    for area in sorted(areas):
        result += f"#### {area}\n\n"
        for file in sorted(areas[area]):
            result += f"- [{file.name}]({file})\n"
        result += "\n"
    return result

def update_readme():
    all_files = list(Path(".").rglob("*.md"))
    valid_files = [f for f in all_files if is_valid_note(f)]

    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()

    # 최근 변경사항 업데이트
    recent_section = get_recent_changes(valid_files)
    content = re.sub(
        r"<!-- RECENT_CHANGES -->.*?<!-- RECENT_CHANGES_END -->",
        f"<!-- RECENT_CHANGES -->\n{recent_section}\n<!-- RECENT_CHANGES_END -->",
        content,
        flags=re.DOTALL,
    )

    # 연구 영역 TOC 업데이트
    toc_section = get_research_areas(valid_files)
    content = re.sub(
        r"<!-- RESEARCH_AREAS -->.*?<!-- RESEARCH_AREAS_END -->",
        f"<!-- RESEARCH_AREAS -->\n{toc_section}\n<!-- RESEARCH_AREAS_END -->",
        content,
        flags=re.DOTALL,
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md has been updated.")

if __name__ == "__main__":
    update_readme()
