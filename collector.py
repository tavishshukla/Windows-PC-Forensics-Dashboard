import os
import platform
import socket
import subprocess
import time
from datetime import datetime

import psutil


def _powershell(script):
    if os.name != "nt":
        return None
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True, text=True, timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if p.returncode != 0:
            return None
        return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _ps_json(script, default):
    import json
    out = _powershell(script)
    if not out:
        return default
    try:
        value = json.loads(out)
        return value if value is not None else default
    except json.JSONDecodeError:
        return default


def windows_info():
    data = {
        "manufacturer": None, "model": None, "bios": None,
        "bios_version": None, "windows_version": platform.version(),
        "build": None, "gpu": [], "defender": None, "firewall": [],
    }
    cs = _ps_json("(Get-CimInstance Win32_ComputerSystem | Select Manufacturer,Model | ConvertTo-Json -Compress)", {})
    bios = _ps_json("(Get-CimInstance Win32_BIOS | Select Manufacturer,SMBIOSBIOSVersion,ReleaseDate | ConvertTo-Json -Compress)", {})
    osinfo = _ps_json("(Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber,LastBootUpTime | ConvertTo-Json -Compress)", {})
    gpu = _ps_json("(Get-CimInstance Win32_VideoController | Select Name,DriverVersion,AdapterRAM | ConvertTo-Json -Compress)", [])
    if isinstance(gpu, dict): gpu = [gpu]
    data.update({
        "manufacturer": cs.get("Manufacturer"),
        "model": cs.get("Model"),
        "bios": bios.get("Manufacturer"),
        "bios_version": bios.get("SMBIOSBIOSVersion"),
        "windows_version": osinfo.get("Caption") or data["windows_version"],
        "build": osinfo.get("BuildNumber"),
        "gpu": gpu,
    })
    defender = _ps_json("(Get-MpComputerStatus | Select AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated | ConvertTo-Json -Compress)", None)
    data["defender"] = defender
    firewall = _ps_json("(Get-NetFirewallProfile | Select Name,Enabled,DefaultInboundAction,DefaultOutboundAction | ConvertTo-Json -Compress)", [])
    data["firewall"] = firewall if isinstance(firewall, list) else ([firewall] if firewall else [])
    return data


def services():
    value = _ps_json("(Get-Service | Select Name,DisplayName,Status,StartType | ConvertTo-Json -Compress)", [])
    if isinstance(value, dict): value = [value]
    return value[:250]


def startup_items():
    script = r'''
$items=@()
$paths=@(
'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
)
foreach($path in $paths){
  if(Test-Path $path){
    $p=Get-ItemProperty $path
    foreach($prop in $p.PSObject.Properties){
      if($prop.Name -notmatch '^PS'){
        $items += [pscustomobject]@{Location=$path;Name=$prop.Name;Command=[string]$prop.Value}
      }
    }
  }
}
$items | ConvertTo-Json -Compress
'''
    value = _ps_json(script, [])
    if isinstance(value, dict): value = [value]
    return value


def event_summary():
    script = r'''
$logs=@('System','Application','Security')
$out=@()
foreach($log in $logs){
  try {
    Get-WinEvent -LogName $log -MaxEvents 20 -ErrorAction Stop |
      Select TimeCreated,Id,LevelDisplayName,ProviderName,Message |
      ForEach-Object {
        [pscustomobject]@{
          Log=$log;Time=$_.TimeCreated;Id=$_.Id;Level=$_.LevelDisplayName;
          Provider=$_.ProviderName;Message=([string]$_.Message).Substring(0,[Math]::Min(180,([string]$_.Message).Length))
        }
      } | ForEach-Object {$out += $_}
  } catch {}
}
$out | ConvertTo-Json -Compress
'''
    value = _ps_json(script, [])
    if isinstance(value, dict): value = [value]
    return value[:60]


def snapshot():
    vm = psutil.virtual_memory()
    io = psutil.net_io_counters()
    disk_path = os.environ.get("SystemDrive", "C:") + "\\"
    procs = []
    for p in psutil.process_iter(["pid", "ppid", "name", "username", "status", "exe", "memory_info", "create_time"]):
        try:
            i = p.info
            m = i.get("memory_info")
            procs.append({
                "pid": i["pid"], "ppid": i.get("ppid"), "name": i.get("name"),
                "user": i.get("username"), "status": i.get("status"),
                "exe": i.get("exe"), "ram_mb": round((m.rss if m else 0) / 1048576, 1),
                "started": datetime.fromtimestamp(i["create_time"]).isoformat(timespec="seconds") if i.get("create_time") else None,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
    procs.sort(key=lambda x: x["ram_mb"], reverse=True)

    conns = []
    for c in psutil.net_connections("inet"):
        try:
            conns.append({
                "pid": c.pid, "local": str(c.laddr), "remote": str(c.raddr) if c.raddr else "",
                "status": c.status, "family": str(c.family).split(".")[-1],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({"device": part.device, "mount": part.mountpoint, "fstype": part.fstype,
                               "total": usage.total, "used": usage.used, "free": usage.free,
                               "percent": usage.percent})
        except (OSError, PermissionError):
            pass

    try:
        freq = psutil.cpu_freq()
        cpu_frequency = {
            "current_mhz": round(freq.current, 1) if freq else None,
            "min_mhz": round(freq.min, 1) if freq else None,
            "max_mhz": round(freq.max, 1) if freq else None,
        }
    except (AttributeError, OSError):
        cpu_frequency = {"current_mhz": None, "min_mhz": None, "max_mhz": None}

    try:
        battery = psutil.sensors_battery()
        battery_info = {
            "percent": battery.percent if battery else None,
            "plugged": battery.power_plugged if battery else None,
            "seconds_left": battery.secsleft if battery else None,
        }
    except (AttributeError, OSError):
        battery_info = {"percent": None, "plugged": None, "seconds_left": None}

    try:
        disk_io = psutil.disk_io_counters()
        disk_activity = {
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0,
            "read_count": disk_io.read_count if disk_io else 0,
            "write_count": disk_io.write_count if disk_io else 0,
        }
    except (AttributeError, OSError):
        disk_activity = {"read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0}

    return {
        "time": datetime.now().isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "os": platform.platform(),
        "cpu": psutil.cpu_percent(.1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "cpu_frequency": cpu_frequency,
        "memory": vm.percent,
        "memory_total": vm.total,
        "memory_available": vm.available,
        "disk": psutil.disk_usage(disk_path).percent,
        "processes": procs[:150],
        "connections": conns[:300],
        "network": {"sent": io.bytes_sent, "received": io.bytes_recv},
        "disk_activity": disk_activity,
        "partitions": partitions,
        "battery": battery_info,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(timespec="seconds"),
        "uptime": time.time() - psutil.boot_time(),
        "windows": windows_info(),
        "services": services(),
        "startup": startup_items(),
        "events": event_summary(),
    }
