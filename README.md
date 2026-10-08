# Windows PC Forensics Dashboard

A local, read-only Windows telemetry and PC forensics dashboard built with Python, Flask, and psutil.

## What it tracks

- CPU usage, physical/logical CPU counts, RAM, disk usage, uptime
- Windows version/build, motherboard/system manufacturer and model
- BIOS vendor and BIOS version
- GPU names and driver versions when Windows exposes them
- Processes: PID, parent PID, user, status, RAM, executable path, start time
- Active network connections: PID, local/remote endpoints, address family, TCP state
- Network byte counters
- Disk partitions, capacity, free space, and utilization
- Windows services and their start types
- Registry startup / Run / RunOnce entries
- Recent System, Application, and Security event-log summaries when accessible
- Microsoft Defender status when available
- Windows Firewall profile status when available
- Live changes between scans: process starts/exits, connection changes, service changes, and startup changes

## Safety

This project is intentionally **read-only**. It does not kill processes, modify the firewall, change registry values, collect passwords, keylog, access webcams/microphones, or execute commands supplied by network clients.

The dashboard binds to `127.0.0.1` so the telemetry stays local to the machine running it.

Some Windows telemetry requires appropriate permissions. If a Windows API or event log cannot be read, the dashboard reports that data as unavailable instead of trying to bypass permissions.

## Setup

Install Python 3.11+ and Git, then:

~~~text
git clone https://github.com/tavishshukla/Windows-PC-Forensics-Dashboard.git
cd Windows-PC-Forensics-Dashboard
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

Start the dashboard:

~~~text
python app.py
~~~

Open:

~~~text
http://127.0.0.1:5000
~~~

## API

- `/api/health` — health/read-only status
- `/api/snapshot` — full current telemetry snapshot
- `/api/changes` — changes detected since the previous tracking scan

## Tests

~~~text
python -m pytest
~~~

## Notes

This is a local observability/forensics project, not an antivirus replacement or a guarantee that a machine is secure. Telemetry visibility depends on Windows permissions and which providers are installed.
