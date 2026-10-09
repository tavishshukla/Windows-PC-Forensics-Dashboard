import os
import platform
from collector import _ps_json

def _list(script, default=None):
    value = _ps_json(script, default or [])
    if isinstance(value, dict):
        return [value]
    return value if isinstance(value, list) else (default or [])

def inventory():
    return {
        "computer": _list("(Get-CimInstance Win32_ComputerSystem | Select Name,Manufacturer,Model,Domain,PartOfDomain,TotalPhysicalMemory,NumberOfLogicalProcessors | ConvertTo-Json -Compress)", {}),
        "cpu": _list("(Get-CimInstance Win32_Processor | Select Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,CurrentClockSpeed,Architecture,SocketDesignation | ConvertTo-Json -Compress)", {}),
        "memory_modules": _list("(Get-CimInstance Win32_PhysicalMemory | Select Manufacturer,PartNumber,Capacity,Speed,SerialNumber,DeviceLocator | ConvertTo-Json -Compress)", []),
        "motherboard": _list("(Get-CimInstance Win32_BaseBoard | Select Manufacturer,Product,Version,SerialNumber | ConvertTo-Json -Compress)", {}),
        "bios_detail": _list("(Get-CimInstance Win32_BIOS | Select Manufacturer,Name,SMBIOSBIOSVersion,SerialNumber,ReleaseDate,Version | ConvertTo-Json -Compress)", {}),
        "gpu_detail": _list("(Get-CimInstance Win32_VideoController | Select Name,AdapterCompatibility,DriverVersion,DriverDate,VideoModeDescription,CurrentHorizontalResolution,CurrentVerticalResolution,AdapterRAM | ConvertTo-Json -Compress)", []),
        "disks": _list("(Get-CimInstance Win32_DiskDrive | Select Model,InterfaceType,MediaType,Size,FirmwareRevision,SerialNumber,Partitions | ConvertTo-Json -Compress)", []),
        "volumes": _list("(Get-CimInstance Win32_LogicalDisk | Select DeviceID,VolumeName,FileSystem,Size,FreeSpace,DriveType | ConvertTo-Json -Compress)", []),
        "network_adapters": _list("(Get-NetAdapter -ErrorAction SilentlyContinue | Select Name,InterfaceDescription,Status,LinkSpeed,MacAddress,Virtual | ConvertTo-Json -Compress)", []),
        "ip_config": _list("(Get-NetIPConfiguration -ErrorAction SilentlyContinue | Select InterfaceAlias,IPv4Address,IPv6Address,DNSServer,IPv4DefaultGateway | ConvertTo-Json -Compress)", []),
        "routes": _list("(Get-NetRoute -ErrorAction SilentlyContinue | Select DestinationPrefix,NextHop,InterfaceAlias,RouteMetric,State | ConvertTo-Json -Compress)", []),
        "arp": _list("(Get-NetNeighbor -ErrorAction SilentlyContinue | Select IPAddress,LinkLayerAddress,State,InterfaceAlias | ConvertTo-Json -Compress)", []),
        "users": _list("(Get-CimInstance Win32_UserAccount | Select Name,Domain,LocalAccount,Disabled,Lockout,PasswordRequired,PasswordExpires | ConvertTo-Json -Compress)", []),
        "local_groups": _list("(Get-LocalGroup -ErrorAction SilentlyContinue | Select Name,Description,SID | ConvertTo-Json -Compress)", []),
        "installed_software": _list("(Get-ItemProperty 'HKLM:\\\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKCU:\\\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | Where-Object DisplayName | Select DisplayName,DisplayVersion,Publisher,InstallDate,InstallLocation | Sort-Object DisplayName | ConvertTo-Json -Compress)", []),
        "hotfixes": _list("(Get-HotFix | Select HotFixID,Description,InstalledOn,InstalledBy | Sort-Object InstalledOn -Descending | ConvertTo-Json -Compress)", []),
        "drivers": _list("(Get-CimInstance Win32_PnPSignedDriver | Where-Object DeviceName | Select DeviceName,DriverVersion,DriverDate,Manufacturer,InfName,Signer | ConvertTo-Json -Compress)", []),
        "printers": _list("(Get-CimInstance Win32_Printer | Select Name,DriverName,PortName,Network,Default,PrinterStatus | ConvertTo-Json -Compress)", []),
        "usb_devices": _list("(Get-CimInstance Win32_PnPEntity | Where-Object {$_.PNPDeviceID -like 'USB*'} | Select Name,Manufacturer,Status,PNPDeviceID | ConvertTo-Json -Compress)", []),
        "environment": {k:v for k,v in os.environ.items() if k.upper() in {"COMPUTERNAME","USERNAME","USERDOMAIN","USERPROFILE","SYSTEMROOT","WINDIR","TEMP","TMP","PROCESSOR_ARCHITECTURE","NUMBER_OF_PROCESSORS","PROGRAMDATA","PROGRAMFILES"}},
        "python": {"version":platform.python_version(),"implementation":platform.python_implementation(),"executable":os.path.abspath(os.sys.executable)},
    }
