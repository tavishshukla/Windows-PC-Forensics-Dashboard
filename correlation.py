def correlate_process_network(snapshot):
    by_pid = {p.get("pid"): p for p in snapshot.get("processes", [])}
    rows = []
    for c in snapshot.get("connections", []):
        p = by_pid.get(c.get("pid"))
        rows.append({
            "pid": c.get("pid"),
            "process": p.get("name") if p else None,
            "exe": p.get("exe") if p else None,
            "user": p.get("user") if p else None,
            "local": c.get("local"),
            "remote": c.get("remote"),
            "status": c.get("status"),
        })
    return rows
