import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

def get_last_commit_date(file_path_str):
    """주어진 파일 경로 문자열에 대한 마지막 Git 커밋 날짜를 YYYY-MM-DD 형식으로 반환합니다."""
    try:
        # git log 명령어 실행 (파일 경로는 문자열이어야 함)
        cmd = ['git', 'log', '-1', '--format=%cs', '--', file_path_str]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        commit_date = result.stdout.strip()
        # 유효한 날짜 형식인지 간단히 확인 (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', commit_date):
            return commit_date
        else:
            # 예상치 못한 출력이면 경고 후 오늘 날짜 반환
            print(f"Warning: Unexpected git log output for {file_path_str}: '{commit_date}'. Using today's date.")
            return datetime.now().strftime('%Y-%m-%d')

    except subprocess.CalledProcessError:
        # 파일이 Git 추적 중이 아니거나, 커밋이 없는 경우 등
        # print(f"Warning: Could not get git log for {file_path_str}. Using file system mtime as fallback.")
        # Git 기록이 없는 경우, 파일 시스템 수정 시간을 대신 사용하거나 오늘 날짜 사용
        try:
            mtime = Path(file_path_str).stat().st_mtime
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except FileNotFoundError:
            return datetime.now().strftime('%Y-%m-%d') # 파일이 없으면 오늘 날짜
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed and in PATH?")
        # Git 명령어를 찾을 수 없는 경우 오늘 날짜 반환
        return datetime.now().strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error getting commit date for {file_path_str}: {e}")
        # 기타 예외 발생 시 오늘 날짜 반환
        return datetime.now().strftime('%Y-%m-%d')


def get_files_with_commit_dates():
    """
    저장소 내 필터링된 마크다운 파일과 각 파일의 마지막 Git 커밋 날짜 목록을 반환합니다.
    결과는 [(Path 객체, 'YYYY-MM-DD'), ...] 형태의 리스트입니다.
    """
    files_with_dates = []
    for file_path_obj in Path('.').glob('**/*.md'):
        # --- 기존 필터링 로직 ---
        if 'README.md' in str(file_path_obj) or 'z-note-template.md' in str(file_path_obj):
            continue
        if any(part.startswith('.') for part in file_path_obj.parts):
            continue
        # drafts 또는 fleeting-note 디렉토리에 있는 파일 제외 (소문자 비교)
        if any(part.lower() in {'drafts', 'fleeting-note'} for part in file_path_obj.parts):
             continue
        # --- 필터링 끝 ---

        # 파일 경로를 문자열로 변환하여 마지막 커밋 날짜 가져오기
        commit_date = get_last_commit_date(str(file_path_obj))
        files_with_dates.append((file_path_obj, commit_date))

    # 커밋 날짜를 기준으로 내림차순 정렬 (최신 날짜가 위로)
    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    return files_with_dates

def get_recent_changes(files_data, max_items=5):
    """주어진 파일 데이터 리스트에서 최근 변경된 항목 문자열 생성"""
    result = ""
    # 이미 날짜순으로 정렬되어 있으므로 상위 N개만 사용
    for file_path_obj, commit_date in files_data[:max_items]:
        # 링크 생성 시 Path 객체를 문자열로 변환하고, URL 인코딩이 필요할 수 있으나
        # 보통 마크다운에서는 상대 경로로 잘 동작함. 필요시 urllib.parse.quote 사용.
        link_path = str(file_path_obj).replace("\\", "/") # Windows 경로 구분자 변경
        result += f"- [{file_path_obj.stem}]({link_path}) - {commit_date}\n" # .name 대신 .stem 사용 (확장자 제외)
    return result

def get_full_note_list(files_data):
    """주어진 파일 데이터 리스트에서 전체 노트 목록 테이블 문자열 생성"""
    result = ""
    result += "| 파일명 | 최종 수정일 |\n"
    result += "|--------|-------------|\n"
    # 전체 목록 순회
    for file_path_obj, commit_date in files_data:
        link_path = str(file_path_obj).replace("\\", "/") # Windows 경로 구분자 변경
        result += f"| [{file_path_obj.stem}]({link_path}) | {commit_date} |\n" # .name 대신 .stem 사용 (확장자 제외)
    return result

def update_readme():
    """README.md 파일을 읽고, 최신 변경사항과 전체 노트 목록을 업데이트합니다."""
    try:
        readme_path = "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 파일 목록과 커밋 날짜 가져오기 (한 번만 호출)
        files_data = get_files_with_commit_dates()

        # 최근 수정된 파일 목록 변경
        recent_section = get_recent_changes(files_data) # max_items 기본값 사용
        content = re.sub(
            r"(\s*).*(?=\s*)", # 시작 태그 바로 다음부터 끝 태그 직전까지 매칭
            r"\1" + recent_section.strip(), # 시작 태그 + 새로운 내용 (앞뒤 공백 제거)
            content,
            flags=re.DOTALL | re.IGNORECASE, # DOTALL: 개행문자 포함, IGNORECASE: 대소문자 무시
        )

        # 전체 노트 TOC 업데이트
        toc_section = get_full_note_list(files_data)
        content = re.sub(
            r"(\s*).*(?=\s*)", # 시작 태그 바로 다음부터 끝 태그 직전까지 매칭
            r"\1" + toc_section.strip(), # 시작 태그 + 새로운 내용 (앞뒤 공백 제거)
            content,
            flags=re.DOTALL | re.IGNORECASE, # DOTALL: 개행문자 포함, IGNORECASE: 대소문자 무시
        )

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("README.md 업데이트 완료")

    except Exception as e:
        print(f"README 업데이트 오류: {e}")
        # 오류 발생 시 스크립트 실패 처리 (GitHub Actions에서 인지하도록)
        exit(1)

if __name__ == "__main__":
    update_readme()
