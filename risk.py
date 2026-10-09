import os


def assess(snapshot):
    score = 0
    findings = []
    windows = snapshot.get("windows") or {}
    defender = windows.get("defender") or {}

    if defender.get("AntivirusEnabled") is False:
        score += 30
        findings.append({"severity": "high", "reason": "Windows antivirus is reported disabled."})
    if defender.get("RealTimeProtectionEnabled") is False:
        score += 25
        findings.append({"severity": "high", "reason": "Real-time protection is reported disabled."})

    firewall = windows.get("firewall") or []
    disabled = [x.get("Name") for x in firewall if x.get("Enabled") is False]
    if disabled:
        score += min(30, 10 * len(disabled))
        findings.append({"severity": "medium", "reason": "Firewall profiles reported disabled: " + ", ".join(map(str, disabled))})

    startup = snapshot.get("startup") or []
    temp_like = []
    for item in startup:
        command = str(item.get("Command") or "").lower()
        if "\temp\" in command or "\appdata\local\temp\" in command:
            temp_like.append(item.get("Name"))
    if temp_like:
        score += min(20, 5 * len(temp_like))
        findings.append({"severity": "medium", "reason": "Startup entries reference temporary directories."})

    score = min(score, 100)
    label = "low" if score < 25 else "moderate" if score < 50 else "high" if score < 75 else "critical"
    return {"score": score, "level": label, "findings": findings}
