"""Extra read-only Windows telemetry for the local forensic dashboard.

This module intentionally avoids passwords, secrets, private file contents,
keystrokes, webcam/microphone data, and remote collection.
"""
import json
import os
import subprocess
from typing import Any


def _run(command: str, timeout: int = 12) -> str:
    if os.name != "nt":
        return ""
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return (p.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _json(command: str, timeout: int = 12) -> Any:
    raw = _run(command, timeout)
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def battery() -> list[dict[str, Any]]:
    return _json(
        "Get-CimInstance Win32_Battery | "
        "Select-Object Name,DeviceID,Status,BatteryStatus,EstimatedChargeRemaining,"
        "EstimatedRunTime,DesignVoltage,DesignCapacity,FullChargeCapacity | "
        "ConvertTo-Json -Compress"
    )


def security_products() -> list[dict[str, Any]]:
    # Security Center is read-only here. ProductState is retained as the
    # Windows-reported numeric state rather than guessing its bit layout.
    return _json(
        "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct "
        "| Select-Object DisplayName,ProductState,PathToSignedProductExe,"
        "PathToSignedReportingExe,timestamp | ConvertTo-Json -Compress"
    )


def update_services() -> list[dict[str, Any]]:
    return _json(
        "Get-CimInstance Win32_Service -Filter "
        "'Name="wuauserv" OR Name="bits" OR Name="cryptsvc" OR Name="UsoSvc"' "
        "| Select-Object Name,DisplayName,State,StartMode,StartName,ProcessId | "
        "ConvertTo-Json -Compress"
    )


def time_sync() -> dict[str, str]:
    return {
        "source": _run("w32tm /query /source", 8) or "Unavailable",
        "status": _run("w32tm /query /status", 8) or "Unavailable",
    }


def power_capabilities() -> str:
    return _run("powercfg /a", 8) or "Unavailable"


def reliability_events() -> list[dict[str, Any]]:
    # Common application crash / Windows Error Reporting event IDs.
    return _json(
        "Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000,1001} "
        "-MaxEvents 40 -ErrorAction SilentlyContinue | "
        "Select-Object TimeCreated,Id,ProviderName,LevelDisplayName,Message | "
        "ConvertTo-Json -Compress -Depth 4",
        15,
    )


def event_counts() -> list[dict[str, Any]]:
    # Counts only; event messages are already exposed in the normal Events view.
    script = r"""
$since=(Get-Date).AddHours(-24)
$logs=@('System','Application','Security')
$out=@()
foreach($log in $logs){
  try{
    $events=Get-WinEvent -FilterHashtable @{LogName=$log;StartTime=$since} -ErrorAction Stop
    $levels=@{1='Critical';2='Error';3='Warning';4='Information';5='Verbose'}
    foreach($level in 1..5){
      $n=($events | Where-Object {$_.LevelDisplayName -eq $levels[$level]}).Count
      $out += [pscustomobject]@{Log=$log;Level=$levels[$level];Count=$n;WindowHours=24}
    }
  }catch{
    $out += [pscustomobject]@{Log=$log;Level='Unavailable';Count=0;WindowHours=24}
  }
}
$out | ConvertTo-Json -Compress
"""
    return _json(script, 25)


def advanced_telemetry() -> dict[str, Any]:
    return {
        "battery": battery(),
        "security_products": security_products(),
        "update_services": update_services(),
        "time_sync": time_sync(),
        "power_capabilities": power_capabilities(),
        "reliability_events": reliability_events(),
        "event_counts_24h": event_counts(),
    }
