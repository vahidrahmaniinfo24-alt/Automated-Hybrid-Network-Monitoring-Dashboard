from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from collector import collect_status

app = FastAPI(title="Automated Hybrid Network Monitoring Dashboard")


@app.get("/api/devices")
def api_devices():
    return collect_status()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Automated Hybrid Network Monitoring Dashboard</title>

    <style>
        :root {
            --bg: #07111f;
            --panel: rgba(14, 28, 48, 0.72);
            --panel-strong: rgba(18, 36, 60, 0.92);
            --border: rgba(104, 190, 255, 0.18);
            --border-strong: rgba(104, 190, 255, 0.35);

            --text: #f3f8ff;
            --muted: #8ea5bd;

            --azure: #38bdf8;
            --azure-2: #0ea5e9;
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
            background:
                radial-gradient(
                    circle at 20% 0%,
                    rgba(14,165,233,0.13),
                    transparent 32%
                ),
                radial-gradient(
                    circle at 90% 10%,
                    rgba(59,130,246,0.10),
                    transparent 28%
                ),
                linear-gradient(
                    135deg,
                    #050b14,
                    #07111f 50%,
                    #091828
                );
            color: var(--text);
        }

        .app {
            display: grid;
            grid-template-columns: 250px 1fr;
            min-height: 100vh;
        }

        .sidebar {
            border-right: 1px solid var(--border);
            background: rgba(4, 12, 24, 0.82);
            backdrop-filter: blur(22px);
            padding: 24px 18px;
            display: flex;
            flex-direction: column;
        }

        .brand {
            padding: 12px 10px 28px;
            border-bottom: 1px solid var(--border);
        }

        .brand-title {
            font-size: 18px;
            font-weight: 700;
            line-height: 1.35;
        }

        .brand-domain {
            color: var(--azure);
            font-size: 12px;
            margin-top: 8px;
            letter-spacing: 1px;
        }

        .nav {
            margin-top: 20px;
            display: grid;
            gap: 8px;
        }

        .nav-item {
            padding: 12px 14px;
            border-radius: 10px;
            color: var(--muted);
            border: 1px solid transparent;
        }

        .nav-item.active {
            color: white;
            background: rgba(14,165,233,0.10);
            border-color: rgba(56,189,248,0.28);
            box-shadow:
                inset 0 0 20px rgba(14,165,233,0.04),
                0 0 18px rgba(14,165,233,0.04);
        }

        .sidebar-footer {
            margin-top: auto;
            padding-top: 20px;
        }

        .mini-status {
            padding: 16px;
            border: 1px solid var(--border);
            background: var(--panel);
            border-radius: 12px;
        }

        .mini-row {
            display: flex;
            justify-content: space-between;
            margin: 9px 0;
            color: var(--muted);
            font-size: 13px;
        }

        .main {
            padding: 26px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
        }

        .title h1 {
            margin: 0;
            font-size: 27px;
            letter-spacing: -0.5px;
        }

        .title p {
            margin: 7px 0 0;
            color: var(--muted);
            font-size: 14px;
        }

        .live {
            display: flex;
            align-items: center;
            gap: 9px;
            color: #d9fbe4;
            font-size: 13px;
            border: 1px solid rgba(34,197,94,0.2);
            background: rgba(34,197,94,0.06);
            padding: 9px 12px;
            border-radius: 999px;
        }

        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 12px var(--green);
        }

        .cards {
            display: grid;
            grid-template-columns:
                repeat(5, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }

        .card {
            position: relative;
            overflow: hidden;
            border-radius: 14px;
            padding: 18px;
            background: var(--panel);
            border: 1px solid var(--border);
            backdrop-filter: blur(18px);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.03),
                0 8px 30px rgba(0,0,0,0.15);
        }

        .card::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.025),
                    transparent 50%
                );
            pointer-events: none;
        }

        .card-label {
            color: var(--muted);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        .card-value {
            font-size: 30px;
            font-weight: 700;
            margin-top: 8px;
        }

        .card-sub {
            margin-top: 5px;
            font-size: 12px;
            color: var(--muted);
        }

        .accent-blue {
            border-color: rgba(56,189,248,0.28);
        }

        .accent-green {
            border-color: rgba(34,197,94,0.25);
        }

        .accent-red {
            border-color: rgba(239,68,68,0.24);
        }

        .accent-purple {
            border-color: rgba(168,85,247,0.25);
        }

        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 14px;
            margin-bottom: 18px;
        }

        .metric-panel {
            border: 1px solid var(--border);
            background: var(--panel);
            border-radius: 14px;
            padding: 18px;
        }

        .panel-title {
            font-size: 13px;
            color: #cbd9e8;
            margin-bottom: 16px;
        }

        .metric-big {
            font-size: 30px;
            font-weight: 700;
        }

        .progress {
            height: 8px;
            background: rgba(255,255,255,0.06);
            border-radius: 999px;
            margin-top: 16px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background:
                linear-gradient(
                    90deg,
                    var(--azure),
                    #60a5fa
                );
            box-shadow: 0 0 12px rgba(56,189,248,0.35);
        }

        .table-panel {
            border: 1px solid var(--border);
            border-radius: 14px;
            background: var(--panel);
            overflow: hidden;
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px;
            border-bottom: 1px solid var(--border);
        }

        .table-title {
            font-size: 14px;
            font-weight: 600;
        }

        .last-update {
            color: var(--muted);
            font-size: 12px;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 1050px;
        }

        th {
            text-align: left;
            padding: 13px 16px;
            font-size: 11px;
            color: #8299b1;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            background: rgba(255,255,255,0.018);
        }

        td {
            padding: 15px 16px;
            border-top: 1px solid rgba(104,190,255,0.08);
            font-size: 13px;
        }

        tr:hover td {
            background: rgba(56,189,248,0.035);
        }

        .device-name {
            color: #dff5ff;
            font-weight: 600;
        }

        .role {
            display: inline-block;
            padding: 5px 8px;
            border-radius: 6px;
            background: rgba(168,85,247,0.10);
            border: 1px solid rgba(168,85,247,0.22);
            color: #d6b4ff;
            font-size: 11px;
        }

        .role.client {
            background: rgba(56,189,248,0.08);
            border-color: rgba(56,189,248,0.20);
            color: #9bddff;
        }

        .online {
            color: #73e694;
            font-weight: 600;
        }

        .offline {
            color: #ff7c7c;
            font-weight: 600;
        }

        .mini-bar {
            width: 78px;
            height: 6px;
            background: rgba(255,255,255,0.07);
            border-radius: 999px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-left: 6px;
        }

        .mini-fill {
            height: 100%;
            border-radius: 999px;
            background: var(--azure);
        }

        .mini-fill.warning {
            background: var(--yellow);
        }

        .mini-fill.critical {
            background: var(--red);
        }

        .bottom-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-top: 18px;
        }

        .info-card {
            border: 1px solid var(--border);
            background: var(--panel);
            border-radius: 14px;
            padding: 17px;
        }

        .info-title {
            color: var(--azure);
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .info-value {
            font-size: 13px;
            line-height: 1.6;
            color: #d9e8f5;
        }

        @media (max-width: 1150px) {
            .app {
                grid-template-columns: 1fr;
            }

            .sidebar {
                display: none;
            }

            .cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .content-grid {
                grid-template-columns: 1fr;
            }

            .bottom-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 650px) {
            .main {
                padding: 15px;
            }

            .cards,
            .bottom-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
<div class="app">

    <aside class="sidebar">

        <div class="brand">
            <div class="brand-title">
                Windows Infrastructure Monitor
            </div>

            <div class="brand-domain">
                KURS.INTERN
            </div>
        </div>

        <div class="nav">
            <div class="nav-item active">Dashboard</div>
            <div class="nav-item">Devices</div>
            <div class="nav-item">Active Directory</div>
            <div class="nav-item">Performance</div>
            <div class="nav-item">Alerts</div>
            <div class="nav-item">Reports</div>
        </div>

        <div class="sidebar-footer">

            <div class="mini-status">

                <div class="mini-row">
                    <span>Collector</span>
                    <span style="color:#73e694;">Online</span>
                </div>

                <div class="mini-row">
                    <span>Domain</span>
                    <span>kurs.intern</span>
                </div>

                <div class="mini-row">
                    <span>Refresh</span>
                    <span>10 sec</span>
                </div>

            </div>

        </div>

    </aside>


    <main class="main">

        <div class="topbar">

            <div class="title">
                <h1>
                    Automated Hybrid Network Monitoring Dashboard
                </h1>

                <p>
                    Real-Time Windows Infrastructure Monitoring
                </p>
            </div>

            <div class="live">
                <span class="dot"></span>
                LIVE
            </div>

        </div>


        <section class="cards">

            <div class="card accent-blue">
                <div class="card-label">Total Devices</div>
                <div class="card-value" id="totalDevices">0</div>
                <div class="card-sub">Active Directory Devices</div>
            </div>

            <div class="card accent-green">
                <div class="card-label">Online</div>
                <div class="card-value" id="onlineDevices">0</div>
                <div class="card-sub" id="onlinePercent">0%</div>
            </div>

            <div class="card accent-red">
                <div class="card-label">Offline</div>
                <div class="card-value" id="offlineDevices">0</div>
                <div class="card-sub">Requires attention</div>
            </div>

            <div class="card accent-purple">
                <div class="card-label">Servers</div>
                <div class="card-value" id="serverCount">0</div>
                <div class="card-sub">Infrastructure Nodes</div>
            </div>

            <div class="card accent-blue">
                <div class="card-label">Clients</div>
                <div class="card-value" id="clientCount">0</div>
                <div class="card-sub">Domain Workstations</div>
            </div>

        </section>


        <section class="content-grid">

            <div class="metric-panel">
                <div class="panel-title">
                    Average CPU Usage
                </div>

                <div class="metric-big" id="avgCpu">
                    0%
                </div>

                <div class="progress">
                    <div
                        class="progress-fill"
                        id="cpuBar"
                        style="width:0%"
                    ></div>
                </div>
            </div>


            <div class="metric-panel">
                <div class="panel-title">
                    Average RAM Usage
                </div>

                <div class="metric-big" id="avgRam">
                    0%
                </div>

                <div class="progress">
                    <div
                        class="progress-fill"
                        id="ramBar"
                        style="width:0%"
                    ></div>
                </div>
            </div>


            <div class="metric-panel">
                <div class="panel-title">
                    Average Disk Usage
                </div>

                <div class="metric-big" id="avgDisk">
                    0%
                </div>

                <div class="progress">
                    <div
                        class="progress-fill"
                        id="diskBar"
                        style="width:0%"
                    ></div>
                </div>
            </div>

        </section>


        <section class="table-panel">

            <div class="table-header">

                <div class="table-title">
                    Device Overview
                </div>

                <div
                    class="last-update"
                    id="lastUpdate"
                >
                    Waiting for data...
                </div>

            </div>

            <div class="table-wrap">

                <table>

                    <thead>
                        <tr>
                            <th>Device</th>
                            <th>Role</th>
                            <th>IP Address</th>
                            <th>Status</th>
                            <th>CPU</th>
                            <th>RAM</th>
                            <th>Disk</th>
                            <th>Uptime</th>
                        </tr>
                    </thead>

                    <tbody id="deviceTable"></tbody>

                </table>

            </div>

        </section>


        <section class="bottom-grid">

            <div class="info-card">
                <div class="info-title">
                    Active Directory
                </div>
                <div class="info-value">
                    Domain: kurs.intern
                    <br>
                    Auto Discovery: Enabled
                </div>
            </div>

            <div class="info-card">
                <div class="info-title">
                    DNS Servers
                </div>
                <div class="info-value">
                    192.168.100.10
                    <br>
                    192.168.100.11
                </div>
            </div>

            <div class="info-card">
                <div class="info-title">
                    DHCP Server
                </div>
                <div class="info-value">
                    192.168.100.20
                    <br>
                    Pool: 192.168.100.100 – 200
                </div>
            </div>

            <div class="info-card">
                <div class="info-title">
                    Domain Controllers
                </div>
                <div class="info-value">
                    SERVER-DC
                    <br>
                    SRV-DC01
                </div>
            </div>

        </section>

    </main>

</div>


<script>

function metricClass(value) {

    if (value >= 85) {
        return "critical";
    }

    if (value >= 70) {
        return "warning";
    }

    return "";
}


function valueOrDash(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "-";
    }

    return value;
}


async function loadDashboard() {

    try {

        const response = await fetch(
            "/api/devices",
            {
                cache: "no-store"
            }
        );

        const devices = await response.json();

        const total = devices.length;

        const online = devices.filter(
            device => device.online
        ).length;

        const offline = total - online;

        const servers = devices.filter(
            device => device.type !== "Client"
        ).length;

        const clients = devices.filter(
            device => device.type === "Client"
        ).length;


        document.getElementById(
            "totalDevices"
        ).textContent = total;

        document.getElementById(
            "onlineDevices"
        ).textContent = online;

        document.getElementById(
            "offlineDevices"
        ).textContent = offline;

        document.getElementById(
            "serverCount"
        ).textContent = servers;

        document.getElementById(
            "clientCount"
        ).textContent = clients;


        const onlinePercent =
            total > 0
            ? Math.round(
                (online / total) * 100
            )
            : 0;

        document.getElementById(
            "onlinePercent"
        ).textContent =
            `${onlinePercent}% healthy`;


        const validCpu = devices
            .map(device => device.cpu)
            .filter(value => value !== null);

        const validRam = devices
            .map(device => device.ram)
            .filter(value => value !== null);

        const validDisk = devices
            .map(device => device.disk)
            .filter(value => value !== null);


        const average = values => {

            if (!values.length) {
                return 0;
            }

            return (
                values.reduce(
                    (a, b) => a + b,
                    0
                ) / values.length
            ).toFixed(1);
        };


        const avgCpu = average(validCpu);
        const avgRam = average(validRam);
        const avgDisk = average(validDisk);


        document.getElementById(
            "avgCpu"
        ).textContent = `${avgCpu}%`;

        document.getElementById(
            "avgRam"
        ).textContent = `${avgRam}%`;

        document.getElementById(
            "avgDisk"
        ).textContent = `${avgDisk}%`;


        document.getElementById(
            "cpuBar"
        ).style.width = `${avgCpu}%`;

        document.getElementById(
            "ramBar"
        ).style.width = `${avgRam}%`;

        document.getElementById(
            "diskBar"
        ).style.width = `${avgDisk}%`;


        const table = document.getElementById(
            "deviceTable"
        );

        table.innerHTML = "";


        devices.forEach(device => {

            const tr = document.createElement("tr");

            const statusClass =
                device.online
                ? "online"
                : "offline";

            const statusText =
                device.online
                ? "● ONLINE"
                : "● OFFLINE";


            const cpu = valueOrDash(device.cpu);
            const ram = valueOrDash(device.ram);
            const disk = valueOrDash(device.disk);
            const uptime = valueOrDash(device.uptime);


            const roleClass =
                device.type === "Client"
                ? "role client"
                : "role";


            tr.innerHTML = `
                <td class="device-name">
                    ${device.name}
                </td>

                <td>
                    <span class="${roleClass}">
                        ${device.type}
                    </span>
                </td>

                <td>
                    ${device.ip}
                </td>

                <td class="${statusClass}">
                    ${statusText}
                </td>

                <td>
                    ${cpu}%
                </td>

                <td>
                    ${ram}%

                    <span class="mini-bar">
                        <span
                            class="mini-fill ${metricClass(ram)}"
                            style="display:block;width:${ram === "-" ? 0 : ram}%"
                        ></span>
                    </span>
                </td>

                <td>
                    ${disk}%

                    <span class="mini-bar">
                        <span
                            class="mini-fill ${metricClass(disk)}"
                            style="display:block;width:${disk === "-" ? 0 : disk}%"
                        ></span>
                    </span>
                </td>

                <td>
                    ${uptime} h
                </td>
            `;

            table.appendChild(tr);

        });


        document.getElementById(
            "lastUpdate"
        ).textContent =
            "Last update: " +
            new Date().toLocaleTimeString();

    }

    catch (error) {

        document.getElementById(
            "lastUpdate"
        ).textContent =
            "Collector unavailable";

        console.error(error);
    }
}


loadDashboard();

setInterval(
    loadDashboard,
    10000
);

</script>

</body>
</html>
"""

