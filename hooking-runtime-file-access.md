## Context
- **Tactic:** Runtime Behavior Monitoring
- **Technique:** File I/O Interception via LD_PRELOAD
- **Procedure**:
	- Intercept file access at runtime by hooking `open()` and `read()` using `LD_PRELOAD`

## Core Idea
```markdown
[사용자 코드 영역]
    사용자 프로그램에서 open("/etc/passwd") 호출
              │
              ▼
────────────────────────────────────────────────────
[LD_PRELOAD 로드 영역]
 사용자 정의 open() 함수 (hook.so 내부)
────────────────────────────────────────────────────
              │
      ├─ [1] 호출 로그 출력
      │      "[hook] open: /etc/passwd"
      │
      └─ [2] dlsym(RTLD_NEXT, "open")
              └─ 원래 libc 내부 open() 주소 조회
                    │
                    ▼
────────────────────────────────────────────────────
[공식 libc 영역]
 실제 libc의 open() 함수 실행
────────────────────────────────────────────────────
                    │
           파일 디스크립터 반환
                    ▼
          사용자 프로그램으로 복귀 (정상 흐름 유지)
``` 

**1. LD_PRELOAD**
- **Abbr:** Linker Dynamic Preload  
- **Def:** An environment variable that tells the dynamic linker to load a custom `.so` file before standard libraries.  
- **Purpose:** To override standard functions (e.g., open, read) at runtime by injecting your own versions.  
- **e.g.,** LD_PRELOAD=`./hook.so cat /etc/passwd`

**2. dlsym**
- **Abbr:** Dynamic Linker Symbol  
- **Def:** A function that retrieves the memory address of a symbol (function/variable) from a shared object.  
- **Purpose:** To call the original libc function from within a hook, avoiding infinite recursion.  
- **e.g.,** `dlsym(RTLD_NEXT, "open")`

## Code / Experiment

```c
#define _GNU_SOURCE  // GNU 확장 기능을 사용하기 위한 매크로 (dlsym 등에서 필요)
#include <stdio.h>
#include <stdarg.h>   // 가변 인자 함수 (open에 mode 인자를 처리하기 위해 필요)
#include <dlfcn.h>    // dlsym, RTLD_NEXT 등 동적 심볼 관련 함수
#include <fcntl.h>    // open() 관련 플래그 상수 정의
#include <unistd.h>   // read(), close() 등 POSIX 함수 정의

// ─────────────────────────────────────────────
// 후킹 대상 1: open()
// ─────────────────────────────────────────────
int open(const char *pathname, int flags, ...) {
    // 원래 libc의 open 함수 주소를 저장할 함수 포인터
    static int (*orig_open)(const char*, int, mode_t) = NULL;

    // 최초 호출 시 dlsym을 통해 원래 open() 주소를 동적으로 찾는다
    if (!orig_open)
        orig_open = dlsym(RTLD_NEXT, "open");

    // O_CREAT 플래그가 있을 경우, mode 인자도 받아야 한다 (open은 가변 인자 함수임)
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);        // 가변 인자 시작
        mode = va_arg(args, int);     // 다음 인자를 mode_t로 읽어옴
        va_end(args);                 // 가변 인자 종료
    }

    // 파일 경로 및 플래그 로그 출력
    printf("[hook] open: %s, flags: 0x%x\n", pathname, flags);

    // 원래 open() 호출로 흐름 전달 (기능 정상 유지)
    return orig_open(pathname, flags, mode);
}

// ─────────────────────────────────────────────
// 후킹 대상 2: read()
// ─────────────────────────────────────────────
ssize_t read(int fd, void *buf, size_t count) {
    // 원래 read 함수 주소를 저장할 함수 포인터
    static ssize_t (*orig_read)(int, void*, size_t) = NULL;

    // 최초 한 번만 dlsym으로 원래 read() 주소를 가져옴
    if (!orig_read)
        orig_read = dlsym(RTLD_NEXT, "read");

    // 진짜 read() 호출 → 버퍼에 데이터를 읽어옴
    ssize_t ret = orig_read(fd, buf, count);

    // 파일 디스크립터, 읽은 크기, 반환값 로그 출력
    printf("[hook] read: fd=%d, count=%zu, ret=%zd\n", fd, count, ret);

    return ret;
}

// ─────────────────────────────────────────────
// 후킹 대상 3: fopen() - 고수준 입출력
// ─────────────────────────────────────────────
FILE *fopen(const char *pathname, const char *mode) {
    // 원래 fopen 함수 주소를 저장할 함수 포인터
    static FILE* (*orig_fopen)(const char*, const char*) = NULL;

    // 최초 호출 시 dlsym으로 진짜 fopen() 주소 가져옴
    if (!orig_fopen)
        orig_fopen = dlsym(RTLD_NEXT, "fopen");

    // fopen 호출 경로 및 모드 로그 출력
    printf("[hook] fopen: %s, mode: %s\n", pathname, mode);

    return orig_fopen(pathname, mode);
}
```

## Note

**Why use `static` for function pointers?**
Hook 함수가 여러 번 호출되어도 `dlsym()`은 한 번만 실행됨 (성능 + 안정성 향상)

**What happens without `dlsym(RTLD_NEXT)`?**
- `dlsym(RTLD_NEXT)`를 사용하지 않을 경우:
    1. 프로그램이 `open()` 호출
    2. `LD_PRELOAD`로 인해 후킹된 `open()` 실행
    3. 후킹된 `open()`이 원본 함수를 호출하려고 시도
    4. 다시 2번으로 돌아가 후킹된 `open()`이 실행됨
    5. 이 과정이 무한 반복되어 스택 오버플로우 발생
- `dlsym(RTLD_NEXT)` 사용 시:
    1. 프로그램이 `open()` 호출
    2. `LD_PRELOAD`로 인해 후킹된 `open()` 실행
    3. `dlsym`으로 원본 libc의 `open()` 주소를 직접 찾아서 호출
    4. 정상적으로 원본 함수가 실행되어 무한 반복이 발생하지 않음

**Where does `LD_PRELOAD` attach in memory?**
프로세스 초기화 시, `ld.so`가 `.so`를 ELF 인터프리터 앞에 로드 시 `/proc/[pid]/maps` 상단에서 확인 가능

```
7f8b12345000-7f8b12346000 r-xp 00000000 08:01 1234567    /path/to/hook.so 
7f8b12346000-7f8b12347000 r--p 00000000 08:01 1234567    /path/to/hook.so
7f8b12347000-7f8b12348000 rw-p 00001000 08:01 1234567    /path/to/hook.so
...
7f8b12349000-7f8b1234a000 r-xp 00000000 08:01 7654321    /lib/x86_64-linux-gnu/ld-2.31.so
```

**How is control flow preserved?**
1. 프로그램이 `open()`과 같은 함수를 호출 시, 먼저 사용자가 만든 **custom open 함수**(LD_PRELOAD를 통해 라이브러리 표준 함수들이 호출되기 전에 가로채서 작성한 함수)로 대체
2. 후킹 함수는 `printf`로 로그를 남기거나 파일 경로를 검사하는 등의 작업 수행
3. `dlsym(RTLD_NEXT)`로 찾은 `libc`의 진짜 `open()`함수 호출
4. 프로그램은 정상적으로 파일을 열 수 있으면서도, 파일 접근 감시 가능

**Is this detectable?**
`/proc/[pid]/maps`, `LD_PRELOAD` 환경 변수, `/proc/self/environ` 등으로 감지 가능

|**기법**|**탐지 우회 대상**|
|---|---|
|`unsetenv("LD_PRELOAD")`, `execve` 후 삭제|환경 변수 탐지 우회|
|`memfd_create()`, `ptrace`, `LD_AUDIT`|`/proc/maps` 흔적 우회|
|`GOT/PLT` 오염|심볼 분석 도구 우회|
|`LKM`, `syscall table` 후킹|모든 사용자 레벨 탐지 우회 (고위험)|

**Which libc functions can be hooked like this?**
- 거의 모든 함수
	- e.g., `read`, `write`, `fopen`, `execve`, `connect`, `system`...
- 일반적으로 후킹이 어려운 함수?
    - **정적으로 링크된 함수**:
        - `musl libc`로 정적 컴파일된 프로그램의 `printf()`, `malloc()` 등
        - `-static` 플래그로 컴파일된 프로그램의 모든 `libc` 함수들
    - **인라인 함수**:
        - `strlen()`, `memcpy()` 같은 작은 크기의 최적화된 문자열/메모리 함수들
        - gcc의 `-O2` 이상 최적화로 인라인화된 간단한 함수들
    - **내부 시스템 콜**:
        - Go 런타임의 직접적인 `syscall` 호출
        - 어셈블리로 작성된 `raw syscall` 함수들
    - **보안 기능이 적용된 함수**:
        - SELinux가 보호하는 `setuid()` 같은 권한 관련 함수
        - `secure_getenv()`와 같은 보안 강화 환경변수 접근 함수

**Why hook both `open()` and `fopen()`?**
- 둘 다 감시해야 전체 파일 액세스 흐름을 포착 가능하기 때문
```
# 파일 I/O 시스템 계층도
[사용자 어플리케이션 계층]
    프로그램 (예: cat, vim 등)
           │
           ▼
[고수준 C 라이브러리 계층]
    stdio.h (fopen, fread, fprintf...)
           │
           ▼
[저수준 POSIX 계층]
    open(), read(), write()
           │
           ▼
[시스템콜 인터페이스]
    syscall(SYS_open, ...)
           │
           ▼
[커널 계층]
    VFS (가상 파일시스템)
           │
           ▼
[파일시스템 드라이버]
    ext4, ntfs, etc...
           │
           ▼
[물리적 저장장치]
    HDD/SSD
```

| **함수**    | **의미**                 | **계층**             |
| --------- | ---------------------- | ------------------ |
| `open()`  | 원시 파일 디스크립터 open       | 저수준 POSIX          |
| `fopen()` | FILE* 스트림을 위한 고수준 open | stdio (C 라이브러리 계층) |
- `fopen()` = FILE stream open
    - stdio 기반의 **스트림 지향 고수준 입출력 API**
    - FILE 스트림은 fread, fwrite, fseek 등과 함께 작동하며 FILE* 구조체를 중심으로 작동