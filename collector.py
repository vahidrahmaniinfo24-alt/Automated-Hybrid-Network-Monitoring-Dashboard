import json
import os
import re
import subprocess
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


DC_IP = "192.168.100.10"
MAX_WORKERS = 6

RENDER_URL = os.getenv(
    "MONITOR_RENDER_URL",
    ""
).rstrip("/")

API_KEY = os.getenv(
    "MONITOR_API_KEY",
    ""
)


def run_powershell(script, timeout=12):
    try:
        return subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
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

    result = run_powershell(
        script,
        timeout=15,
    )

    if (
        not result
        or result.returncode != 0
    ):
        print("AD discovery failed.")

        if result:
            print(result.stderr)

        return []

    try:
        data = json.loads(
            result.stdout
        )
    except json.JSONDecodeError:
        print("AD discovery returned invalid JSON.")
        return []

    if isinstance(data, dict):
        return [data]

    return data


def resolve_ip(hostname):
    if not hostname:
        return None

    try:
        result = subprocess.run(
            [
                "nslookup",
                hostname,
                DC_IP,
            ],
            capture_output=True,
            text=True,
            timeout=4,
        )
    except subprocess.TimeoutExpired:
        return None

    addresses = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        result.stdout,
    )

    for ip in reversed(addresses):
        if (
            ip != DC_IP
            or hostname.lower().startswith(
                "server-dc"
            )
        ):
            return ip

    return None


def ping_device(ip):
    if not ip:
        return False

    try:
        result = subprocess.run(
            [
                "ping",
                "-n",
                "1",
                "-w",
                "1000",
                ip,
            ],
            capture_output=True,
            timeout=3,
        )

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False


def device_type(name):
    upper = name.upper()

    if upper.startswith("CLI"):
        return "Client"

    if "DC" in upper:
        return "Domain Controller"

    return "Server"


def get_remote_metrics(ip):
    if not ip:
        return None

    script = rf'''
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
    }} |
    ConvertTo-Json -Compress
}}
'''

    result = run_powershell(
        script,
        timeout=10,
    )

    if (
        not result
        or result.returncode != 0
    ):
        return None

    try:
        return json.loads(
            result.stdout
        )
    except json.JSONDecodeError:
        return None


def collect_one_device(computer):
    name = computer.get("Name")
    hostname = computer.get(
        "DNSHostName"
    )

    ip = resolve_ip(
        hostname
    )

    online = ping_device(
        ip
    )

    metrics = (
        get_remote_metrics(ip)
        if online
        else None
    )

    return {
        "name": name,
        "hostname": hostname,
        "ip": ip or "Unknown",
        "type": device_type(name),
        "online": online,
        "cpu": (
            metrics.get("CPUPercent")
            if metrics
            else None
        ),
        "ram": (
            metrics.get("RAMUsedPercent")
            if metrics
            else None
        ),
        "disk": (
            metrics.get("DiskUsedPercent")
            if metrics
            else None
        ),
        "uptime": (
            metrics.get("UptimeHours")
            if metrics
            else None
        ),
    }


def collect_status():
    computers = discover_ad_computers()

    if not computers:
        return []

    devices = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                collect_one_device,
                computer,
            )
            for computer in computers
        ]

        for future in as_completed(
            futures
        ):
            try:
                devices.append(
                    future.result()
                )
            except Exception as exc:
                print(
                    "Device collection error:",
                    exc,
                )

    devices.sort(
        key=lambda device:
            device["name"]
    )

    return devices


def push_to_render(devices):
    if not RENDER_URL:
        print(
            "MONITOR_RENDER_URL "
            "is not configured."
        )
        return False

    if not API_KEY:
        print(
            "MONITOR_API_KEY "
            "is not configured."
        )
        return False

    url = (
        f"{RENDER_URL}/api/ingest"
    )

    try:
        response = requests.post(
            url,
            json={
                "devices": devices
            },
            headers={
                "X-API-Key": API_KEY
            },
            timeout=20,
        )

        response.raise_for_status()

        print(
            "Cloud update OK:",
            response.json(),
        )

        return True

    except requests.RequestException as exc:
        print(
            "Cloud push failed:",
            exc,
        )
        return False


def run_once():
    print(
        "\nCollecting infrastructure..."
    )

    devices = collect_status()

    print(
        json.dumps(
            devices,
            indent=2,
        )
    )

    push_to_render(
        devices
    )


def run_forever():
    while True:
        try:
            run_once()

        except KeyboardInterrupt:
            print(
                "\nCollector stopped."
            )
            break

        except Exception as exc:
            print(
                "Collector cycle failed:",
                exc,
            )

        print(
            "Waiting 30 seconds..."
        )

        time.sleep(30)


if __name__ == "__main__":
    run_forever()