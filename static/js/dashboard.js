/**
 * SecureFog Health Dashboard Client
 * Clean Tabbed Interface with Real-Time Telemetry and Multi-Agent Tracking
 */

let vitalsChart = null;
const chartTimeLabels = [];
const chartHrData = [];
const chartSpo2Data = [];
const maxChartPoints = 25;

// Tab Navigation Switcher
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    // Show target tab
    const target = document.getElementById(`tab-${tabId}`);
    if (target) {
        target.classList.remove('hidden');
    }

    // Update sidebar active buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.className = "nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium transition text-left active-tab bg-cyan-600/10 text-cyan-400 border border-cyan-500/30";
        } else {
            btn.className = "nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium transition text-left text-slate-400 hover:bg-slate-800 hover:text-slate-200";
        }
    });

    if (tabId === 'cloud-sync') {
        fetchCloudRecords();
    }
}

// Initialize Chart.js
function initChart() {
    const canvas = document.getElementById('overviewChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    vitalsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartTimeLabels,
            datasets: [
                {
                    label: 'Heart Rate (BPM)',
                    data: chartHrData,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2,
                    tension: 0.35,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'SpO2 (%)',
                    data: chartSpo2Data,
                    borderColor: '#10b981',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    grid: { color: 'rgba(51, 65, 85, 0.3)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 40,
                    max: 180,
                    grid: { color: 'rgba(51, 65, 85, 0.3)' },
                    ticks: { color: '#06b6d4', font: { size: 10 } }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 70,
                    max: 100,
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#10b981', font: { size: 10 } }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#cbd5e1', boxWidth: 12, font: { size: 11 } }
                }
            }
        }
    });
}

let selectedPatientId = "P-101";

function onChartPatientChange(newPid) {
    selectedPatientId = newPid;
    chartTimeLabels.length = 0;
    chartHrData.length = 0;
    chartSpo2Data.length = 0;
    if (vitalsChart) {
        vitalsChart.update();
    }
}

function updateChart(hr, spo2) {
    if (!vitalsChart) return;
    const nowStr = new Date().toLocaleTimeString();
    
    chartTimeLabels.push(nowStr);
    chartHrData.push(hr);
    chartSpo2Data.push(spo2);

    if (chartTimeLabels.length > maxChartPoints) {
        chartTimeLabels.shift();
        chartHrData.shift();
        chartSpo2Data.shift();
    }

    vitalsChart.update();
}

// Render Patient Vitals Cards
function renderPatients(vitalsList) {
    const container = document.getElementById('patient-cards-container');
    if (!container || !vitalsList || vitalsList.length === 0) return;

    const latestPatients = {};
    for (const v of vitalsList) {
        if (!latestPatients[v.patient_id] || latestPatients[v.patient_id].timestamp < v.timestamp) {
            latestPatients[v.patient_id] = v;
        }
    }

    let html = '';
    for (const pid in latestPatients) {
        const p = latestPatients[pid];
        const isEmergency = p.triage_level === 'CRITICAL_EMERGENCY';
        const isWarning = p.triage_level === 'WARNING';
        
        let cardClass = "bg-slate-900/80 border border-slate-800";
        let badgeClass = "bg-emerald-950 text-emerald-400 border-emerald-800";
        let statusText = "STABLE";

        if (isEmergency) {
            cardClass = "bg-red-950/40 border-red-700 emergency-pulse";
            badgeClass = "bg-red-900 text-red-300 border-red-600 animate-pulse";
            statusText = "CRITICAL EMERGENCY";
        } else if (isWarning) {
            cardClass = "bg-amber-950/30 border-amber-700/80";
            badgeClass = "bg-amber-900 text-amber-300 border-amber-600";
            statusText = "WARNING / ATTENTION";
        }

        html += `
        <div class="${cardClass} p-4 rounded-xl shadow-md transition space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <div>
                    <h3 class="text-sm font-bold text-slate-100">${p.patient_name || pid}</h3>
                    <span class="text-[11px] text-slate-400 font-mono">${pid} • ${p.department || 'ICU'}</span>
                </div>
                <span class="text-[10px] font-bold px-2.5 py-0.5 rounded border ${badgeClass}">
                    ${statusText}
                </span>
            </div>

            <div class="grid grid-cols-3 gap-2 text-center">
                <div class="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
                    <div class="text-[10px] text-slate-400 font-semibold">HEART RATE</div>
                    <div class="text-lg font-extrabold ${p.heart_rate > 100 || p.heart_rate < 55 ? 'text-red-400' : 'text-cyan-400'}">
                        ${p.heart_rate} <span class="text-[10px] font-normal text-slate-400">bpm</span>
                    </div>
                </div>
                <div class="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
                    <div class="text-[10px] text-slate-400 font-semibold">SPO2 OXYGEN</div>
                    <div class="text-lg font-extrabold ${p.spo2 < 93 ? 'text-red-400' : 'text-emerald-400'}">
                        ${p.spo2}%
                    </div>
                </div>
                <div class="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
                    <div class="text-[10px] text-slate-400 font-semibold">BLOOD PRESS.</div>
                    <div class="text-lg font-extrabold ${p.systolic_bp > 140 ? 'text-amber-400' : 'text-indigo-400'}">
                        ${Math.round(p.systolic_bp)}/${Math.round(p.diastolic_bp)}
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                <span>Temp: <strong class="text-slate-200">${p.temperature}°C</strong> | Glucose: <strong class="text-slate-200">${Math.round(p.blood_glucose)} mg/dL</strong></span>
                <span class="text-cyan-400 font-mono">${p.fog_node_id || 'FogNode-01'}</span>
            </div>
        </div>
        `;
    }

    container.innerHTML = html;

    // Update KPI counter
    const kpiP = document.getElementById('kpi-patients-count');
    if (kpiP) kpiP.textContent = `${Object.keys(latestPatients).length} Monitored`;

    // Update the Dropdown options if patient count changed
    const selectEl = document.getElementById('chart-patient-select');
    if (selectEl && selectEl.options.length !== Object.keys(latestPatients).length) {
        let optHtml = '';
        for (const pid in latestPatients) {
            const p = latestPatients[pid];
            const prefix = p.triage_level === 'CRITICAL_EMERGENCY' ? '🔴 [CRITICAL] ' : (p.triage_level === 'WARNING' ? '🟡 [WARNING] ' : '🟢 ');
            optHtml += `<option value="${pid}" ${pid === selectedPatientId ? 'selected' : ''}>${prefix}${pid} (${p.patient_name || pid} - ${p.department || 'Ward'})</option>`;
        }
        selectEl.innerHTML = optHtml;
        selectEl.value = selectedPatientId;
    }

    // Stream selected patient (or default critical patient) to waveform chart
    let targetP = latestPatients[selectedPatientId];
    if (!targetP) {
        targetP = Object.values(latestPatients)[0];
        if (targetP) {
            selectedPatientId = targetP.patient_id;
            if (selectEl) selectEl.value = selectedPatientId;
        }
    }

    if (targetP) {
        updateChart(targetP.heart_rate, targetP.spo2);
    }
}

// Render Fog Computing Nodes
function renderFogNodes(fogNodesMap) {
    const container = document.getElementById('fog-nodes-container');
    if (!container || !fogNodesMap) return;

    let html = '';
    let totalThreats = 0;
    for (const nid in fogNodesMap) {
        const node = fogNodesMap[nid];
        totalThreats += node.active_threats_blocked || 0;
        
        const cpu = node.cpu_utilization_pct || 0;
        const cpuColor = cpu > 80 ? 'bg-red-500' : (cpu > 60 ? 'bg-amber-500' : 'bg-cyan-500');

        html += `
        <div class="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-md space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <div class="flex items-center space-x-2">
                    <div class="w-2.5 h-2.5 rounded-full ${node.status === 'OPTIMAL' ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'}"></div>
                    <h3 class="text-sm font-bold text-slate-200">${node.node_name}</h3>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-mono">${node.node_id}</span>
            </div>

            <!-- CPU Gauge -->
            <div>
                <div class="flex justify-between text-xs text-slate-400 mb-1.5">
                    <span>CPU Utilization</span>
                    <span class="font-mono text-slate-200 font-bold">${cpu}%</span>
                </div>
                <div class="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800">
                    <div class="${cpuColor} h-2.5 rounded-full progress-bar-fill" style="width: ${cpu}%"></div>
                </div>
            </div>

            <!-- Adaptive Computing Stats -->
            <div class="grid grid-cols-2 gap-2 text-xs pt-2">
                <div class="bg-slate-950/70 p-2 rounded-lg border border-slate-800 text-center">
                    <div class="text-[10px] text-slate-400">Adaptive Rate</div>
                    <div class="font-bold text-cyan-400">${node.sampling_rate_hz} Hz</div>
                </div>
                <div class="bg-slate-950/70 p-2 rounded-lg border border-slate-800 text-center">
                    <div class="text-[10px] text-slate-400">Offloaded Jobs</div>
                    <div class="font-bold text-purple-400">${node.offloaded_tasks_count} tasks</div>
                </div>
            </div>

            <div class="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                <span>Queue Latency: <strong class="text-slate-200">${node.queue_latency_ms} ms</strong></span>
                <span class="text-red-400 font-bold">Blocked: ${node.active_threats_blocked}</span>
            </div>
        </div>
        `;
    }

    container.innerHTML = html;
    const threatKpi = document.getElementById('kpi-threats-count');
    if (threatKpi) threatKpi.textContent = `${totalThreats} Blocked`;
}

// Render Quarantined Devices
function renderQuarantined(quarantinedList) {
    const container = document.getElementById('quarantined-list');
    const badge = document.getElementById('quarantine-count-badge');
    const kpiBadge = document.getElementById('kpi-quarantine-count');

    if (badge) badge.textContent = `${quarantinedList.length} Devices`;
    if (kpiBadge) kpiBadge.textContent = `${quarantinedList.length} Quarantined`;

    if (!container) return;

    if (!quarantinedList || quarantinedList.length === 0) {
        container.innerHTML = `<p class="text-slate-500 italic text-center py-4">No active quarantines. Network secure.</p>`;
        return;
    }

    let html = '';
    for (const d of quarantinedList) {
        html += `
        <div class="bg-red-950/40 border border-red-800/80 p-3 rounded-lg flex items-center justify-between">
            <div class="space-y-0.5">
                <div class="font-mono text-red-300 font-bold text-xs flex items-center space-x-1.5">
                    <i class="fa-solid fa-lock text-red-400"></i>
                    <span>${d.sensor_id}</span>
                </div>
                <div class="text-[11px] text-slate-400">${d.reason}</div>
            </div>
            <button onclick="unblockSensor('${d.sensor_id}')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 px-2.5 py-1 rounded text-xs font-semibold transition">
                Unblock
            </button>
        </div>
        `;
    }
    container.innerHTML = html;
}

// Render Security and Clinical Alerts
function renderAlerts(secAlerts, clinAlerts) {
    // Security Alerts (in Security Tab)
    const secContainer = document.getElementById('security-alerts-list');
    if (secContainer && secAlerts && secAlerts.length > 0) {
        let secHtml = '';
        for (const a of secAlerts.slice(0, 5)) {
            secHtml += `
            <div class="bg-red-950/30 border border-red-900/60 p-2.5 rounded-lg space-y-1">
                <div class="flex items-center justify-between text-xs font-bold text-red-400">
                    <span>${a.threat_type}</span>
                    <span class="text-[10px] bg-red-900/80 px-1.5 py-0.5 rounded text-red-200">${a.severity}</span>
                </div>
                <div class="text-xs text-slate-300">${a.description}</div>
                <div class="text-[10px] text-slate-500 flex justify-between">
                    <span>Source: ${a.source_sensor_id}</span>
                    <span>Action: ${a.mitigation_action}</span>
                </div>
            </div>
            `;
        }
        secContainer.innerHTML = secHtml;
    }

    // Combined Alerts (in Overview Tab)
    const overviewAlerts = document.getElementById('overview-alerts-list');
    if (overviewAlerts) {
        let combHtml = '';
        if (secAlerts) {
            for (const a of secAlerts.slice(0, 3)) {
                combHtml += `
                <div class="bg-red-950/30 border border-red-900/60 p-2.5 rounded-lg space-y-0.5">
                    <div class="flex justify-between text-xs font-bold text-red-400">
                        <span><i class="fa-solid fa-shield-virus mr-1"></i> ${a.threat_type}</span>
                        <span class="text-[10px] text-slate-400">${a.severity}</span>
                    </div>
                    <div class="text-xs text-slate-300">${a.description}</div>
                </div>
                `;
            }
        }
        if (clinAlerts) {
            for (const c of clinAlerts.slice(0, 3)) {
                combHtml += `
                <div class="bg-amber-950/30 border border-amber-900/60 p-2.5 rounded-lg space-y-0.5">
                    <div class="flex justify-between text-xs font-bold text-amber-300">
                        <span><i class="fa-solid fa-notes-medical mr-1"></i> ${c.patient_name} (${c.patient_id})</span>
                        <span class="text-[10px] text-amber-400">${c.triage_level}</span>
                    </div>
                    <div class="text-xs text-slate-300">${c.diagnosis_flag}</div>
                </div>
                `;
            }
        }
        if (combHtml) {
            overviewAlerts.innerHTML = combHtml;
        }
    }
}

// Render Agent Logs
function renderAgentLogs(messages) {
    const container = document.getElementById('agent-bus-logs');
    if (!container || !messages || messages.length === 0) return;

    let html = '';
    for (const m of messages.slice(-20)) {
        html += `
        <div class="border-b border-slate-900 pb-1">
            <span class="text-cyan-400 font-bold">[${m.sender_agent}]</span>
            <span class="text-slate-500">→</span>
            <span class="text-purple-400">[${m.receiver_agent}]</span>:
            <span class="text-amber-300 font-semibold">${m.action}</span>
        </div>
        `;
    }
    container.innerHTML = html;
    container.scrollTop = container.scrollHeight;
}

// Fetch Cloud Anonymized Records
async function fetchCloudRecords() {
    const tbody = document.getElementById('cloud-records-body');
    if (!tbody) return;
    try {
        const res = await fetch('/api/cloud/summary');
        const data = await res.json();
        const records = data.recent_cloud_syncs || [];

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-500 italic">No cloud records synced yet.</td></tr>`;
            return;
        }

        let html = '';
        for (const r of records) {
            const dateStr = new Date(r.timestamp * 1000).toLocaleTimeString();
            html += `
            <tr class="hover:bg-slate-900/50">
                <td class="p-2.5 font-mono text-cyan-400">${r.sync_id}</td>
                <td class="p-2.5 font-mono text-slate-300">${r.fog_node_id}</td>
                <td class="p-2.5 font-mono text-emerald-400">${r.anonymized_patient_hash}</td>
                <td class="p-2.5 text-slate-300">${r.triage_summary}</td>
                <td class="p-2.5 text-slate-400">${dateStr}</td>
            </tr>
            `;
        }
        tbody.innerHTML = html;
    } catch (e) {
        console.error('Error loading cloud records:', e);
    }
}

// Modal Controller
function toggleModal(modalId, show) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    if (show) {
        modal.classList.remove('hidden');
    } else {
        modal.classList.add('hidden');
    }
}

// Global Toast Notification
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('global-notification-toast');
    if (!toast) return;

    let bgClass = "bg-slate-900 border-slate-700 text-slate-200";
    let icon = '<i class="fa-solid fa-circle-info text-cyan-400 text-lg mr-3"></i>';

    if (type === 'attack_intercepted') {
        bgClass = "bg-red-950/90 border-red-600 text-red-100 emergency-pulse";
        icon = '<i class="fa-solid fa-shield-virus text-red-400 text-xl mr-3 animate-bounce"></i>';
    } else if (type === 'success') {
        bgClass = "bg-emerald-950/90 border-emerald-600 text-emerald-100";
        icon = '<i class="fa-solid fa-circle-check text-emerald-400 text-xl mr-3"></i>';
    }

    toast.className = `${bgClass} p-4 rounded-xl shadow-2xl flex items-center justify-between border block mb-4`;
    toast.innerHTML = `
        <div class="flex items-center">
            ${icon}
            <div>
                <div class="font-bold text-sm">${title}</div>
                <div class="text-xs opacity-90 mt-0.5">${message}</div>
            </div>
        </div>
        <button onclick="document.getElementById('global-notification-toast').classList.add('hidden')" class="text-slate-400 hover:text-white text-lg ml-4">&times;</button>
    `;

    // Auto-dismiss after 7 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 7000);
}

// Submit New Patient
async function submitNewPatient() {
    const name = document.getElementById('new-p-name').value.trim();
    const age = parseInt(document.getElementById('new-p-age').value) || 45;
    const department = document.getElementById('new-p-dept').value;
    const baseHr = parseFloat(document.getElementById('new-p-hr').value) || 75.0;
    const baseSpo2 = parseFloat(document.getElementById('new-p-spo2').value) || 98.0;
    const tendency = document.getElementById('new-p-tendency').value;
    const fogNode = document.getElementById('new-p-fognode').value;

    if (!name) {
        alert("Please enter patient full name.");
        return;
    }

    const payload = {
        name: name,
        age: age,
        department: department,
        base_hr: baseHr,
        base_spo2: baseSpo2,
        base_sbp: 120.0,
        base_dbp: 80.0,
        condition_tendency: tendency,
        target_fog_node: fogNode
    };

    try {
        const res = await fetch('/api/patients/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        toggleModal('patient-modal', false);
        document.getElementById('new-p-name').value = '';
        showToast("Patient Admitted & Live Stream Started", data.message, "success");
    } catch (err) {
        alert("Failed to admit patient: " + err.message);
    }
}

// Attack Simulation Launch
async function launchAttackSimulation() {
    const attackType = document.getElementById('attack-type-select').value;
    const targetFogNode = document.getElementById('attack-node-select').value;
    const tamperVal = parseFloat(document.getElementById('tamper-val').value) || 480.0;

    let targetSensor = "SENS-ECG-101";
    if (attackType === "SENSOR_SPOOFING") {
        targetSensor = "ROGUE_SENSOR_0xDEADBEEF";
    }

    const payload = {
        attack_type: attackType,
        target_sensor_id: targetSensor,
        target_fog_node: targetFogNode,
        intensity: 20,
        tamper_metric: "heart_rate",
        tamper_value: tamperVal
    };

    const feedbackBox = document.getElementById('attack-feedback-box');
    if (feedbackBox) {
        feedbackBox.className = "p-3 rounded-lg text-xs border bg-amber-950/60 border-amber-700 text-amber-300 block";
        feedbackBox.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Injecting ${attackType} to ${targetFogNode}...`;
    }

    try {
        const response = await fetch('/api/attack/inject', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();

        if (feedbackBox) {
            feedbackBox.className = "p-3 rounded-lg text-xs border bg-red-950/80 border-red-600 text-red-200 block";
            feedbackBox.innerHTML = `
                <div class="font-bold flex items-center space-x-1">
                    <i class="fa-solid fa-shield-halved"></i>
                    <span>Threat Intercepted by Security Agent!</span>
                </div>
                <div class="mt-1">${result.message}</div>
                <div class="mt-1 text-[11px] text-amber-300">Sensor quarantined and firewall policy enforced.</div>
            `;
        }

        // Show prominent toast across all screens
        showToast(
            `⚠️ Cyber Threat Intercepted: ${attackType}`,
            `Security Agent isolated rogue sensor (${targetSensor}) on ${targetFogNode}. Dynamic Firewall enforced.`,
            'attack_intercepted'
        );
    } catch (err) {
        if (feedbackBox) {
            feedbackBox.className = "p-3 rounded-lg text-xs border bg-red-950 border-red-800 text-red-400 block";
            feedbackBox.innerHTML = `Failed to inject attack: ${err.message}`;
        }
    }
}

// Unblock Sensor
async function unblockSensor(sensorId) {
    try {
        await fetch(`/api/quarantine/unblock?sensor_id=${sensorId}`, { method: 'POST' });
        showToast("Device Unblocked", `Sensor ${sensorId} restored to active network communication.`, "success");
    } catch (err) {
        console.error('Error unblocking:', err);
    }
}

// Force Cloud Sync
async function forceCloudSync() {
    try {
        const res = await fetch('/api/cloud/sync', { method: 'POST' });
        const data = await res.json();
        showToast("HIPAA Privacy Sync Completed", `${data.message} Records masked with SHA-256 and age-generalized.`, "success");
        fetchCloudRecords();
    } catch (err) {
        alert('Cloud sync failed: ' + err.message);
    }
}

// WebSocket Live Stream Connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        const statusEl = document.getElementById('ws-status');
        if (statusEl) {
            statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span>Live</span>`;
            statusEl.className = 'flex items-center space-x-1.5 text-emerald-400 font-semibold';
        }
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'TELEMETRY_UPDATE') {
                renderPatients(data.vitals);
                renderFogNodes(data.fog_nodes);
                renderQuarantined(data.quarantined_devices);
                renderAlerts(data.security_alerts, data.clinical_alerts);
                renderAgentLogs(data.agent_messages);
            }
        } catch (e) {
            console.error('Error parsing WS frame:', e);
        }
    };

    ws.onclose = () => {
        const statusEl = document.getElementById('ws-status');
        if (statusEl) {
            statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span><span>Reconnecting...</span>`;
            statusEl.className = 'flex items-center space-x-1.5 text-amber-400 font-semibold';
        }
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => {
        ws.close();
    };
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    connectWebSocket();

    const attackSelect = document.getElementById('attack-type-select');
    const tamperParams = document.getElementById('tamper-params');
    if (attackSelect && tamperParams) {
        attackSelect.addEventListener('change', (e) => {
            if (e.target.value === 'DATA_TAMPERING') {
                tamperParams.classList.remove('hidden');
            } else {
                tamperParams.classList.add('hidden');
            }
        });
    }
});
