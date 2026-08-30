import os

from datetime import datetime, timezone
from threading import Lock

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI(
    title="Automated Hybrid Network Monitoring Dashboard"
)


API_KEY = os.getenv(
    "MONITOR_API_KEY",
    ""
)


latest_devices = []
latest_update = None

data_lock = Lock()


class MetricsPayload(BaseModel):
    devices: list[dict]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "hybrid-monitor",
    }


@app.post("/api/ingest")
def ingest_metrics(
    payload: MetricsPayload,
    x_api_key: str | None = Header(
        default=None
    ),
):
    global latest_devices
    global latest_update

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "MONITOR_API_KEY "
                "is not configured"
            ),
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    with data_lock:
        latest_devices = (
            payload.devices
        )

        latest_update = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    return {
        "status": "accepted",
        "device_count": len(
            payload.devices
        ),
        "updated_at": latest_update,
    }


@app.get("/api/devices")
def api_devices():
    with data_lock:
        return {
            "devices":
                latest_devices,

            "updated_at":
                latest_update,
        }


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Automated Hybrid Network Monitoring Dashboard
</title>

<style>

:root {
    --bg: #050b14;

    --panel:
        rgba(14, 29, 48, 0.72);

    --border:
        rgba(80, 190, 255, 0.18);

    --text: #eef8ff;

    --muted: #88a3ba;

    --blue: #38bdf8;

    --green: #22c55e;

    --yellow: #facc15;

    --red: #ef4444;

    --purple: #a855f7;
}


* {
    box-sizing: border-box;
}


body {
    margin: 0;

    min-height: 100vh;

    font-family:
        Inter,
        Segoe UI,
        Arial,
        sans-serif;

    color: var(--text);

    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(
                14,
                165,
                233,
                .14
            ),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 5%,
            rgba(
                168,
                85,
                247,
                .08
            ),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #040912,
            #071220,
            #081829
        );
}


.app {
    display: grid;

    grid-template-columns:
        240px 1fr;

    min-height: 100vh;
}


.sidebar {
    padding:
        24px 18px;

    background:
        rgba(
            3,
            10,
            20,
            .80
        );

    border-right:
        1px solid
        var(--border);

    backdrop-filter:
        blur(20px);

    display: flex;

    flex-direction:
        column;
}


.brand {
    padding:
        8px 8px 24px;

    border-bottom:
        1px solid
        var(--border);
}


.brand h2 {
    margin: 0;

    font-size: 17px;

    line-height: 1.4;
}


.domain {
    margin-top: 8px;

    color: var(--blue);

    font-size: 12px;

    letter-spacing: 1px;
}


.menu {
    margin-top: 22px;

    display: grid;

    gap: 8px;
}


.menu-item {
    padding: 12px 14px;

    border-radius: 10px;

    color: var(--muted);
}


.menu-item.active {
    color: white;

    border:
        1px solid
        rgba(
            56,
            189,
            248,
            .28
        );

    background:
        rgba(
            56,
            189,
            248,
            .08
        );
}


.sidebar-bottom {
    margin-top: auto;

    padding: 15px;

    border:
        1px solid
        var(--border);

    border-radius: 12px;

    background:
        var(--panel);
}


.sidebar-row {
    display: flex;

    justify-content:
        space-between;

    margin: 8px 0;

    font-size: 12px;

    color: var(--muted);
}


main {
    padding: 28px;
}


.topbar {
    display: flex;

    justify-content:
        space-between;

    align-items:
        center;

    margin-bottom: 22px;
}


h1 {
    margin: 0;

    font-size: 26px;
}


.subtitle {
    margin-top: 7px;

    color: var(--muted);

    font-size: 13px;
}


.live {
    display: flex;

    align-items:
        center;

    gap: 8px;

    padding:
        8px 12px;

    border:
        1px solid
        rgba(
            34,
            197,
            94,
            .25
        );

    border-radius:
        999px;

    color:
        #8df0aa;

    background:
        rgba(
            34,
            197,
            94,
            .06
        );

    font-size: 12px;
}


.live-dot {
    width: 8px;

    height: 8px;

    border-radius:
        50%;

    background:
        var(--green);

    box-shadow:
        0 0 12px
        var(--green);
}


.cards {
    display: grid;

    grid-template-columns:
        repeat(
            5,
            1fr
        );

    gap: 14px;

    margin-bottom:
        16px;
}


.card,
.metric,
.table-panel,
.info {
    border:
        1px solid
        var(--border);

    background:
        var(--panel);

    backdrop-filter:
        blur(18px);

    border-radius:
        14px;

    box-shadow:
        0 10px 35px
        rgba(
            0,
            0,
            0,
            .15
        );
}


.card {
    padding: 18px;
}


.label {
    color:
        var(--muted);

    font-size: 11px;

    text-transform:
        uppercase;

    letter-spacing:
        .7px;
}


.value {
    margin-top: 8px;

    font-size: 30px;

    font-weight: 700;
}


.small {
    margin-top: 5px;

    font-size: 11px;

    color:
        var(--muted);
}


.metrics {
    display: grid;

    grid-template-columns:
        repeat(
            3,
            1fr
        );

    gap: 14px;

    margin-bottom:
        16px;
}


.metric {
    padding: 18px;
}


.metric-value {
    font-size: 28px;

    font-weight: 700;
}


.progress {
    margin-top: 15px;

    height: 7px;

    border-radius:
        999px;

    overflow: hidden;

    background:
        rgba(
            255,
            255,
            255,
            .06
        );
}


.fill {
    height: 100%;

    background:
        linear-gradient(
            90deg,
            #0ea5e9,
            #67e8f9
        );

    box-shadow:
        0 0 12px
        rgba(
            56,
            189,
            248,
            .35
        );
}


#collectorWarning {
    display: none;

    margin-bottom:
        16px;

    padding:
        12px 15px;

    border:
        1px solid
        rgba(
            250,
            204,
            21,
            .25
        );

    border-radius:
        10px;

    color:
        #fde68a;

    background:
        rgba(
            250,
            204,
            21,
            .06
        );
}


.table-panel {
    overflow: hidden;
}


.table-header {
    padding:
        17px 18px;

    display: flex;

    justify-content:
        space-between;

    border-bottom:
        1px solid
        var(--border);
}


.table-wrap {
    overflow-x: auto;
}


table {
    width: 100%;

    border-collapse:
        collapse;

    min-width:
        1000px;
}


th {
    padding:
        13px 15px;

    text-align: left;

    color:
        #8299b1;

    font-size: 10px;

    letter-spacing:
        .6px;

    text-transform:
        uppercase;
}


td {
    padding: 15px;

    border-top:
        1px solid
        rgba(
            100,
            190,
            255,
            .07
        );

    font-size: 13px;
}


tr:hover td {
    background:
        rgba(
            56,
            189,
            248,
            .025
        );
}


.device-name {
    font-weight: 600;

    color:
        #dff6ff;
}


.online {
    color:
        #69df8b;
}


.offline {
    color:
        #ff7474;
}


.role {
    display:
        inline-block;

    padding:
        5px 8px;

    border-radius:
        6px;

    font-size:
        10px;

    color:
        #d8b6ff;

    background:
        rgba(
            168,
            85,
            247,
            .09
        );

    border:
        1px solid
        rgba(
            168,
            85,
            247,
            .20
        );
}


.role.client {
    color:
        #9bdcff;

    background:
        rgba(
            56,
            189,
            248,
            .08
        );

    border-color:
        rgba(
            56,
            189,
            248,
            .20
        );
}


.bottom {
    margin-top:
        16px;

    display: grid;

    grid-template-columns:
        repeat(
            4,
            1fr
        );

    gap: 14px;
}


.info {
    padding: 16px;
}


.info-title {
    color:
        var(--blue);

    font-size:
        11px;

    font-weight:
        600;
}


.info-body {
    margin-top:
        8px;

    color:
        #d5e6f3;

    font-size:
        12px;

    line-height:
        1.6;
}


@media(
    max-width:
    1100px
) {

    .app {
        grid-template-columns:
            1fr;
    }

    .sidebar {
        display: none;
    }

    .cards {
        grid-template-columns:
            repeat(
                2,
                1fr
            );
    }

}


@media(
    max-width:
    700px
) {

    main {
        padding: 15px;
    }

    .cards,
    .metrics,
    .bottom {
        grid-template-columns:
            1fr;
    }

}

</style>

</head>


<body>


<div class="app">


<aside class="sidebar">


<div class="brand">

<h2>
Windows Infrastructure Monitor
</h2>

<div class="domain">
KURS.INTERN
</div>

</div>


<div class="menu">

<div class="menu-item active">
Dashboard
</div>

<div class="menu-item">
Devices
</div>

<div class="menu-item">
Active Directory
</div>

<div class="menu-item">
Performance
</div>

<div class="menu-item">
Alerts
</div>

<div class="menu-item">
Reports
</div>

</div>


<div class="sidebar-bottom">

<div class="sidebar-row">

<span>
Cloud API
</span>

<span
    style="
        color:#69df8b;
    "
>
Online
</span>

</div>


<div class="sidebar-row">

<span>
Domain
</span>

<span>
kurs.intern
</span>

</div>


<div class="sidebar-row">

<span>
Refresh
</span>

<span>
10 sec
</span>

</div>

</div>


</aside>


<main>


<div class="topbar">


<div>

<h1>
Automated Hybrid Network Monitoring Dashboard
</h1>

<div class="subtitle">
Real-time Windows Infrastructure Monitoring
</div>

</div>


<div class="live">

<span class="live-dot">
</span>

LIVE

</div>


</div>


<div id="collectorWarning">

Waiting for the local collector to send monitoring data.

</div>


<section class="cards">


<div class="card">

<div class="label">
Total Devices
</div>

<div
    class="value"
    id="total"
>
0
</div>

<div class="small">
Active Directory
</div>

</div>


<div class="card">

<div class="label">
Online
</div>

<div
    class="value"
    id="online"
>
0
</div>

<div
    class="small"
    id="health"
>
0% healthy
</div>

</div>


<div class="card">

<div class="label">
Offline
</div>

<div
    class="value"
    id="offline"
>
0
</div>

<div class="small">
Attention required
</div>

</div>


<div class="card">

<div class="label">
Servers
</div>

<div
    class="value"
    id="servers"
>
0
</div>

<div class="small">
Infrastructure nodes
</div>

</div>


<div class="card">

<div class="label">
Clients
</div>

<div
    class="value"
    id="clients"
>
0
</div>

<div class="small">
Domain workstations
</div>

</div>


</section>


<section class="metrics">


<div class="metric">

<div class="label">
Average CPU
</div>

<div
    class="metric-value"
    id="cpu"
>
0%
</div>

<div class="progress">

<div
    class="fill"
    id="cpuBar"
    style="width:0%"
>
</div>

</div>

</div>


<div class="metric">

<div class="label">
Average RAM
</div>

<div
    class="metric-value"
    id="ram"
>
0%
</div>

<div class="progress">

<div
    class="fill"
    id="ramBar"
    style="width:0%"
>
</div>

</div>

</div>


<div class="metric">

<div class="label">
Average Disk
</div>

<div
    class="metric-value"
    id="disk"
>
0%
</div>

<div class="progress">

<div
    class="fill"
    id="diskBar"
    style="width:0%"
>
</div>

</div>

</div>


</section>


<section class="table-panel">


<div class="table-header">

<span>
Device Overview
</span>

<span
    class="small"
    id="updated"
>
No data yet
</span>

</div>


<div class="table-wrap">


<table>


<thead>

<tr>

<th>
Device
</th>

<th>
Role
</th>

<th>
IP Address
</th>

<th>
Status
</th>

<th>
CPU
</th>

<th>
RAM
</th>

<th>
Disk
</th>

<th>
Uptime
</th>

</tr>

</thead>


<tbody id="deviceTable">
</tbody>


</table>


</div>


</section>


<section class="bottom">


<div class="info">

<div class="info-title">
Active Directory
</div>

<div class="info-body">

Domain:
kurs.intern

<br>

Auto Discovery:
Enabled

</div>

</div>


<div class="info">

<div class="info-title">
DNS
</div>

<div class="info-body">

SERVER-DC

<br>

SRV-DC01

</div>

</div>


<div class="info">

<div class="info-title">
DHCP
</div>

<div class="info-body">

SRV-APP01

<br>

192.168.100.100 – 200

</div>

</div>


<div class="info">

<div class="info-title">
Monitoring
</div>

<div class="info-body">

AD Discovery

<br>

WinRM + CIM

</div>

</div>


</section>


</main>


</div>


<script>


function average(values) {

    const valid =
        values.filter(
            value =>
                value !== null
                &&
                value !== undefined
        );

    if (!valid.length) {
        return 0;
    }

    return (
        valid.reduce(
            (a, b) =>
                a + b,
            0
        )
        /
        valid.length
    ).toFixed(1);
}


function show(value) {

    if (
        value === null
        ||
        value === undefined
    ) {
        return "-";
    }

    return value;
}


async function loadData() {

    try {

        const response =
            await fetch(
                "/api/devices",
                {
                    cache:
                        "no-store"
                }
            );

        if (!response.ok) {
            throw new Error(
                "API request failed"
            );
        }

        const payload =
            await response.json();


        const devices =
            payload.devices
            || [];


        const warning =
            document.getElementById(
                "collectorWarning"
            );


        if (
            !devices.length
        ) {

            warning.style.display =
                "block";

        } else {

            warning.style.display =
                "none";
        }


        const total =
            devices.length;


        const online =
            devices.filter(
                device =>
                    device.online
            ).length;


        const offline =
            total
            -
            online;


        const servers =
            devices.filter(
                device =>
                    device.type
                    !==
                    "Client"
            ).length;


        const clients =
            devices.filter(
                device =>
                    device.type
                    ===
                    "Client"
            ).length;


        document.getElementById(
            "total"
        ).textContent =
            total;


        document.getElementById(
            "online"
        ).textContent =
            online;


        document.getElementById(
            "offline"
        ).textContent =
            offline;


        document.getElementById(
            "servers"
        ).textContent =
            servers;


        document.getElementById(
            "clients"
        ).textContent =
            clients;


        const health =
            total
            ?
            Math.round(
                online
                /
                total
                *
                100
            )
            :
            0;


        document.getElementById(
            "health"
        ).textContent =
            `${health}% healthy`;


        const cpu =
            average(
                devices.map(
                    device =>
                        device.cpu
                )
            );


        const ram =
            average(
                devices.map(
                    device =>
                        device.ram
                )
            );


        const disk =
            average(
                devices.map(
                    device =>
                        device.disk
                )
            );


        document.getElementById(
            "cpu"
        ).textContent =
            `${cpu}%`;


        document.getElementById(
            "ram"
        ).textContent =
            `${ram}%`;


        document.getElementById(
            "disk"
        ).textContent =
            `${disk}%`;


        document.getElementById(
            "cpuBar"
        ).style.width =
            `${cpu}%`;


        document.getElementById(
            "ramBar"
        ).style.width =
            `${ram}%`;


        document.getElementById(
            "diskBar"
        ).style.width =
            `${disk}%`;


        const table =
            document.getElementById(
                "deviceTable"
            );


        table.innerHTML =
            "";


        devices.forEach(
            device => {

                const tr =
                    document.createElement(
                        "tr"
                    );


                const roleClass =
                    device.type
                    ===
                    "Client"
                    ?
                    "role client"
                    :
                    "role";


                const statusClass =
                    device.online
                    ?
                    "online"
                    :
                    "offline";


                const status =
                    device.online
                    ?
                    "● ONLINE"
                    :
                    "● OFFLINE";


                tr.innerHTML = `

                    <td
                        class="
                            device-name
                        "
                    >
                        ${device.name}
                    </td>

                    <td>

                        <span
                            class="
                                ${roleClass}
                            "
                        >
                            ${device.type}
                        </span>

                    </td>

                    <td>
                        ${device.ip}
                    </td>

                    <td
                        class="
                            ${statusClass}
                        "
                    >
                        ${status}
                    </td>

                    <td>
                        ${show(device.cpu)}%
                    </td>

                    <td>
                        ${show(device.ram)}%
                    </td>

                    <td>
                        ${show(device.disk)}%
                    </td>

                    <td>
                        ${show(device.uptime)} h
                    </td>
                `;


                table.appendChild(
                    tr
                );
            }
        );


        if (
            payload.updated_at
        ) {

            const date =
                new Date(
                    payload.updated_at
                );


            document.getElementById(
                "updated"
            ).textContent =
                "Last collector update: "
                +
                date.toLocaleString();

        } else {

            document.getElementById(
                "updated"
            ).textContent =
                "Waiting for collector";
        }

    }

    catch(error) {

        document.getElementById(
            "collectorWarning"
        ).style.display =
            "block";


        document.getElementById(
            "updated"
        ).textContent =
            "Cloud API unavailable";


        console.error(
            error
        );
    }
}


loadData();


setInterval(
    loadData,
    10000
);


</script>


</body>


</html>
"""