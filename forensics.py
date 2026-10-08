from datetime import datetime

def build_findings(snapshot, changes):
    findings = []
    now = snapshot.get("time") or datetime.now().isoformat(timespec="seconds")

    for p in changes.get("new_processes", []):
        name = str(p.get("name") or "unknown")
        exe = str(p.get("exe") or "")
        if "\\temp\\" in exe.lower() or "\\appdata\\local\\temp\\" in exe.lower():
            findings.append({"time": now, "severity": "high", "type": "process", "title": "New process from temporary path", "detail": f"{name} started from {exe}"})
        else:
            findings.append({"time": now, "severity": "info", "type": "process", "title": "New process", "detail": f"{name} (PID {p.get('pid')}) started"})

    for c in changes.get("new_connections", []):
        remote = str(c.get("remote") or "")
        if remote:
            findings.append({"time": now, "severity": "info", "type": "network", "title": "New network connection", "detail": f"PID {c.get('pid')} -> {remote}"})

    for s in changes.get("service_changes", []):
        findings.append({"time": now, "severity": "medium", "type": "service", "title": "Service state changed", "detail": f"{s.get('name')}: {s.get('old')} -> {s.get('new')}"})

    return findings
