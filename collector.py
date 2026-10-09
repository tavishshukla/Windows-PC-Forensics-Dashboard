import os,platform,socket,time
from datetime import datetime
import psutil
def snapshot():
    vm=psutil.virtual_memory(); io=psutil.net_io_counters()
    procs=[]
    for p in psutil.process_iter(["pid","ppid","name","username","status","exe","memory_info"]):
        try:
            i=p.info;m=i.get("memory_info")
            procs.append({"pid":i["pid"],"ppid":i.get("ppid"),"name":i.get("name"),"user":i.get("username"),"status":i.get("status"),"exe":i.get("exe"),"ram_mb":round((m.rss if m else 0)/1048576,1)})
        except (psutil.NoSuchProcess,psutil.AccessDenied): pass
    procs.sort(key=lambda x:x["ram_mb"],reverse=True)
    conns=[]
    for c in psutil.net_connections("inet"):
        try:
            conns.append({"pid":c.pid,"local":str(c.laddr),"remote":str(c.raddr) if c.raddr else "","status":c.status})
        except (psutil.NoSuchProcess,psutil.AccessDenied): pass
    return {"time":datetime.now().isoformat(timespec="seconds"),"host":socket.gethostname(),"os":platform.platform(),"cpu":psutil.cpu_percent(.1),"memory":vm.percent,"memory_total":vm.total,"disk":psutil.disk_usage(os.environ.get("SystemDrive","C:")+"\\").percent,"processes":procs[:100],"connections":conns[:200],"network":{"sent":io.bytes_sent,"received":io.bytes_recv},"uptime":time.time()-psutil.boot_time()}
