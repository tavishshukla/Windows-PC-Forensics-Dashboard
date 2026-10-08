from collections import Counter

_previous = None


def _key_process(p):
    return (p.get("pid"), p.get("name"))


def _key_connection(c):
    return (c.get("pid"), c.get("local"), c.get("remote"), c.get("status"))


def _key_service(s):
    return s.get("Name")


def compare(current):
    global _previous
    if _previous is None:
        _previous = current
        return {"initialized": True, "new_processes": [], "ended_processes": [],
                "new_connections": [], "ended_connections": [], "service_changes": [],
                "new_startup_items": [], "ended_startup_items": []}

    old = _previous
    old_p = {_key_process(x): x for x in old.get("processes", [])}
    new_p = {_key_process(x): x for x in current.get("processes", [])}
    old_c = {_key_connection(x): x for x in old.get("connections", [])}
    new_c = {_key_connection(x): x for x in current.get("connections", [])}

    old_s = {_key_service(x): x for x in old.get("services", []) if x.get("Name")}
    new_s = {_key_service(x): x for x in current.get("services", []) if x.get("Name")}

    old_start = {(x.get("Location"), x.get("Name"), x.get("Command")) for x in old.get("startup", [])}
    new_start = {(x.get("Location"), x.get("Name"), x.get("Command")) for x in current.get("startup", [])}

    service_changes = []
    for name in sorted(set(old_s) & set(new_s)):
        if old_s[name].get("Status") != new_s[name].get("Status"):
            service_changes.append({
                "name": name,
                "old": old_s[name].get("Status"),
                "new": new_s[name].get("Status"),
            })

    result = {
        "initialized": False,
        "new_processes": list(new_p.values())[:50],
        "ended_processes": list(old_p.values())[:50],
        "new_connections": list(new_c.values())[:100],
        "ended_connections": list(old_c.values())[:100],
        "service_changes": service_changes[:100],
        "new_startup_items": [dict(zip(("Location","Name","Command"), x)) for x in (new_start-old_start)][:50],
        "ended_startup_items": [dict(zip(("Location","Name","Command"), x)) for x in (old_start-new_start)][:50],
    }
    result["new_processes"] = [v for k,v in new_p.items() if k not in old_p][:50]
    result["ended_processes"] = [v for k,v in old_p.items() if k not in new_p][:50]
    result["new_connections"] = [v for k,v in new_c.items() if k not in old_c][:100]
    result["ended_connections"] = [v for k,v in old_c.items() if k not in new_c][:100]
    _previous = current
    return result
