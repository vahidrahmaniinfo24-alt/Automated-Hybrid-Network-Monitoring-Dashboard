import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

DC_IP = "192.168.100.10"
MAX_WORKERS = 6


def run_powershell(script, timeout=12):
    try:
        return subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return None


def discover_ad_computers():
    script = rf'''
$cred = Import-Clixml "$env:USERPROFILE\kurs-monitor-cred.xml"

Invoke-Command -ComputerName {DC_IP} -Credential $cred -ScriptBlock {{
    Get-ADComputer -Filter * |
    Select-Object Name,DNSHostName |
    ConvertTo-Json -Compress
}}
'''

    result = run_powershell(script, timeout=15)

    if not result or result.returncode != 0:
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    return [data] if isinstance(data, dict) else data


def resolve_ip(hostname):
    if not hostname:
        return None

    try:
        result = subprocess.run(
            ["nslookup", hostname, DC_IP],
            capture_output=True,
            text=True,
            timeout=4
        )
    except subprocess.TimeoutExpired:
        return None

    addresses = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        result.stdout
    )

    for ip in reversed(addresses):
        if ip != DC_IP or hostname.lower().startswith("server-dc"):
            return ip

    return None


def ping_device(ip):
    if not ip:
        return False

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True,
            timeout=3
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def device_type(name):
    name = name.upper()

    if name.startswith("CLI"):
        return "Client"

    if "DC" in name:
        return "Domain Controller"

    return "Server"


def get_remote_metrics(ip):
    if not ip:
        return None

    ps_script = rf'''
$cred = Import-Clixml "$env:USERPROFILE\kurs-monitor-cred.xml"

Invoke-Command -ComputerName {ip} -Credential $cred -ScriptBlock {{
    $os = Get-CimInstance Win32_OperatingSystem
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"

    [PSCustomObject]@{{
        CPUPercent = [math]::Round(
            (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue,
            1
        )

        RAMUsedPercent = [math]::Round(
            (1 - ($os.FreePhysicalMemory / $os.TotalVisibleMemorySize)) * 100,
            1
        )

        DiskUsedPercent = [math]::Round(
            (1 - ($disk.FreeSpace / $disk.Size)) * 100,
            1
        )

        UptimeHours = [math]::Round(
            ((Get-Date) - $os.LastBootUpTime).TotalHours,
            1
        )
    }} | ConvertTo-Json -Compress
}}
'''

    result = run_powershell(ps_script, timeout=10)

    if not result or result.returncode != 0:
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def collect_one_device(computer):
    name = computer.get("Name")
    hostname = computer.get("DNSHostName")

    ip = resolve_ip(hostname)
    online = ping_device(ip)

    metrics = get_remote_metrics(ip) if online else None

    return {
        "name": name,
        "hostname": hostname,
        "ip": ip or "Unknown",
        "type": device_type(name),
        "online": online,
        "cpu": metrics.get("CPUPercent") if metrics else None,
        "ram": metrics.get("RAMUsedPercent") if metrics else None,
        "disk": metrics.get("DiskUsedPercent") if metrics else None,
        "uptime": metrics.get("UptimeHours") if metrics else None,
    }


def collect_status():
    computers = discover_ad_computers()

    if not computers:
        return []

    devices = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(collect_one_device, computer)
            for computer in computers
        ]

        for future in as_completed(futures):
            try:
                devices.append(future.result())
            except Exception:
                pass

    devices.sort(key=lambda d: d["name"])

    return devices


if __name__ == "__main__":
    print(
        json.dumps(
            collect_status(),
            indent=2
        )
    )