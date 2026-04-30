import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Area, AreaChart
} from 'recharts';

import {
  Shield, LayoutDashboard, Search, TerminalSquare, Activity,
  Server, Network, AlertTriangle, Settings, Zap, Radio, Database, Cpu,
  ScrollText
} from 'lucide-react';

/* ─── Reusable Components ─── */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#000000', border: '1px solid #333333', borderRadius: '4px', padding: '8px 12px', fontSize: '11px', color: '#FFFFFF' }}>
      <p style={{ margin: 0, fontFamily: 'JetBrains Mono' }}>
        <span style={{ color: '#888888', marginRight: '8px' }}>VOL</span>
        <span style={{ color: '#5E6AD2', fontWeight: 500 }}>{Math.round(payload[0].value)} Mbps</span>
      </p>
    </div>
  );
};

const ShapRow = ({ feature, value, maxAbs }) => {
  const safeValue = typeof value === 'number' && isFinite(value) ? value : 0;
  const safeMax = typeof maxAbs === 'number' && maxAbs > 0 ? maxAbs : 1;
  const pct = Math.min(Math.abs(safeValue) / safeMax, 1) * 50;
  const pos = safeValue > 0;

  return (
    <div className="shap-row">
      <div className="shap-labels">
        <span className="shap-feature">{feature ?? '—'}</span>
        <span className={`shap-value ${pos ? 'pos' : 'neg'}`}>
          {pos ? '+' : ''}{safeValue.toFixed(4)}
        </span>
      </div>
      <div className="shap-track-container">
        <div className="shap-track-center-line"></div>
        <div
          className={`shap-fill-diverge ${pos ? 'pos' : 'neg'}`}
          style={{ width: `${pct}%`, left: pos ? '50%' : `${50 - pct}%` }}
        />
      </div>
    </div>
  );
};

const InputField = ({ label, field, value, onChange }) => (
  <div className="form-group">
    <label className="form-label">{label}</label>
    <input
      type="number" step="0.01" min="0" max="1"
      className="form-input"
      value={value}
      onChange={e => onChange(field, parseFloat(e.target.value) || 0)}
    />
  </div>
);

/* ─── Severity helpers ─── */
const severityColor = (sev) => {
  if (sev === 'High') return '#FF3366';
  if (sev === 'Medium') return '#FFB020';
  return '#00E599';
};

const severityClass = (sev) => {
  if (sev === 'High') return 'severity-high';
  if (sev === 'Medium') return 'severity-med';
  return 'severity-low';
};

/* ═══════════════════════════════════════════
   MAIN APP
   ═══════════════════════════════════════════ */
export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activePreset, setActivePreset] = useState('normal');

  // Dashboard live data (compact feed from /api/live_feed)
  const [liveFeed, setLiveFeed] = useState([]);
  const [chartData, setChartData] = useState(
    Array.from({ length: 40 }, (_, i) => ({ time: i, val: 50 + Math.random() * 20 }))
  );

  // Full Event Logs from /api/logs
  const [eventLogs, setEventLogs] = useState([]);
  const [logStats, setLogStats] = useState({ total_predictions: 0, total_attacks: 0 });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [riskData, setRiskData] = useState({ score: 12, status: 'secure' });
  const [modelInfo, setModelInfo] = useState({ type: '...', dataset: '...', status: '...', metrics: { accuracy: 0, f1: 0 } });

  const [inputs, setInputs] = useState({
    duration: 0.05, src_bytes: 0.12, dst_bytes: 0.22,
    num_failed_logins: 0.0, num_file_creations: 0.0, num_shells: 0.0,
    is_guest_login: 0.0, count: 0.18, srv_count: 0.25, dst_host_count: 0.6
  });

  const timeRef = useRef(41);
  const logListRef = useRef(null);

  /* ── Live Feed polling (drives dashboard + generates logs on backend) ── */
  useEffect(() => {
    const id = setInterval(async () => {
      try {
        const res = await fetch('/api/live_feed');
        if (!res.ok) throw new Error();
        const data = await res.json();
        const entry = data.log_entry;

        // Update compact dashboard feed
        setLiveFeed(prev => [entry, ...prev].slice(0, 10));

        // Dynamic chart: realistic noise + attack bursts
        const isAttack = entry.label === 'Attack';
        const noise = (Math.random() - 0.5) * 15;
        const idle = Math.random() > 0.85 ? -20 : 0;
        const burst = isAttack ? 300 + Math.random() * 400 : (Math.random() > 0.92 ? 120 : 0);
        const baseVal = 45 + noise + idle + burst;

        setChartData(prev => [...prev.slice(1), { time: timeRef.current++, val: Math.max(8, baseVal) }]);

        // Risk indicator
        setRiskData({
          score: data.risk_score,
          status: data.risk_score > 70 ? 'danger' : (data.risk_score > 30 ? 'warning' : 'secure')
        });

        // Model info
        if (data.model_info) {
          setModelInfo({ ...data.model_info, metrics: data.metrics });
        }

        // Stats
        if (data.stats) {
          setLogStats(data.stats);
        }
      } catch (e) {
        // silent
      }
    }, 2000);
    return () => clearInterval(id);
  }, []);

  /* ── Event Logs polling (fetches full log list from /api/logs) ── */
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch('/api/logs?limit=50');
        if (!res.ok) throw new Error();
        const data = await res.json();
        setEventLogs(data.logs);
        if (data.stats) setLogStats(data.stats);
      } catch (e) {
        // silent
      }
    };

    // Fetch immediately and then every 3 seconds
    fetchLogs();
    const id = setInterval(fetchLogs, 3000);
    return () => clearInterval(id);
  }, []);

  /* ── Presets ── */
  const loadPreset = (type) => {
    setActivePreset(type);
    if (type === 'normal') {
      setInputs({ duration: 0.02, src_bytes: 0.05, dst_bytes: 0.8, num_failed_logins: 0.0, num_file_creations: 0.0, num_shells: 0.0, is_guest_login: 0.0, count: 0.1, srv_count: 0.15, dst_host_count: 0.85 });
    } else {
      setInputs({ duration: 0.85, src_bytes: 0.75, dst_bytes: 0.0, num_failed_logins: 0.8, num_file_creations: 0.6, num_shells: 0.9, is_guest_login: 0.0, count: 0.95, srv_count: 0.05, dst_host_count: 0.1 });
    }
  };

  /* ── Manual Analysis ── */
  const runAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs)
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setPrediction(data);
    } catch (e) {
      console.error("Analysis error:", e);
    }
    setIsAnalyzing(false);
  };

  /* ── Derived state ── */
  const shapData = prediction?.shap_data ?? [];
  const maxShap = shapData.length > 0 ? Math.max(...shapData.map(d => Math.abs(d["SHAP Value"] ?? 0))) || 1 : 1;

  const getRiskColor = (score) => {
    if (score > 70) return '#FF3366';
    if (score > 30) return '#FFB020';
    return '#00E599';
  };

  const safeMetric = (val) => {
    return typeof val === 'number' && isFinite(val) ? (val * 100).toFixed(1) : '—';
  };

  /* ═══════════════════════════════════════════
     RENDER
     ═══════════════════════════════════════════ */
  return (
    <div className="app-container">
      {/* ─── Sidebar ─── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/sentrax_logo.png" alt="SentraX Logo" className="brand-logo-img" />
          <div className="brand-text">
            <h1>SentraX</h1>
            <span>Security Engine</span>
          </div>
        </div>

        <div className="nav-group">
          <div className="nav-label">Core</div>
          <ul className="nav-items">
            <li className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
              <LayoutDashboard size={16} strokeWidth={2} /> Dashboard
            </li>
            <li className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
              <ScrollText size={16} strokeWidth={2} /> Event Logs
            </li>
          </ul>
        </div>

        <div className="nav-group">
          <div className="nav-label">Model Insights</div>
          <div className="model-stats-sidebar">
            <div className="stat-mini">
              <span className="mini-label">Accuracy</span>
              <span className="mini-val">{safeMetric(modelInfo.metrics?.accuracy)}%</span>
            </div>
            <div className="stat-mini">
              <span className="mini-label">F1 Score</span>
              <span className="mini-val">{safeMetric(modelInfo.metrics?.f1)}%</span>
            </div>
            <div className="stat-mini">
              <span className="mini-label">Predictions</span>
              <span className="mini-val">{logStats.total_predictions}</span>
            </div>
            <div className="stat-mini">
              <span className="mini-label">Attacks</span>
              <span className="mini-val" style={{ color: '#FF3366' }}>{logStats.total_attacks}</span>
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="system-status-indicator">
            <div className="status-dot"></div>
            {modelInfo.type} / {modelInfo.status}
          </div>
        </div>
      </aside>

      {/* ─── Main Content ─── */}
      <main className="main-wrapper">
        <header className="top-header">
          <div className="header-title">
            <h2>Security Operations Center</h2>
            <p>Real-time AI Inference Pipeline | {modelInfo.dataset} Dataset</p>
          </div>
          <div className="header-actions">
            <div className="risk-indicator-box">
              <span className="risk-label">RISK SCORE</span>
              <div className="risk-score-display" style={{ color: getRiskColor(riskData.score) }}>
                {riskData.score}
              </div>
              <div className="risk-bar-bg">
                <div className="risk-bar-fill" style={{ width: `${riskData.score}%`, backgroundColor: getRiskColor(riskData.score) }}></div>
              </div>
            </div>
          </div>
        </header>

        <div className="content-area">

          {/* ═══════════════════════════════════════
             TAB: DASHBOARD
             ═══════════════════════════════════════ */}
          {activeTab === 'dashboard' && (
            <div className="dashboard-grid">

              {/* KPI Row */}
              <div className="kpi-row">
                <div className="kpi-card">
                  <div className="kpi-header">
                    <div className="kpi-icon" style={{ color: '#5E6AD2' }}><Server size={18} strokeWidth={2.5} /></div>
                    <div className="kpi-label">Model Type</div>
                  </div>
                  <div className="kpi-value" style={{ fontSize: '1.2rem' }}>{modelInfo.type}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-header">
                    <div className="kpi-icon" style={{ color: '#00E599' }}><Database size={18} strokeWidth={2.5} /></div>
                    <div className="kpi-label">Training Set</div>
                  </div>
                  <div className="kpi-value" style={{ fontSize: '1.2rem' }}>{modelInfo.dataset}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-header">
                    <div className="kpi-icon" style={{ color: '#FFB020' }}><Zap size={18} strokeWidth={2.5} /></div>
                    <div className="kpi-label">Total Predictions</div>
                  </div>
                  <div className="kpi-value" style={{ fontSize: '1.2rem' }}>{logStats.total_predictions}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-header">
                    <div className="kpi-icon" style={{ color: '#FF3366' }}><AlertTriangle size={18} strokeWidth={2.5} /></div>
                    <div className="kpi-label">Attacks Detected</div>
                  </div>
                  <div className="kpi-value" style={{ fontSize: '1.2rem', color: '#FF3366' }}>{logStats.total_attacks}</div>
                </div>
              </div>

              {/* Middle Row: Chart + Live Feed */}
              <div className="middle-row">
                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title"><Activity size={16} strokeWidth={2.5} /> Live Traffic Analytics</div>
                    <span className="panel-action">STREAM • 2s</span>
                  </div>
                  <div className="panel-body no-pad">
                    <div className="chart-container">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
                          <defs>
                            <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#5E6AD2" stopOpacity={0.4} />
                              <stop offset="100%" stopColor="#5E6AD2" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" vertical={false} />
                          <XAxis dataKey="time" hide />
                          <YAxis stroke="#888888" fontSize={10} axisLine={false} tickLine={false} tickFormatter={(val) => `${val} M`} />
                          <Tooltip content={<CustomTooltip />} />
                          <Area type="monotone" dataKey="val" stroke="#5E6AD2" strokeWidth={1.5} fillOpacity={1} fill="url(#colorVal)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title"><TerminalSquare size={16} strokeWidth={2.5} /> Threat Feed</div>
                    <span className="panel-action">LIVE</span>
                  </div>
                  <div className="panel-body no-pad">
                    <div className="feed-list">
                      {liveFeed.length === 0 ? (
                        <div className="empty-state" style={{ minHeight: '200px' }}>
                          <div className="empty-icon">📡</div>
                          <p>Awaiting network events...</p>
                        </div>
                      ) : (
                        liveFeed.map((entry, idx) => (
                          <div key={idx} className={`feed-item ${entry.label === 'Attack' ? 'alert' : ''}`}>
                            <div className="feed-content">
                              <div className="feed-event">{entry.event}</div>
                              <div className="feed-meta mono" style={{ fontSize: '0.7rem' }}>
                                {entry.source_ip} → {entry.dest_ip} • {entry.protocol}:{entry.port}
                              </div>
                            </div>
                            <div className="feed-right">
                              <span className="feed-time mono">{entry.timestamp}</span>
                              <span className={`feed-badge ${severityClass(entry.severity)}`}>{entry.severity}</span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Row: Manual Analysis + XAI */}
              <div className="bottom-row">
                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title"><Search size={16} strokeWidth={2.5} /> Manual Inference Engine</div>
                  </div>
                  <div className="panel-body">
                    <div className="form-section">
                      <div className="preset-controls">
                        <button className={`btn btn-sm btn-outline ${activePreset === 'normal' ? 'active' : ''}`} onClick={() => loadPreset('normal')}>🟢 Normal</button>
                        <button className={`btn btn-sm btn-outline ${activePreset === 'attack' ? 'active' : ''}`} onClick={() => loadPreset('attack')}>🔴 Intrusion</button>
                      </div>
                      <div className="input-grid">
                        <InputField label="Duration" field="duration" value={inputs.duration} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Src Bytes" field="src_bytes" value={inputs.src_bytes} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Dst Bytes" field="dst_bytes" value={inputs.dst_bytes} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Host Conn Count" field="count" value={inputs.count} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Srv Conn Count" field="srv_count" value={inputs.srv_count} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Dst Host Count" field="dst_host_count" value={inputs.dst_host_count} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Failed Logins" field="num_failed_logins" value={inputs.num_failed_logins} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                        <InputField label="Shell Sessions" field="num_shells" value={inputs.num_shells} onChange={(f, v) => setInputs(p => ({ ...p, [f]: v }))} />
                      </div>
                      <button className="btn btn-primary" onClick={runAnalysis} disabled={isAnalyzing}>
                        {isAnalyzing ? 'Running Model...' : 'Execute Deep Inspection'}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title"><AlertTriangle size={16} strokeWidth={2.5} /> XAI Insight (Explainability)</div>
                  </div>
                  <div className="panel-body">
                    {!prediction ? (
                      <div className="empty-state">
                        <Radio size={48} strokeWidth={1} style={{ marginBottom: '1rem', opacity: 0.3 }} />
                        <p>Run inference to generate SHAP explanations.</p>
                      </div>
                    ) : (
                      <div className="xai-container">
                        <div className={`verdict-banner ${prediction.label === 'Attack' ? 'attack' : 'normal'}`}>
                          <div className="verdict-info">
                            <div className="verdict-icon-container">
                              {prediction.label === 'Attack' ? <AlertTriangle size={24} /> : <Shield size={24} />}
                            </div>
                            <div className="verdict-text">
                              <h3>{prediction.label}: {prediction.category}</h3>
                              <p>Confidence: {(prediction.confidence * 100).toFixed(1)}%</p>
                            </div>
                          </div>
                        </div>

                        <div className="shap-section">
                          <div className="shap-header">
                            <span>SHAP Feature Breakdown</span>
                            <div className="shap-legend">
                              <div className="legend-item"><div className="legend-dot red" /> Attack</div>
                              <div className="legend-item"><div className="legend-dot green" /> Normal</div>
                            </div>
                          </div>
                          <div className="shap-list">
                            {shapData.slice(0, 5).map((item, i) => (
                              <ShapRow key={i} feature={item.Feature} value={item["SHAP Value"]} maxAbs={maxShap} />
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════
             TAB: EVENT LOGS
             ═══════════════════════════════════════ */}
          {activeTab === 'logs' && (
            <div className="logs-page">
              <div className="logs-header-bar">
                <div className="logs-title-area">
                  <h3><ScrollText size={20} strokeWidth={2} /> Event Logs</h3>
                  <p>{eventLogs.length} entries • Auto-refreshing every 3s</p>
                </div>
                <div className="logs-stats">
                  <div className="log-stat-chip">
                    <span className="log-stat-dot" style={{ background: '#00E599' }}></span>
                    Normal: {logStats.total_predictions - logStats.total_attacks}
                  </div>
                  <div className="log-stat-chip">
                    <span className="log-stat-dot" style={{ background: '#FF3366' }}></span>
                    Attacks: {logStats.total_attacks}
                  </div>
                </div>
              </div>

              <div className="logs-table-container" ref={logListRef}>
                <table className="logs-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Source IP</th>
                      <th>Dest IP</th>
                      <th>Protocol</th>
                      <th>Port</th>
                      <th>Category</th>
                      <th>Confidence</th>
                      <th>Severity</th>
                      <th>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eventLogs.map((log, idx) => (
                      <tr key={log.id ?? idx} className={`log-row ${log.label === 'Attack' ? 'log-row-attack' : ''}`}>
                        <td className="mono">{log.timestamp}</td>
                        <td className="mono">{log.source_ip}</td>
                        <td className="mono">{log.dest_ip}</td>
                        <td><span className="proto-badge">{log.protocol}</span></td>
                        <td className="mono">{log.port}</td>
                        <td>
                          <span className={`category-badge ${log.label === 'Attack' ? 'cat-attack' : 'cat-normal'}`}>
                            {log.category}
                          </span>
                        </td>
                        <td className="mono">{(log.confidence * 100).toFixed(1)}%</td>
                        <td>
                          <span className={`severity-pill ${severityClass(log.severity)}`}>
                            {log.severity}
                          </span>
                        </td>
                        <td>
                          <span className={`source-tag ${log.source === 'manual' ? 'source-manual' : 'source-sim'}`}>
                            {log.source === 'manual' ? '🔬 Manual' : '📡 Sim'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {eventLogs.length === 0 && (
                  <div className="empty-state" style={{ minHeight: '300px' }}>
                    <div className="empty-icon">📋</div>
                    <p>No logs yet. Predictions will appear here automatically.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
