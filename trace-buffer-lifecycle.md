## Context
- **Tactic**: Memory-Oriented Analysis
- **Technique**: Tracing the Lifecycle of Stack/Heap Buffers
- **Procedure**:
	- Visualize how buffers are created, used, and freed in memory
	- Examine the internal structure of memory-resident buffers
	- Follow the data flow from input to output through buffers
	- Identify potential risks (e.g., overflows) at buffer boundaries

## Core Idea

```markdown
1. Memory Structure (Where to store?)
+----------------------+
|        Stack         |   ← Temporary function memory
|                      |
|   ↳ Input Buffer     |   e.g., char buf[128];
|                      |
|   Internal Layout:                 (Figure 2 inlined)
|   ┌────────────┬────────────┐
|   │ Offset     │ Content    │
|   ├────────────┼────────────┤
|   │ 0 ~ 3      │ Header     │
|   │ 4 ~ 7      │ Flags      │
|   │ 8 ~ 127    │ Payload    │
|   └────────────┴────────────┘
|                      |
|        Heap          |   ← Dynamically allocated memory
+----------------------+
```
**Figure 1.**  Conceptual Overview of Buffer Memory


**Example: File Reading Process**
1. Allocate buffer memory in heap/stack
2. Read data from hard disk to buffer
3. Process buffer data in program
4. Store results back to buffer
5. Output from buffer to screen

A buffer is a temporary storage area in memory that serves as an intermediary between system components, particularly between input/output devices and programs. It enables efficient management of data flow and temporary storage.

```markdown
# Data Flow Summary (How does it move?)
[Input Device] ➜ [Buffer] ➜ [Program] ➜ [Buffer] ➜ [Output Device]
              ↕          ↕           ↕
         Stack/Heap   Processing  Stack/Heap
         Allocation   Phase       Allocation

# Data Flow
[ Input Device ]
(e.g., keyboard, file, socket)
       │
       ▼
Call: recv(), fgets(), read()
       │     ↳ receives user or system input
       ▼
┌──────────────────────────────┐
│        Input Buffer          │
│  (e.g., char buf[128];)      │
│  stack or heap allocated     │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│        Program Logic         │
│  e.g., parse(buf), logic()   │
│  process input data here     │
└──────────────────────────────┘
       │
       ▼
Call: printf(), fwrite(), send()
       │     ↳ writes output to buffer
       ▼
┌──────────────────────────────┐
│        Output Buffer         │
│  (e.g., libc stdout buffer)  │
│  flushed when full or on \n  │
└──────────────────────────────┘
       │
       ▼
[ Output Device ]
(e.g., terminal, file, network socket)
```
**Figure 2** Conceptual data flow of a buffer in memory

## Code / Experiment

```c
#include <stdio.h>
#include <string.h>

// 간단한 예: 파일에서 한 줄씩 읽어오는 버퍼
int main(int argc, char* argv[]) {
    char buffer[32]; // 32바이트짜리 버퍼
    FILE* fp;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    fp = fopen(argv[1], "r");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    // fgets를 이용해 한 줄을 buffer에 저장
    if (fgets(buffer, sizeof(buffer), fp)) {
        printf("첫 줄: %s", buffer);
    }

    fclose(fp);
    return 0;
}
```

### Basic Buffer Usage Example
```c
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[256]; // 스택에 버퍼 할당

    // 버퍼에 데이터 쓰기
    strcpy(buffer, "Hello, Memory World!");

    // 버퍼 내용 출력
    printf("%s\\n", buffer);

    return 0; // 함수 종료 시 버퍼 자동 해제
}
```

### Buffer Flush Operation Test
```c
#include <stdio.h>
#include <unistd.h> // sleep() 함수 사용

int main() {
    printf("이 텍스트는 버퍼에 저장됩니다"); // 줄바꿈 없음 - 버퍼에 저장
    sleep(3); // 3초 대기 - 이 동안 출력되지 않음

    printf("\\n"); // 줄바꿈 문자 - 버퍼 플러시 발생

    printf("이 텍스트는 ");
    fflush(stdout); // 명시적 플러시 - 즉시 출력

    printf("즉시 출력됩니다");
    fflush(stdout);

    return 0;
}
```

### Buffer Overflow
```c
#include <stdio.h>
#include <string.h>

void vulnerable_function() {
    char small_buffer[10]; // 10바이트 스택 버퍼

    // 버퍼 크기보다 큰 데이터 복사 시도 - 오버플로우 발생!
    strcpy(small_buffer, "This string is too long for the buffer");

    printf("Buffer content: %s\\n", small_buffer);
}

int main() {
    vulnerable_function();
    return 0;
}
```

## Note

### Questions for Further Exploration

- **When is a buffer allocated on the heap instead of the stack?**
1. **버퍼 크기가 크거나 정적으로 알 수 없는 경우**
    - 스택은 일반적으로 수십~수백 KB 제한 (예: 1MB 미만)
    - 예: `char *buf = malloc(user_input_size);`
2. **버퍼를 여러 함수나 스레드 간에 공유해야 할 경우**
    - 스택은 함수가 종료되면 소멸됨
    - 예: 힙에 할당하고 포인터로 전달
3. **버퍼 생존 시간을 명시적으로 제어하고 싶을 때**
    - `malloc/free`로 메모리 수명 관리
4. **동적으로 크기를 조절하거나 재사용할 때**
    - `realloc` 등과 함께 사용

- **At what exact point in memory does a buffer overflow begin to corrupt adjacent data?**

    - 복사 함수(`strcpy`)가 NULL까지 복사하는 과정에서 발생
    - 침범: `buf`의 끝 이후부터 시작
        - +0~+32: 정상 버퍼
        - +36~+40: Saved EBP
        - +40~+44: Return Address (RET)
    - GDB에서 `x/32x &buf`, Pwntools `cyclic()`/`cyclic_find()`로 침범 위치 확인 가능
    
- **How are standard library output buffers managed, and when does flushing occur?**

	```markdown
      [ Program Calls printf("Hello") ]
                   │
                   ▼
          +-------------------+
          |   Output Buffer   |   ← Not shown yet!
          +-------------------+
                   │
          (Waiting... until flush)
                   │
          +------------------------+
          |   Flush Conditions     |
          |  - Newline (\\n)       |
          |  - fflush(stdout)      |
          |  - Buffer full         |
          |  - Program ends        |
          +------------------------+
                   │
                   ▼
          +-------------------+
          |  Output Device    |   ← Now it's shown!
          |  (e.g., Terminal) |
          +-------------------+
	```