from collector import _ps_json

def scheduled_tasks():
    script = r'''
try {
  Get-ScheduledTask | Select TaskName,TaskPath,State,Author,Description |
    Select -First 300 | ConvertTo-Json -Compress
} catch {}
'''
    value = _ps_json(script, [])
    if isinstance(value, dict):
        return [value]
    return value
