## Context
- **Tactic**: Bounding Infinite Structures
- **Technique**: Modular Wrapping Transform
- **Procedure**: “Cut → Fold → Wind” as an intuitive narrative for modular systems

## Core Idea

현실 세계의 컴퓨터, 암호 시스템, 시간 계산은 모두 무한한 수를 직접 다룰 수 없다.
따라서 우리는 주기적으로 잘라내고, 나머지를 남기고, 원형 구조로 감아 올리는 방식을 통해 **무한을 유한으로 다루는 기술**을 발전시켰다.
**모듈러 연산(Modular Arithmetic)** 은 이 과정을 수학적으로 체계화한 것이다.
이를 직관적으로 설명하기 위해 `Cut → Fold → Wind` 흐름을 따라가며 이해한다.

### Infinite Integer Line (무한 정수선)
우리는 무한히 뻗은 정수선 위에 있다.

```
                                     ∞
<-------|-------|-------|-------|-------|-------|------->
...  -2n       -n       0       n       2n      3n     ...
```

하지만 이 무한한 공간을 그대로 다룰 수는 없다.
우리는 “주기 n”을 정하고, 이 주기를 기준으로 정수선을 잘라야 한다.

### Cut: 정수선 절단
Cut은 정수선에 일정한 간격으로 절단선을 긋는 작업이다.
예를 들어 $n=5$라면, 절단선은 다음과 같이 배치된다.

```
       절단선 ↓           ↓         ↓         ↓         ↓
...─────── -10 ─────── -5 ─────── 0 ─────── 5 ─────── 10 ───...
```

어떤 정수 $x$에 대해, 고정된 양의 정수 $n$에 대해 다음처럼 표현할 수 있다.
$$x = q \times n + r \quad \text{where} \quad 0 \leq r < n$$

- $q$는 몫(quotient)은 $n$을 몇 번 지났는지를 나타낸다.
- $r$은 나머지(remainder)는 구간 안에서의 상대적 위치를 나타낸다.

이 과정을 통해 무한한 정수선 $\mathbb{Z}$를 길이 $n$의 구간들로 **균등 분할**하게 된다.
결국 우리는 $\mathbb{Z}/n\mathbb{Z}$라는 **몫집합(quotient set)**을 만든다.

### 구간 분리 구조

```
[-10] -9 -8 -7 -6    [-5] -4 -3 -2 -1    [0] 1 2 3 4
     (q=-2)              (q=-1)              (q=0)
```

- 각 구간은 $n$의 배수를 경계로 하여 나뉜다.
- 각 구간 내부에는 정확히 $n$개의 연속된 정수가 존재한다.
- 각 구간은 몫 $q$에 대응한다.

### Fold: 나머지를 기준으로 접기
Cut을 통해 무한 정수선을 잘랐다면, 이제 Fold 단계에서는 **몫 정보($q$)를 버리고 나머지($r$)만을 남긴다.**
결국 Fold는 무한 정수선을 나머지에 따라 $n$개의 그룹으로 압축하는 과정이다.

$$
r = x \bmod n,\quad
x \equiv r \pmod{n}
$$

```
Fold (mod 5)

r=0 | …, –10, –5, 0, 5, 10, …
r=1 | …, –9,  –4, 1, 6, 11, …
r=2 | …, –8,  –3, 2, 7, 12, …
r=3 | …, –7,  –2, 3, 8, 13, …
r=4 | …, –6,  –1, 4, 9, 14, …

⇒ 접힌 나머지 공간: {0, 1, 2, 3, 4}
```

### Fold가 만드는 수학적 구조
Fold를 통해 생성되는 것은 **동치류(equivalence class)** 이다.

```
 - [0] = {…, -10, -5, 0, 5, 10, 15, …}
 - [1] = {…, -9, -4, 1, 6, 11, 16, …}
 - …
```

수학적으로, 두 수 $x, y$가 다음을 만족하면 합동이다.

$$
x \equiv y \pmod{n} \quad \iff \quad n \mid (x-y)
\quad \iff \quad x \mod n = y \mod n
$$

이 합동 관계는 아래를 모두 만족하는 **동치 관계(equivalence relation)** 이다.
- **반사성(reflexive)**: 어떤 수  $x$는 항상 자기 자신과 합동이다.  $$x \equiv x \pmod{n}$$
- **대칭성(symmetric)**: $x \equiv y \pmod{n}$이면, $y \equiv x \pmod{n}$이다.  
  $$
  x \equiv y \pmod{n} \quad \Rightarrow \quad y \equiv x \pmod{n}
  $$
- **추이성(transitive)**: $x \equiv y \pmod{n}$이고 $y \equiv z \pmod{n}$이면, $x \equiv z \pmod{n}$이다.  
  $$
  x \equiv y \pmod{n}, \quad y \equiv z \pmod{n} \quad \Rightarrow \quad x \equiv z \pmod{n}
  $$

### Wind: 원형 구조 만들기
접힌 나머지 값을 순환하는 원형으로 배열한다. 이로써 **유한 순환군(cyclic group)**이 완성된다.

```
Wind (mod 5)

      (0)
    ↗     ↘
  (4)     (1)
   |       |
   |       |
  (3)-----(2)
```

- 덧셈/곱셈이 이 원형 안에서 닫힌다.
- `4+1=5≡0`, `2+3=5≡0` 등 순환을 보여준다.

이 구조가 바로 **$\mathbb{Z}/5\mathbb{Z}$** 또는 **$\mathbb{Z}_5$**인 **모듈러 환(modular ring)**이다.

## Note
`Cut`은 무한 정수선에 **몫과 나머지(divison with remainder)** 구조를 설정하여 경계를 세우고, `Fold`는 나머지 값에 따라 **동치류(partition into equivalence classes)**로 분할하여 유한 집합을 만들며, `Wind`는 이 집합 위에 **유한 순환군(finite cyclic group)** 구조를 부여하여 새로운 연산 체계를 완성한다. 
이 `Cut → Fold → Wind` 과정은 단순한 수학 계산이 아니라, 무한을 유한으로 재구성하는 수학적 방법론이자, 새로운 연산 세계를 설계하는 방식이다.
