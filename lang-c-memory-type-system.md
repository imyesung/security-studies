## Context
- **Tactic**: Type-Driven Memory Interpretation  
- **Technique**: Structuring C Types as Memory Models  
- **Procedure**:
    - Classify and map C types to memory layout
    - Analyze struct size variation via alignment/padding
    - Apply reinterpretation techniques for binary-level insight

## Core Idea

### Overview of C type system

#### 1. Primitive Data Types 기본 데이터 타입

|분류|타입|크기|설명|
|---|---|---|---|
|**정수형**|`char`|1바이트|문자/작은 정수 저장|
||`short`|2바이트|작은 범위의 정수|
||`int`|일반적으로 4바이트|기본 정수 타입|
||`long`|4~8바이트|큰 범위의 정수|
||`long long`|8바이트|매우 큰 범위의 정수|
|**부호 지정자**|`signed`|-|양수와 음수 모두 표현(기본값)|
||`unsigned`|-|양수만 표현 (0 포함)|
|**부동 소수점형**|`float`|4바이트|단정도 실수|
||`double`|8바이트|배정도 실수 (정밀도 높음)|
||`long double`|12~16바이트|확장 정밀도 실수|
|**void 타입**|`void`|-|값이 없음, 범용 목적|

#### 2. Derived Data Types 파생 데이터 타입

| 분류         | 구문                  | 설명                        | 예시                         |
| ---------- | ------------------- | ------------------------- | -------------------------- |
| **포인터 타입** | `type *`            | 특정 타입의 변수 주소 저장           | `int *p;`                  |
|            | `void *`            | 범용 포인터<br>(어떤 타입의 주소든 저장) | `void *ptr;`               |
| **배열 타입**  | `type name[size]`   | 같은 타입의 요소들 모음             | `int arr[10];`             |
| **구조체**    | `struct name {...}` | 다양한 타입의 변수들 묶음            | `struct Person {...};`     |
| **공용체**    | `union name {...}`  | 여러 타입이 메모리 공유             | `union Data {...};`        |
| **열거형**    | `enum name {...}`   | 상수값 집합                    | `enum Color {RED, GREEN};` |
#### 3. Type Qualifiers 타입 한정자

| 한정자        | 설명             | 예시                      |
| ---------- | -------------- | ----------------------- |
| `const`    | 값 변경 불가능       | `const int x = 5;`      |
| `volatile` | 컴파일러 최적화 방지    | `volatile int counter;` |
| `restrict` | 포인터 최적화(C99)   | `int * restrict ptr;`   |
| `_Atomic`  | 원자적 연산 지원(C11) | `_Atomic int counter;`  |
- `volatile`: 외부 요인(하드웨어 등)에 의해 값이 바뀔 수 있으니 최적화하지 말라는 힌트를 컴파일러에 제공
- `restrict`: 이 포인터가 가리키는 메모리는 이 포인터만이 접근한다고 컴파일러에 보장
#### 4. User-Defined Types 사용자 정의 타입

|구문|설명|예시|
|---|---|---|
|`typedef 기존타입 새이름`|기존 타입에 새 이름 부여|`typedef unsigned long size_t;`|

---

### Link types to memory layout and binary representation

> C 언어의 데이터 타입은 단순한 의미적 분류를 넘어서, 해당 값이 메모리에 어떻게 저장되고, 어떤 방식으로 읽고 쓰일지를 결정하는 핵심 요소이다.

#### 1. 메모리 정렬(Alignment)과 패딩(Padding)

CPU 아키텍처는 특정 데이터 타입에 대한 정렬 요구사항을 가지고 있다.
```c
// Memory alignment and padding visualization
struct Example {
    char c;    // 1 byte
    int i;     // 4 bytes
};

Memory layout:
+------+------+------+------+
|  c   | pad  | pad  | pad  |  ← offset 0
+------+------+------+------+
|  i0  | i1   | i2   | i3   |  ← offset 4
+------+------+------+------+
   ↑                    ↑
 Low address       High address
```
> **Offset** 
> 각 구조체 멤버는 구조체 시작 주소로부터 특정 바이트만큼 떨어진 위치에 저장되며, 이를 오프셋(offset)이라 한다. 예를 들어, 위 예제에서 c의 offset은 0이고, i의 offset은 4이다.


#### 2. Struct Optimization and Memory Efficiency
> The size of a struct can vary depending on the order of its fields.
```c
struct BadLayout {
    char a;    // 1 byte
    double b;  // 8 bytes
    int c;     // 4 bytes
    char d;    // 1 byte
}; // Total size: 24 bytes (including padding)

struct OptimizedLayout {
    double b;  // 8 bytes
    int c;     // 4 bytes
    char a;    // 1 byte
    char d;    // 1 byte
}; // Total size: 16 bytes (including padding)
```

```markdown
# Struct Memory Layouts: Bad vs Optimized

 BadLayout (24 bytes)               OptimizedLayout (16 bytes)
+------+------+------+------+     +------+------+------+------+
| a | pad(7)                |     | b(8)                      |
+------+------+------+------+     +------+------+------+------+
| b(8)                      |     | c(4)        |a | d |pad(2)|
+------+------+------+------+     +------+------+------+------+
| c(4)        |d  | pad(3)  |
+------+------+------+------+
```

#### 3. Type Punning & Union
- `union`: C 언어의 파생 데이터 타입으로, **여러 멤버가 하나의 메모리 공간을 공유**하도록 정의된다.
- **Type Punning**: 이 메모리 특성을 활용해 저장된 값을 다른 타입으로 해석하는 기법

```c
union FloatInt {
    uint32_t i;
    float    f;
};

union FloatInt u;
u.f = 3.14f;       // store float as IEEE 754 bits
printf("%x", u.i); // read same bits as integer → 0x4048F5C3


// Both u.i and u.f share the same memory space.
+--------+--------+--------+--------+
|    Shared 4-byte memory region    |
|    (interpreted as float or int)  |
+--------+--------+--------+--------+
        ↑
   u.f writes bits
   u.i reads the same bits
```

## Code / Experiment

```c
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

// 구조체 패딩과 메모리 정렬 예제
struct Example {
    char c;    // 1 byte
    int i;     // 4 bytes
};

// 타입 펀칭 예제
union FloatBits {
    float f;
    uint32_t bits;
};

int main() {
    // 1. 기본 데이터 타입 크기 출력
    printf("char: %lu 바이트\n", sizeof(char));
    printf("int: %lu 바이트\n", sizeof(int));
    printf("float: %lu 바이트\n", sizeof(float));
    
    // 2. 구조체 크기와 패딩 분석
    printf("Example 구조체 크기: %lu 바이트\n", sizeof(struct Example));
    printf("c의 오프셋: %lu\n", offsetof(struct Example, c));
    printf("i의 오프셋: %lu\n", offsetof(struct Example, i));
    
    // 3. Type Punning으로 float의 비트 표현 확인
    union FloatBits fb;
    fb.f = 3.14f;
    printf("3.14의 16진수 표현: 0x%08X\n", fb.bits);
    
    // 4. 정수 비트를 float로 reinterpret
    fb.bits = 0x4048F5C3;
    printf("0x4048F5C3의 float 해석: %f\n", fb.f);

    return 0;
}
```

## Note

> **Why is type punning through pointer casting considered undefined behavior in C, and how is using union safer?**

- "정의되지 않은 동작(undefined behavior)"은 C 언어 표준에서 결과를 보장하지 않는 동작을 의미한다. 즉, 프로그램이 예측할 수 없는 방식으로 작동할 수 있다는 뜻이다.
- 포인터 캐스팅을 통한 Type Punning 위험성
    - 다른 타입의 메모리 정렬 요구사항이 다를 수 있음
    - 컴파일러마다 다르게 해석될 수 있음
    - 하드웨어 아키텍처에 따라 다른 결과가 나올 수 있음

	∴ 실무에서는 포인터 캐스팅보다 `union` 기반의 Type Punning이 C 표준에 부합하며, 컴파일러 동작과 플랫폼 간 이식성 측면에서도 더 안전한 방식이다.