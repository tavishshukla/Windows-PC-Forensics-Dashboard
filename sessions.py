from collector import _ps_json

def logged_on_sessions():
    script = r'''
try {
  Get-CimInstance Win32_LoggedOnUser | ForEach-Object {
    $a=$_.Antecedent
    $d=$_.Dependent
    [pscustomobject]@{
      Account=[string]$a
      Session=[string]$d
    }
  } | Select -First 100 | ConvertTo-Json -Compress
} catch {}
'''
    value = _ps_json(script, [])
    if isinstance(value, dict):
        return [value]
    return value
