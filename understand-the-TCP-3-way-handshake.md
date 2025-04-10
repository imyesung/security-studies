## Context

- **Tactic:** Connection Establishment (연결 설정)
- **Technique:** Reliable Connection Setup (신뢰성 있는 연결 구성)
- **Procedure:**
	1. `Client → Server: SYN, Seq = x`  
	2. `Server → Client: SYN-ACK, Seq = y, Ack = x+1` 
	3. `Client → Server: ACK, Seq = x+1, Ack = y+1`

## **Core Idea**

**TCP(Transmission Control Protocol)**는 인터넷 프로토콜 스위트(TCP/IP)의 핵심 프로토콜 중 하나이다. **TCP/IP**는 인터넷과 대부분의 상용 네트워크에서 사용되는 통신 프로토콜의 모음으로, 계층화된 구조를 가진다. 하위 계층의 **IP(Internet Protocol)**가 데이터 조각(패킷)의 주소 지정 및 경로 설정을 담당하고, 그 상위 계층인 TCP가 애플리케이션 간의 신뢰성 있는 데이터 전송을 관리한다.

TCP는 네트워크상의 애플리케이션 간에 신뢰성 있고, 순서가 보장되며, 오류 검사를 거친 **옥텟 스트림(octet stream)** 전송을 제공한다. **스트림**은 데이터가 개별 메시지나 레코드 같은 명확한 경계 없이, 연속적인 바이트(옥텟)의 흐름으로 취급됨을 의미한다. TCP는 이 바이트 스트림이 송신된 순서대로, 손실이나 중복 없이 수신 측 애플리케이션에 전달되도록 보장한다.

TCP는 **연결 지향형(Connection-Oriented) 프로토콜**이기 때문에, 실제 데이터 전송 전에 송신자와 수신자 사이에 논리적인 연결을 설정하는 과정이 필수적이다. 이 연결 설정 과정의 핵심 메커니즘이 바로 **TCP 3-way 핸드셰이크**이다. 이 과정은 양방향 통신 설정, 시퀀스 번호 동기화, 그리고 연결 매개변수 협상을 가능하게 한다.

**Handshake의 목적**
- 양 끝점이 데이터 송수신 준비가 되었는지 확인
- 데이터 전송 순서를 관리하기 위한 **초기 시퀀스 번호(ISN)**를 교환하여 동기화
- 윈도우 크기, 최대 세그먼트 크기(MSS) 등의 연결 매개변수 협상

### **TCP 3-Way Handshake 단계별 상세 설명**

|**단계**|**교환 메시지**|**설명**|
|---|---|---|
|1|`SYN`|클라이언트가 서버에 연결을 요청하고, 자신의 **초기 시퀀스 번호(ISN)** (x)를 전송함|
|2|`SYN-ACK`|서버가 요청을 수락하고, **자신의 ISN**(y)을 전송. **클라이언트 ISN+1**(x+1) 확인함|
|3|`ACK`|클라이언트가 **서버 ISN+1**(y+1)을 확인하여 연결 설정을 완료함|

> 참고: 초기 시퀀스 번호(ISN)는 보안을 위해 예측 불가능한 무작위 값으로 선택된다. 이는 TCP 연결 가로채기(Session Hijacking)와 같은 공격을 어렵게 만든다.

### **기본 용어: 패킷(Packet)**

네트워크 통신에서 **패킷**은 데이터를 주고받는 기본 단위이다. 일반적으로 헤더(Header)와 페이로드(Payload)로 구성된다. 헤더에는 송신 및 수신 IP 주소, 포트 번호, 프로토콜 종류, 오류 검출 코드, 그리고 TCP의 경우 순서 번호(Sequence Number), 확인 응답 번호(Acknowledgment Number), 제어 플래그 등 패킷을 올바르게 목적지까지 전달하고 처리하기 위한 제어 정보가 포함된다.

페이로드에는 실제 전송하려는 사용자 데이터가 담긴다. TCP/IP 통신에서는 애플리케이션 데이터가 TCP 세그먼트로 나뉘고, 각 TCP 세그먼트는 다시 IP 패킷의 페이로드에 캡슐화되어 네트워크를 통해 전송된다. 3-way 핸드셰이크에서 교환되는 `SYN`, `SYN-ACK`, `ACK` 메시지 역시 이러한 패킷 형태로 전달된다.

```markdown
      Client                Server
        |                     |
        |---------SYN-------->|
        |  (Seq=x)            | Client sends SYN with its Initial Sequence Number (ISN).
        |                     | Client state: SYN_SENT
        |                     |
        |<------SYN-ACK-------| Server replies with SYN-ACK, containing its own ISN (y)
        |  (Seq=y, Ack=x+1)   | and acknowledging the client's SYN (Ack=x+1).
        |                     | Server state: SYN_RECEIVED
        |                     |
        |---------ACK-------->| Client sends ACK, acknowledging the server's SYN (Ack=y+1).
        |  (Seq=x+1, Ack=y+1) | Sequence number is now x+1.
        |                     | Client state: ESTABLISHED
        |                     | Server receives ACK, Server state: ESTABLISHED
        |                     |
    +---------------------------+
    |  Connection Established   | Both sides are ready for data transfer.
    +---------------------------+
```

_**Figure 1.** TCP 3-Way Handshake Flow_

### 플래그 및 필드의 의미

### 1. Handshake Packet Analysis

#### `SYN` (Synchronize) 패킷 (Client → Server)
- **의미:** 새로운 연결 시작을 **요청한다**.
- **TCP 헤더:**
    - `SYN` 플래그 = **1**
    - `ACK` 플래그 = **0** (아직 확인할 것이 없음)
    - `Sequence Number` = 클라이언트의 **ISN** (예: **x**)
- **상태:** 클라이언트는 이 단계 후 `SYN_SENT` 상태로 전환됨

#### `SYN-ACK` (Synchronize-Acknowledge) 패킷 (Server → Client)
- **의미:** 연결 요청 수락 및 자신의 연결 시작을 **알린다**.
- **TCP 헤더:**
    - `SYN` 플래그 = **1** (서버도 동기화를 원함)
    - `ACK` 플래그 = **1** (클라이언트의 SYN을 확인함)
    - `Sequence Number` = 서버의 **ISN** (예: **y**)
    - `Acknowledgment Number` = **클라이언트 ISN + 1** (즉, **x+1**)
- **상태:** 서버는 이 단계 후 `SYN_RECEIVED` 상태로 전환됨

#### `ACK` (Acknowledge) 패킷 (Client → Server)
- **의미:** 상대방의 연결 요청 확인 및 연결 완료를 **알린다**.
- **TCP 헤더:**
    - `SYN` 플래그 = **0** (더 이상 새로운 연결 시작 아님)
    - `ACK` 플래그 = **1** (서버의 SYN을 확인함)
    - `Sequence Number` = **클라이언트 ISN + 1** (즉, **x+1**)
    - `Acknowledgment Number` = **서버 ISN + 1** (즉, **y+1**)
- **상태:** 이 단계 후 양쪽 모두 `ESTABLISHED` 상태로 전환됨

### 2. 주요 TCP Header Flag
- `SYN` (Synchronize): 연결 **초기화** 및 시퀀스 번호 **동기화**. (`1` = 연결 시작)
- `ACK` (Acknowledgment): 패킷 **수신 확인**. (`1` = Acknowledgment Number 필드 유효)
- `FIN` (Finish): 데이터 전송 **완료** 및 연결 **종료 요청**. (4-way 핸드셰이크에서 사용됨)
- `RST` (Reset): **오류 발생** 또는 즉각적인 연결 **강제 종료**.
- `PSH` (Push): 수신 버퍼의 데이터를 **즉시 애플리케이션으로 전달** 요청.
- `URG` (Urgent): **긴급 데이터** 포함. (Urgent Pointer 필드 유효)

### 3. TCP Header Field
- **Sequence Number (시퀀스 번호):**
    - 세그먼트의 **첫 데이터 바이트에 부여되는 고유 번호**이다.
    - TCP는 이 번호를 사용하여 데이터 스트림 내에서 각 바이트의 순서를 식별한다. 수신 측에서는 이 번호를 통해 **패킷이 순서대로 도착했는지 확인**하고, 순서가 어긋났을 경우 **올바르게 재조립**한다. 또한, **데이터 손실 및 중복을 탐지**하는 데에도 사용된다.
    - 3-way 핸드셰이크 시: 양측이 초기 시퀀스 번호(ISN)를 교환하여 데이터 전송 시작점의 시퀀스 번호를 동기화한다.
- **Acknowledgment Number (확인 응답 번호):**
    - 수신측이 **다음에 받기를 기대하는** 시퀀스 번호. (즉, 마지막으로 성공적으로 수신한 바이트의 시퀀스 번호 + 1)
    - **`ACK=1`일 때만 유효**. 이를 통해 송신측은 어느 데이터까지 성공적으로 전달되었는지 파악한다.
- **Window Size (윈도우 크기):**
    - 수신 버퍼의 남은 공간 크기. **흐름 제어(Flow Control)**에 사용된다. 수신측이 처리할 수 있는 데이터 양을 송신측에 알려 과도한 데이터 전송을 방지한다.
- **Checksum (체크섬):**
    - TCP 헤더 및 데이터의 **오류 감지** 및 **무결성 검증**을 위한 값이다.

### TCP State Transition (상태 전이)
**3-way 핸드셰이크 과정 중 TCP 상태 변화**
1. **Client:** `CLOSED` → `SYN_SENT`
    - **시점:** 클라이언트가 `connect()` 호출 후 `SYN` 전송 시.
    - **의미:** 연결 시작, 서버의 `SYN-ACK` 응답 대기.
2. **Server:** `LISTEN` → `SYN_RECEIVED`
    - **시점:** 서버가 `SYN` 수신 후 `SYN-ACK` 전송 시.
    - **의미:** 클라이언트의 `ACK` 대기.
3. **Client:** `SYN_SENT` → `ESTABLISHED`
    - **시점:** 클라이언트가 `SYN-ACK` 수신 후 `ACK` 전송 시.
    - **의미:** 연결 성공적으로 설정 완료.
4. **Server:** `SYN_RECEIVED` → `ESTABLISHED`
    - **시점:** 서버가 클라이언트로부터 마지막 `ACK` 수신 시.
    - **의미:** 연결 성공적으로 설정 완료.

### **시간 초과 및 재전송 메커니즘**
- **SYN 타임아웃 (클라이언트 측)**
    - `SYN` 전송 후 `SYN-ACK` 응답 대기 시간 제한.
    - 초기 타임아웃: 보통 **1초**, 이후 지수적 증가 (Exponential Backoff).
    - 최대 재시도 (보통 **3~5회**) 후 연결 실패 처리.
- **SYN-ACK 타임아웃 (서버 측)**
    - `SYN-ACK` 전송 후 `ACK` 응답 대기 시간 제한.
    - 타임아웃: 보통 **30초 ~ 2분**.
    - 타임아웃 발생 시, 관련 리소스 정리 후 다시 `LISTEN` 상태로 복귀.

## **Code / Experiment**

- 클라이언트 측 C 코드 (3-Way Handshake 시뮬레이션)
```c
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

int main() {
    int client_socket;
    struct sockaddr_in server_addr;

    // 소켓 생성 (IPv4, TCP)
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        perror("[Client] 소켓 생성 실패");
        return -1;
    }

    // 서버 주소 설정
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);  // 대상 서버 포트
    server_addr.sin_addr.s_addr = inet_addr("192.168.1.1");  // 대상 서버 IP (수정 필요)

    printf("[Client] 서버에 연결 시도 (connect() 호출)...\n");
    printf("[Client] 내부적으로 SYN 패킷 전송됨.\n");

    // connect() 내부에서 3-way 핸드셰이크 자동 수행
    // 1. Client → Server: SYN, Seq = x
    // 2. Server → Client: SYN-ACK, Seq = y, Ack = x+1
    // 3. Client → Server: ACK, Seq = x+1, Ack = y+1
    if (connect(client_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("[Client] 연결 실패 (핸드셰이크 실패 또는 서버 응답 없음)");
        close(client_socket);
        return -1;
    }

    printf("[Client] TCP 3-way 핸드셰이크 완료. 연결 상태: ESTABLISHED\n");

    // --- TCP 핸드셰이크 완료 이후 데이터 전송 예시 ---
    char msg[] = "Hello, server!";
    send(client_socket, msg, strlen(msg), 0);
    printf("[Client] 데이터 전송 완료: \"%s\"\n", msg);

    // 연결 종료: FIN 전송 → 4-way 핸드셰이크 시작
    close(client_socket);
    printf("[Client] 연결 종료 시작 (내부적으로 FIN 패킷 전송됨).\n");

    return 0;
}
```

- Python Scapy 코드(패킷 캡처 및 분석)
```python
# 경고: 이 코드는 네트워크 패킷을 직접 캡처하므로, 실행 시 root/관리자 권한이 필요할 수 있다.
# 개인 정보 보호 및 법적 문제에 유의하여 책임감 있게 사용해야 한다.

from scapy.all import *
import sys
import signal

# 종료 시그널 핸들러
def signal_handler(sig, frame):
    print('\\n패킷 캡처 중지됨.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler) # Ctrl+C 처리

print("TCP 3-way 핸드셰이크 관련 패킷 모니터링 시작...")
print("대상 포트 80 또는 8080 (필요시 필터 수정)")
print("Ctrl+C 를 눌러 중지.")

def packet_callback(packet):
    # IP 레이어와 TCP 레이어가 모두 있는지 확인
    if IP in packet and TCP in packet:
        ip_layer = packet[IP]
        tcp_layer = packet[TCP]
        flags = tcp_layer.flags

        src_ip_port = f"{ip_layer.src}:{tcp_layer.sport}"
        dst_ip_port = f"{ip_layer.dst}:{tcp_layer.dport}"

        # 핸드셰이크 관련 패킷 필터링 (SYN, SYN-ACK, ACK)
        # SYN (플래그 'S')
        if flags == 'S':
            print(f"[SYN] {src_ip_port} -> {dst_ip_port} | Seq={tcp_layer.seq}")

        # SYN-ACK (플래그 'SA')
        elif flags == 'SA':
            print(f"[SYN-ACK] {src_ip_port} -> {dst_ip_port} | Seq={tcp_layer.seq}, Ack={tcp_layer.ack}")

        # ACK (플래그 'A') - 핸드셰이크의 마지막 ACK는 보통 Payload가 없음
        elif flags == 'A':
            # Scapy에서 payload 유무 확인 (버전 따라 .load 또는 .payload)
            payload_len = 0
            if Raw in tcp_layer: # Raw 레이어가 있으면 payload 존재
                payload_len = len(tcp_layer[Raw].load)

            # 핸드셰이크 관련 ACK는 payload 길이가 0인 경우가 많음 (단, 데이터 전송 중 ACK와 구분 필요)
            if payload_len == 0:
                print(f"[ACK] {src_ip_port} -> {dst_ip_port} | Seq={tcp_layer.seq}, Ack={tcp_layer.ack}")

# 네트워크 인터페이스에서 TCP 패킷만 캡처
# filter 예시: "tcp port 80 or tcp port 8080" (특정 포트만) / "tcp" (모든 TCP)
try:
    sniff(filter="tcp and (port 80 or port 8080)", prn=packet_callback, store=0)
except PermissionError:
    print("[오류] 패킷 캡처를 위해 root 또는 관리자 권한이 필요합니다.")
except Exception as e:
    print(f"[오류] 스니핑 중 예상치 못한 오류 발생: {e}")
```

## Note
- TCP 연결 설정은 **3-way 핸드셰이크**, 연결 종료는 일반적으로 **4-way 핸드셰이크** (FIN, ACK 교환)를 사용한다.
- 응답 없는 연결 시도를 방지하기 위해 **타임아웃 및 재전송 메커니즘**이 동작한다.
- 핸드셰이크 과정의 취약점을 이용한 **SYN Flooding**과 같은 서비스 거부(DoS) 공격이 존재하며, 이에 대한 방어 메커니즘이 중요하다.
- **TCP Fast Open (TFO)**는 재연결 시 핸드셰이크를 최적화하여 지연 시간을 줄이는 확장 기능이지만, 모든 환경에서 지원되지 않으며 보안 설정이 필요할 수 있다.

### 보안 고려사항
- **SYN Flooding (SYN 홍수 공격)**
    - **공격:** 다수의 위조된 `SYN` 패킷만 보내고 마지막 `ACK`는 보내지 않아 서버의 연결 대기 큐 (Backlog Queue)를 고갈시켜 정상적인 사용자의 연결을 방해함 (서비스 거부, DoS).
    - **방어:** **SYN 쿠키 (SYN Cookies)** 사용 - 서버가 `SYN_RECEIVED` 상태를 실제로 유지하지 않고도 클라이언트의 `ACK`를 암호학적으로 검증하여 정상 연결 처리. 또는 방화벽에서 임계치 기반 차단.
- **TCP Sequence Number Prediction Attack (시퀀스 번호 예측 공격)**
    - **공격:** ISN 생성 규칙의 취약점을 이용하거나 패턴을 분석하여 유효한 다음 시퀀스 번호를 예측, 이를 통해 TCP 세션에 끼어들거나 데이터를 위변조하는 세션 하이재킹 시도.
    - **방어:** 예측 불가능한 **강력한 무작위 ISN 생성 알고리즘** 사용.
- **TCP Reset Attack (RST 공격)**
    - **공격:** 유효한 시퀀스 번호 범위 내에서 위조된 `RST` 패킷을 보내 정상적인 TCP 연결 강제 종료.
    - **방어:** 방화벽 등에서 연결 상태를 추적하여 비정상적인 RST 패킷 필터링, 패킷의 시퀀스 번호 유효성 검사 강화.

---
