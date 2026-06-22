import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  ShieldAlert, UserCheck, Activity, Share2, BookOpen, Edit3,
  FileText, UploadCloud, CheckCircle, Loader, AlertTriangle,
  Play, Zap, ChevronDown, ChevronUp, Globe, Database, Eye,
  RefreshCw, Clock, TrendingUp, Lock, ArrowRight, Search,
  Upload, X, FilePlus, FileCode, FileSpreadsheet, AlertCircle
} from 'lucide-react';

// ── Document Upload Panel ─────────────────────────────────────────────────────
function DocumentUploadPanel({ onTransactionsExtracted }) {
  const [dragging,   setDragging]   = useState(false);
  const [uploading,  setUploading]  = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error,      setError]      = useState(null);
  const [loadingSample, setLoadingSample] = useState(null);
  const inputRef = useRef(null);

  const FILE_TYPES = [
    { ext: '.pdf',  icon: FileText,       label: 'Bank Statement PDF',      color: '#FF4D4D', desc: 'SWIFT confirmations, corporate docs' },
    { ext: '.csv',  icon: FileSpreadsheet, label: 'TM System CSV Export',   color: '#10B981', desc: 'Actimize, FICO, Oracle FCCM' },
    { ext: '.txt',  icon: FileCode,        label: 'SWIFT MT103/MT202',      color: '#FFB020', desc: 'Raw correspondent bank messages' },
    { ext: '.json', icon: FileCode,        label: 'JSON API Export',        color: '#A78BFA', desc: 'Structured alert feeds' },
  ];

  const processFile = async (file) => {
    setUploading(true); setError(null); setUploadResult(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const resp = await fetch('http://localhost:8000/api/upload-document', {
        method: 'POST', body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'Upload failed');
      setUploadResult(data);
      if (data.transactions?.length > 0) {
        onTransactionsExtracted(data);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) processFile(file);
  }, []);

  const loadSample = async (type) => {
    setLoadingSample(type); setError(null);
    try {
      const r = await fetch(`http://localhost:8000/api/sample-document/${type}`);
      const data = await r.json();
      // Convert sample text to a Blob and upload
      const blob = new Blob([data.content], { type: 'text/plain' });
      const file = new File([blob], data.filename);
      await processFile(file);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div style={{
      background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 16, padding: '1.8rem', marginBottom: '1.25rem',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
        <div style={{ background: 'linear-gradient(135deg,#00C6FF,#0072FF)', borderRadius: 8, padding: '6px 8px', display: 'flex' }}>
          <Upload size={16} color="#fff" />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: '#e2e8f0' }}>
            Document Intelligence — Step 1: Upload Evidence
          </h3>
          <p style={{ margin: 0, fontSize: '0.75rem', color: '#6B7280' }}>
            Upload bank statements, SWIFT messages, or TM system exports. AI extracts transaction data automatically.
          </p>
        </div>
      </div>

      {/* Supported formats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '0.6rem', marginBottom: '1.2rem' }}>
        {FILE_TYPES.map((f, i) => {
          const Icon = f.icon;
          return (
            <div key={i} style={{
              background: f.color + '11', border: `1px solid ${f.color}33`,
              borderRadius: 10, padding: '0.75rem', textAlign: 'center',
            }}>
              <Icon size={18} color={f.color} style={{ marginBottom: 4 }} />
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: f.color }}>{f.label}</div>
              <div style={{ fontSize: '0.65rem', color: '#4B5563', marginTop: 2 }}>{f.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragging ? '#00C6FF' : 'rgba(255,255,255,0.12)'}`,
          borderRadius: 12, padding: '2rem', textAlign: 'center', cursor: 'pointer',
          background: dragging ? 'rgba(0,198,255,0.06)' : 'rgba(0,0,0,0.2)',
          transition: 'all 0.25s ease',
          boxShadow: dragging ? '0 0 20px rgba(0,198,255,0.2)' : 'none',
          marginBottom: '1rem',
        }}>
        <input ref={inputRef} type="file"
          accept=".pdf,.csv,.txt,.json,.swift,.mt103"
          style={{ display: 'none' }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) processFile(f); }} />

        {uploading ? (
          <div style={{ color: '#00C6FF' }}>
            <Loader size={28} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
            <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>Parsing document...</div>
            <div style={{ fontSize: '0.72rem', color: '#6B7280', marginTop: 4 }}>Extracting transaction data with AI</div>
          </div>
        ) : (
          <>
            <UploadCloud size={28} color={dragging ? '#00C6FF' : '#4B5563'} style={{ marginBottom: 8 }} />
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: dragging ? '#00C6FF' : '#9CA3AF' }}>
              {dragging ? 'Drop to parse document' : 'Drop file here or click to browse'}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#4B5563', marginTop: 4 }}>
              PDF, CSV, SWIFT MT103, JSON — max 10MB
            </div>
          </>
        )}
      </div>

      {/* Sample Documents */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: '#6B7280', fontWeight: 600 }}>Try a sample:</span>
        {[
          { type: 'swift', label: '⚡ SWIFT MT103', color: '#FFB020' },
          { type: 'csv',   label: '📊 TM Export CSV', color: '#10B981' },
          { type: 'json',  label: '₿ Crypto Alert JSON', color: '#A78BFA' },
        ].map(s => (
          <button key={s.type} onClick={() => loadSample(s.type)} disabled={!!loadingSample}
            style={{
              background: s.color + '15', border: `1px solid ${s.color}44`,
              borderRadius: 8, padding: '5px 12px', color: s.color,
              fontSize: '0.76rem', fontWeight: 700, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 5, transition: 'all 0.2s',
            }}>
            {loadingSample === s.type ? <Loader size={11} style={{ animation: 'spin 1s linear infinite' }} /> : null}
            {s.label}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div style={{ marginTop: '0.75rem', background: 'rgba(255,77,77,0.1)', border: '1px solid #FF4D4D44', borderRadius: 8, padding: '0.75rem', color: '#FF4D4D', fontSize: '0.8rem' }}>
          <AlertCircle size={13} style={{ display: 'inline', marginRight: 6 }} />{error}
        </div>
      )}

      {/* Extraction Result */}
      {uploadResult && (
        <div style={{ marginTop: '1rem', background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 12, padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
            <div>
              <CheckCircle size={15} color="#10B981" style={{ display: 'inline', marginRight: 6 }} />
              <span style={{ fontWeight: 700, color: '#10B981', fontSize: '0.85rem' }}>
                {uploadResult.message}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <span style={{ background: '#00C6FF22', color: '#00C6FF', border: '1px solid #00C6FF44', borderRadius: 6, padding: '2px 8px', fontSize: '0.7rem', fontWeight: 700 }}>
                {uploadResult.format}
              </span>
              <span style={{ background: '#10B98122', color: '#10B981', border: '1px solid #10B98144', borderRadius: 6, padding: '2px 8px', fontSize: '0.7rem', fontWeight: 700 }}>
                {(uploadResult.confidence * 100).toFixed(0)}% confidence
              </span>
              <span style={{ background: '#A78BFA22', color: '#A78BFA', border: '1px solid #A78BFA44', borderRadius: 6, padding: '2px 8px', fontSize: '0.7rem', fontWeight: 700 }}>
                {uploadResult.parse_method}
              </span>
            </div>
          </div>

          {/* Extracted transactions preview */}
          {uploadResult.transactions?.length > 0 && (
            <div style={{ maxHeight: 200, overflowY: 'auto' }}>
              {uploadResult.transactions.map((t, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.4rem 0.6rem', marginBottom: '0.3rem',
                  background: 'rgba(0,0,0,0.3)', borderRadius: 6,
                  fontSize: '0.75rem',
                }}>
                  <div>
                    <span style={{ color: '#9CA3AF', marginRight: 8 }}>{t.txn_id}</span>
                    <span style={{ color: '#e2e8f0', fontWeight: 600 }}>
                      {t.originator?.name || t.originator?.account || '?'} → {t.beneficiary?.name || t.beneficiary?.account || '?'}
                    </span>
                  </div>
                  <span style={{ color: '#FF4D4D', fontWeight: 700 }}>
                    ${(t.amount || 0).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: '0.75rem', padding: '0.6rem 0.75rem', background: 'rgba(0,198,255,0.08)', border: '1px solid rgba(0,198,255,0.2)', borderRadius: 8, fontSize: '0.76rem', color: '#00C6FF' }}>
            ✅ Transactions loaded into investigation. Select a scenario tab or click <strong>Start Investigation</strong> to run the 8-agent pipeline on this document.
          </div>
        </div>
      )}
    </div>
  );
}

// ── Pre-loaded Demo Scenarios ─────────────────────────────────────────────────
const SCENARIOS = {
  layering: {
    label: '🏝️ Cayman Layering',
    badge: 'SUSPECTED_LAYERING',
    color: '#FF4D4D',
    description: '4-hop wire: Cayman → Panama → Cyprus → Switzerland',
    case_id: 'CAS-2026-007',
    alert_type: 'SUSPECTED_LAYERING',
    transactions: [
      { txn_id:'TXN-201', date:'2026-06-10T09:00:00Z', amount:250000, type:'WIRE_IN',
        originator:{name:'Unknown Entity A', country:'Cayman Islands', account:'CY-999123'},
        beneficiary:{account:'ACC-554433'} },
      { txn_id:'TXN-202', date:'2026-06-11T11:30:00Z', amount:120000, type:'WIRE_OUT',
        originator:{account:'ACC-554433'},
        beneficiary:{name:'Shell Corp B', country:'Panama', account:'PA-888456'} },
      { txn_id:'TXN-203', date:'2026-06-11T14:45:00Z', amount:115000, type:'WIRE_OUT',
        originator:{account:'ACC-554433'},
        beneficiary:{name:'Holdings C', country:'Cyprus', account:'CP-777789'} },
      { txn_id:'TXN-204', date:'2026-06-12T10:15:00Z', amount:115000, type:'WIRE_OUT',
        originator:{name:'Shell Corp B', account:'PA-888456'},
        beneficiary:{name:'Final Dest D', country:'Switzerland', account:'CH-111222'} },
    ],
  },
  trade: {
    label: '📦 Trade-Based ML',
    badge: 'TRADE_BASED_ML',
    color: '#FFB020',
    description: 'Fake invoices from Iran → falsified trade docs',
    case_id: 'CAS-2026-019',
    alert_type: 'TRADE_BASED_MONEY_LAUNDERING',
    transactions: [
      { txn_id:'TXN-301', date:'2026-06-08T07:00:00Z', amount:890000, type:'WIRE_IN',
        originator:{name:'Aryan Trading Co', country:'Iran', account:'IR-445566'},
        beneficiary:{name:'Global Import LLC', country:'UAE', account:'AE-112233'} },
      { txn_id:'TXN-302', date:'2026-06-09T09:00:00Z', amount:870000, type:'WIRE_OUT',
        originator:{name:'Global Import LLC', account:'AE-112233'},
        beneficiary:{name:'Hezbollah Finance', country:'Lebanon', account:'LB-998877'} },
      { txn_id:'TXN-303', date:'2026-06-10T11:00:00Z', amount:850000, type:'WIRE_OUT',
        originator:{name:'Hezbollah Finance', account:'LB-998877'},
        beneficiary:{name:'Offshore Shell X', country:'BVI', account:'VG-556644'} },
    ],
  },
  crypto: {
    label: '₿ Crypto Off-Ramp',
    badge: 'CRYPTO_ML',
    color: '#A78BFA',
    description: 'BTC mixer → OTC desk → bank wire chain',
    case_id: 'CAS-2026-031',
    alert_type: 'CRYPTOCURRENCY_MONEY_LAUNDERING',
    transactions: [
      { txn_id:'TXN-401', date:'2026-06-14T03:00:00Z', amount:2100000, type:'CRYPTO_IN',
        originator:{name:'Tornado Cash Mixer', country:'Decentralized', account:'0xAB...FF11'},
        beneficiary:{name:'OTC Desk Alpha', country:'Hong Kong', account:'HK-OTC-001'} },
      { txn_id:'TXN-402', date:'2026-06-14T06:30:00Z', amount:2050000, type:'WIRE_OUT',
        originator:{name:'OTC Desk Alpha', account:'HK-OTC-001'},
        beneficiary:{name:'Cayman Holdings Y', country:'Cayman Islands', account:'CY-887755'} },
      { txn_id:'TXN-403', date:'2026-06-15T10:00:00Z', amount:2000000, type:'WIRE_OUT',
        originator:{name:'Cayman Holdings Y', account:'CY-887755'},
        beneficiary:{name:'PJSC Gazprombank', country:'Russia', account:'RU-GAZP-999'} },
    ],
  },
  cyber: {
    label: '🚨 REAL WORLD: FBI Cyber',
    badge: 'CYBER_RANSOMWARE',
    color: '#FF4D4D',
    description: 'Real-world data: Zeus Trojan ransomware laundering',
    case_id: 'CAS-FBI-001',
    alert_type: 'CYBER_EXTORTION_LAUNDERING',
    transactions: [
      { txn_id:'TXN-501', date:'2026-06-20T08:00:00Z', amount:3000000, type:'CRYPTO_IN',
        originator:{name:'Ransomware Victim', country:'USA', account:'US-BANK-111'},
        beneficiary:{name:'BOGACHEV', country:'Russia', account:'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'} },
      { txn_id:'TXN-502', date:'2026-06-21T09:00:00Z', amount:2900000, type:'CRYPTO_OUT',
        originator:{name:'BOGACHEV', account:'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'},
        beneficiary:{name:'Slavic Holdings LLC', country:'Cyprus', account:'CY-999-BOGA'} },
    ],
  },
};

const AGENTS = [
  { id:'maestro',    name:'UiPath Maestro',          icon:Zap,         desc:'Orchestrator Case Plan + HITL Gate', color:'#fa709a' },
  { id:'triage',     name:'1. Triage Analyst',        icon:ShieldAlert,  desc:'Entity extraction & case context',   color:'#4facfe' },
  { id:'sanctions',  name:'2. Sanctions Screener',    icon:Search,       desc:'REAL OFAC SDN API — exponential backoff', color:'#f59e0b' },
  { id:'pattern',    name:'3. Pattern Detection',     icon:Activity,     desc:'Llama 3.1 writes live detection code', color:'#a78bfa' },
  { id:'network',    name:'4. Network Investigator',  icon:Share2,       desc:'BFS graph traversal across jurisdictions', color:'#34d399' },
  { id:'regulatory', name:'5. Regulatory Intel',      icon:BookOpen,     desc:'FinCEN 30-day SLA + BSA statute',    color:'#fb923c' },
  { id:'writer',     name:'6. SAR Writer',             icon:Edit3,        desc:'Llama 3.1 → FinCEN 6-question SAR', color:'#60a5fa' },
  { id:'populator',  name:'7. Form 111 Populator',    icon:FileText,     desc:'FinCEN Form 111 JSON schema mapping', color:'#4ade80' },
  { id:'submission', name:'8. Audit & Action Center', icon:UploadCloud,  desc:'Tracking ID + Action Center HITL task', color:'#f472b6' },
];

const JURISDICTION_FLAGS = {
  'Cayman Islands':  '🇰🇾', 'Panama': '🇵🇦', 'Cyprus': '🇨🇾',
  'Switzerland':     '🇨🇭', 'Iran':   '🇮🇷', 'UAE':    '🇦🇪',
  'Lebanon':         '🇱🇧', 'BVI':    '🇻🇬', 'Russia': '🇷🇺',
  'Hong Kong':       '🇭🇰', 'Decentralized': '🌐',
};
const JURISDICTION_RISK = {
  'Cayman Islands':4,'Panama':5,'Cyprus':3,'Switzerland':2,'Iran':10,
  'UAE':4,'Lebanon':7,'BVI':4,'Russia':9,'Hong Kong':3,'Decentralized':8,
};

function getRiskColor(s) {
  if (s >= 85) return '#FF4D4D';
  if (s >= 60) return '#FFB020';
  return '#10B981';
}

function Badge({ color, children }) {
  return (
    <span style={{
      background: color + '22', color, border: `1px solid ${color}55`,
      borderRadius: 6, padding: '3px 10px', fontSize: '0.75rem',
      fontWeight: 700, letterSpacing: '0.04em', whiteSpace: 'nowrap',
    }}>{children}</span>
  );
}

function Collapse({ title, children, defaultOpen = true, accent }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ borderRadius: 12, overflow: 'hidden', marginBottom: '1rem',
      border: `1px solid ${accent || 'rgba(255,255,255,0.08)'}`, }}>
      <button onClick={() => setOpen(o => !o)} style={{
        width: '100%', textAlign: 'left', background: `${accent || 'rgba(255,255,255,0.03)'}11`,
        border: 'none', color: '#e2e8f0', fontWeight: 700, fontSize: '0.9rem',
        padding: '0.9rem 1.2rem', cursor: 'pointer', display: 'flex',
        justifyContent: 'space-between', alignItems: 'center',
        borderBottom: open ? `1px solid ${accent || 'rgba(255,255,255,0.08)'}` : 'none',
      }}>
        {title}
        {open ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>
      {open && <div style={{ padding: '1.2rem', background: 'rgba(0,0,0,0.2)' }}>{children}</div>}
    </div>
  );
}

// ── Animated Money Flow Graph ─────────────────────────────────────────────────
function MoneyFlowGraph({ transactions, running, done }) {
  const hops = [];
  const seen = new Set();
  for (const t of transactions) {
    const from = t.originator?.name || t.originator?.account || '?';
    const to   = t.beneficiary?.name || t.beneficiary?.account || '?';
    const fromC = t.originator?.country || '';
    const toC   = t.beneficiary?.country || '';
    const key = `${from}→${to}`;
    if (!seen.has(key)) { seen.add(key); hops.push({ from, to, fromC, toC, amount: t.amount, type: t.type }); }
  }

  // Build unique nodes
  const nodeNames = [];
  for (const h of hops) {
    if (!nodeNames.includes(h.from)) nodeNames.push(h.from);
    if (!nodeNames.includes(h.to))   nodeNames.push(h.to);
  }

  const nodeCount = nodeNames.length;
  const svgW = 600, svgH = 120;
  const nodeX = nodeNames.map((_, i) => 40 + (i / Math.max(nodeCount - 1, 1)) * (svgW - 80));
  const nodeY = svgH / 2;
  const nodeMap = Object.fromEntries(nodeNames.map((n, i) => [n, i]));
  const flag = (c) => JURISDICTION_FLAGS[c] || '🏳️';
  const riskC = (c) => {
    const r = JURISDICTION_RISK[c] || 3;
    if (r >= 8) return '#FF4D4D'; if (r >= 5) return '#FFB020'; return '#10B981';
  };

  return (
    <div style={{ position: 'relative' }}>
      <svg viewBox={`0 0 ${svgW} ${svgH + 40}`} style={{ width: '100%', overflow: 'visible' }}>
        <defs>
          <marker id="flow-arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <path d="M0,0 L0,6 L8,3 z" fill="#FF4D4D88" />
          </marker>
          {hops.map((_, i) => (
            <linearGradient key={i} id={`flow-grad-${i}`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FF4D4D" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#FFB020" stopOpacity="0.6" />
            </linearGradient>
          ))}
        </defs>

        {/* Flow arrows */}
        {hops.map((h, i) => {
          const x1 = nodeX[nodeMap[h.from]] + 18;
          const x2 = nodeX[nodeMap[h.to]] - 18;
          const animated = running || done;
          return (
            <g key={i}>
              <line x1={x1} y1={nodeY} x2={x2} y2={nodeY}
                stroke={`url(#flow-grad-${i})`} strokeWidth={2.5}
                strokeDasharray={animated ? '8 4' : '4 4'}
                markerEnd="url(#flow-arr)"
                style={{ animation: animated ? 'flowDash 1.2s linear infinite' : 'none' }}
              />
              <text x={(x1 + x2) / 2} y={nodeY - 10} textAnchor="middle"
                fill="#FFB020" fontSize={9} fontWeight={700}>
                ${(h.amount / 1000).toFixed(0)}k
              </text>
            </g>
          );
        })}

        {/* Nodes */}
        {nodeNames.map((name, i) => {
          const hop = hops.find(h => h.from === name || h.to === name);
          const country = hop?.fromC === name ? hop?.fromC : hop?.toC;
          const isSource = nodeMap[name] === 0;
          const isDest   = nodeMap[name] === nodeNames.length - 1;
          const nColor   = isSource ? '#FF4D4D' : isDest ? '#A78BFA' : '#FFB020';
          return (
            <g key={name}>
              <circle cx={nodeX[i]} cy={nodeY} r={18}
                fill={nColor + '22'} stroke={nColor} strokeWidth={1.5}
                style={{ filter: (running || done) ? `drop-shadow(0 0 6px ${nColor})` : 'none' }}
              />
              <text x={nodeX[i]} y={nodeY + 4} textAnchor="middle" fontSize={10}>
                {flag(country || '')}
              </text>
              <text x={nodeX[i]} y={nodeY + 34} textAnchor="middle"
                fill="#9CA3AF" fontSize={8}>
                {name.length > 12 ? name.slice(0, 12) + '…' : name}
              </text>
            </g>
          );
        })}
      </svg>
      <style>{`
        @keyframes flowDash {
          from { stroke-dashoffset: 24; }
          to   { stroke-dashoffset: 0; }
        }
      `}</style>
    </div>
  );
}

// ── Risk Score Gauge ──────────────────────────────────────────────────────────
function RiskGauge({ score, color }) {
  const [displayed, setDisplayed] = useState(0);
  useEffect(() => {
    if (!score) return;
    let cur = 0;
    const step = Math.ceil(score / 40);
    const id = setInterval(() => {
      cur = Math.min(cur + step, score);
      setDisplayed(cur);
      if (cur >= score) clearInterval(id);
    }, 30);
    return () => clearInterval(id);
  }, [score]);

  const r = 52, cx = 70, cy = 70;
  const circ = 2 * Math.PI * r;
  const pct  = displayed / 100;
  const dash  = circ * pct;

  return (
    <div style={{ textAlign: 'center', position: 'relative' }}>
      <svg width={140} height={140} viewBox="0 0 140 140">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={10} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={10}
          strokeDasharray={`${dash} ${circ - dash}`}
          strokeDashoffset={circ * 0.25}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.05s', filter: `drop-shadow(0 0 8px ${color})` }}
        />
        <text x={cx} y={cy - 6} textAnchor="middle" fill={color} fontSize={26} fontWeight={900}>
          {displayed}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fill="#64748b" fontSize={11}>
          /100
        </text>
        <text x={cx} y={cy + 28} textAnchor="middle" fill={color} fontSize={9} fontWeight={700}>
          RISK SCORE
        </text>
      </svg>
    </div>
  );
}

// ── Orchestrator Job Status Panel ─────────────────────────────────────────────
function OrchestratorPanel({ jobKey, running }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const poll = useCallback(async () => {
    if (!jobKey || jobKey === 'N/A') return;
    setLoading(true);
    try {
      const r = await fetch(`http://localhost:8000/api/job-status/${jobKey}`);
      const d = await r.json();
      setStatus(d);
    } catch {
      setStatus({ state: 'unknown', error: 'cannot reach backend' });
    }
    setLoading(false);
  }, [jobKey]);

  useEffect(() => {
    if (jobKey && jobKey !== 'N/A') {
      poll();
      const id = setInterval(poll, 8000);
      return () => clearInterval(id);
    }
  }, [jobKey, poll]);

  if (!jobKey || jobKey === 'N/A') return null;

  const stateColor = { Suspended: '#FFB020', Running: '#4facfe', Successful: '#10B981', Faulted: '#FF4D4D' };
  const sc = stateColor[status?.state] || '#64748b';

  return (
    <div style={{
      background: 'rgba(255,176,32,0.07)', border: '1px solid rgba(255,176,32,0.25)',
      borderRadius: 12, padding: '1.2rem', marginTop: '1rem',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontWeight: 700, color: '#FFB020', fontSize: '0.85rem' }}>
          ⚙️ UiPath Orchestrator — Job Status
        </span>
        <button onClick={poll} disabled={loading} style={{
          background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 6, padding: '4px 10px', color: '#9CA3AF', cursor: 'pointer', fontSize: '0.78rem',
        }}>
          {loading ? '...' : '↻ Refresh'}
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.6rem', fontSize: '0.8rem' }}>
        {[
          { l: 'Process', v: 'agent_6_sar_signature_hitl', c: '#60a5fa' },
          { l: 'Job Key', v: jobKey.slice(0, 8) + '...', c: '#9CA3AF' },
          { l: 'State', v: status?.state || 'Checking...', c: sc },
        ].map((r, i) => (
          <div key={i} style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 8, padding: '0.6rem' }}>
            <div style={{ color: '#4a5568', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{r.l}</div>
            <div style={{ fontWeight: 700, color: r.c, marginTop: 2 }}>{r.v}</div>
          </div>
        ))}
      </div>
      {status?.state === 'Suspended' && (
        <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(255,176,32,0.1)',
          border: '1px solid rgba(255,176,32,0.3)', borderRadius: 8, fontSize: '0.82rem', color: '#FFB020' }}>
          🔔 <strong>Waiting in Action Center</strong> — BSA Officer must review and approve the SAR before filing proceeds.
          <div style={{ fontSize: '0.72rem', color: '#9CA3AF', marginTop: 4 }}>
            Open UiPath Action Center → Tasks → BSA SAR Review to approve
          </div>
        </div>
      )}
    </div>
  );
}

// ── Architecture SVG ──────────────────────────────────────────────────────────
function ArchDiagram() {
  const nodes = [
    { x: 10,  y: 20,  w: 120, h: 38, label: 'React Dashboard',    sub: 'Doc Upload + Analyst', color: '#4facfe' },
    { x: 180, y: 20,  w: 130, h: 38, label: 'FastAPI + LangGraph', sub: '8-Agent Pipeline',     color: '#a78bfa' },
    { x: 360, y: 20,  w: 130, h: 38, label: 'AWS Bedrock',         sub: 'Llama 3.1 70B',        color: '#f59e0b' },
    { x: 10,  y: 98,  w: 120, h: 38, label: 'Doc Intelligence',    sub: 'PDF·CSV·SWIFT·JSON',   color: '#00C6FF' },
    { x: 180, y: 98,  w: 130, h: 38, label: 'UiPath Maestro',      sub: 'Case Orchestrator',    color: '#fa709a' },
    { x: 360, y: 98,  w: 130, h: 38, label: 'Action Center',       sub: 'BSA Officer HITL',     color: '#34d399' },
  ];
  const arrows = [
    [130, 39, 180, 39], [310, 39, 360, 39],
    [130, 117, 180, 117], [310, 117, 360, 117],
    [70,  58, 70,  98],   // Doc Intelligence feeds Dashboard
    [245, 58, 245, 98],   // FastAPI feeds Maestro
  ];
  return (
    <svg viewBox="0 0 510 155" style={{ width: '100%', maxWidth: 510 }}>
      <defs>
        <marker id="arr2" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto">
          <path d="M0,0 L0,6 L7,3 z" fill="rgba(255,255,255,0.35)" />
        </marker>
      </defs>
      {arrows.map(([x1, y1, x2, y2], i) => (
        <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(255,255,255,0.25)"
          strokeWidth={1.5} strokeDasharray="5 3" markerEnd="url(#arr2)" />
      ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={8}
            fill={n.color + '18'} stroke={n.color + '66'} strokeWidth={1.5} />
          <text x={n.x + n.w / 2} y={n.y + 15} textAnchor="middle" fill="#e2e8f0" fontSize={9.5} fontWeight={700}>{n.label}</text>
          <text x={n.x + n.w / 2} y={n.y + 29} textAnchor="middle" fill={n.color} fontSize={8}>{n.sub}</text>
        </g>
      ))}
      <text x={255} y={150} textAnchor="middle" fill="rgba(255,255,255,0.2)" fontSize={8}>
        ← All decisions logged in UiPath Orchestrator Audit Trail →
      </text>
    </svg>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// Main App
// ══════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [scenario,     setScenario]     = useState('layering');
  const [agentStates,  setAgentStates]  = useState(AGENTS.map(() => 'idle'));
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState(null);
  const [running,      setRunning]      = useState(false);
  const [resilience,   setResilience]   = useState(false);
  const [logs,         setLogs]         = useState([]);
  const [uploadedCase, setUploadedCase] = useState(null); // From document upload
  const [uploadedDocs, setUploadedDocs] = useState([]);   // Evidence locker
  const logsRef = useRef(null);

  // The active case: uploaded doc takes priority over preset scenario
  const CASE = uploadedCase || SCENARIOS[scenario];
  const totalAmount = CASE.transactions.reduce((s, t) => s + t.amount, 0);

  // Called when DocumentUploadPanel successfully extracts transactions
  const handleDocumentExtracted = (uploadResult) => {
    const newCase = {
      label:       `📄 ${uploadResult.filename}`,
      badge:       'DOCUMENT_UPLOAD',
      color:       '#00C6FF',
      description: `${uploadResult.tx_count} transactions extracted via ${uploadResult.parse_method}`,
      case_id:     `CAS-DOC-${Date.now().toString(36).toUpperCase()}`,
      alert_type:  'DOCUMENT_UPLOAD',
      transactions: uploadResult.transactions,
    };
    setUploadedCase(newCase);
    setUploadedDocs(prev => [...prev, { ...uploadResult, case_id: newCase.case_id }]);
    setResult(null); setLogs([]); setError(null);
    setAgentStates(AGENTS.map(() => 'idle'));
  };

  const clearUpload = () => { setUploadedCase(null); };

  useEffect(() => {
    if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight;
  }, [logs]);

  const addLog = (msg, type = 'info') =>
    setLogs(l => [...l, { msg, type, t: new Date().toLocaleTimeString() }]);

  const startInvestigation = async () => {
    setRunning(true); setResult(null); setError(null); setLogs([]);
    setAgentStates(AGENTS.map(() => 'idle'));
    addLog(`🚀 Starting investigation: ${CASE.label}`, 'info');
    addLog('🔗 Connecting to FastAPI backend (port 8000)...', 'info');

    try {
      const resp = await fetch('http://localhost:8000/api/investigate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...CASE, resilience_mode: resilience }),
      });
      if (!resp.ok) throw new Error(`Backend returned HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split('\n\n');
        buf = parts.pop();

        for (const chunk of parts) {
          let evType = '', dStr = '';
          for (const line of chunk.split('\n')) {
            if (line.startsWith('event:')) evType = line.slice(6).trim();
            if (line.startsWith('data:'))  dStr   = line.slice(5).trim();
          }
          if (!dStr) continue;
          const data = JSON.parse(dStr);

          if (evType === 'agent_start') {
            setAgentStates(p => { const n = [...p]; n[data.agent] = 'active'; return n; });
            addLog(`⚡ [${data.name}] — running`, 'start');
          } else if (evType === 'agent_pause') {
            setAgentStates(p => { const n = [...p]; n[data.agent] = 'suspended'; return n; });
            addLog(`🔔 [${data.name}] — SUSPENDED. Waiting in UiPath Action Center...`, 'error');
          } else if (evType === 'agent_resume') {
            setAgentStates(p => { const n = [...p]; n[data.agent] = 'active'; return n; });
            addLog(`✅ [${data.name}] — APPROVED in Action Center! Resuming...`, 'start');
          } else if (evType === 'agent_done') {
            setAgentStates(p => { const n = [...p]; n[data.agent] = 'done'; return n; });
            const detail = data.detail ? ` — ${data.detail}` : '';
            addLog(`✅ [${data.name}] complete${detail}`, 'done');
          } else if (evType === 'agent_error') {
            setAgentStates(p => { const n = [...p]; n[data.agent] = 'error'; return n; });
            addLog(`❌ [${data.name}] ${data.error}`, 'error');
          } else if (evType === 'agent_log') {
            addLog(data.msg, data.type || 'info');
          } else if (evType === 'result') {
            setResult(data);
            addLog(`🏁 Complete! FinCEN: ${data.fincen_tracking_id} | Action Center Job: ${data.action_center_item_id}`, 'done');
            setAgentStates(AGENTS.map(() => 'done'));
          }
        }
      }
    } catch (err) {
      setError(err.message);
      addLog(`❌ ${err.message}`, 'error');
    } finally {
      setRunning(false);
    }
  };

  const riskColor = result ? getRiskColor(result.final_risk_score) : '#4facfe';
  const uniqueJurisdictions = [...new Set(
    CASE.transactions.flatMap(t => [t.originator?.country, t.beneficiary?.country].filter(Boolean))
  )];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at 10% 0%, rgba(37,99,235,0.15) 0%, transparent 50%), radial-gradient(ellipse at 90% 10%, rgba(168,85,247,0.15) 0%, transparent 50%), #0F172A',
      fontFamily: "'Inter', system-ui, sans-serif",
      color: '#F8FAFC',
      backgroundAttachment: 'fixed',
    }}>
      {/* ── HERO HEADER ── */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(0,114,255,0.1), rgba(157,80,187,0.07), rgba(250,112,154,0.05))',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        padding: '1.8rem 2rem 1.5rem',
      }}>
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            {/* Brand */}
            <div>
              <h1 style={{
                background: 'linear-gradient(135deg, #00C6FF 0%, #0072FF 50%, #9D50BB 100%)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                margin: 0, fontSize: '2.6rem', fontWeight: 900, letterSpacing: '-1.5px',
              }}>🛡️ SentinelFin</h1>
              <p style={{ margin: '0.3rem 0 0', color: '#9CA3AF', fontSize: '0.95rem', fontWeight: 300 }}>
                Autonomous AML Compliance · 8-Agent LangGraph + Llama 3.1 + UiPath Maestro + Real OFAC SDN API
              </p>
            </div>

            {/* Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              {/* Scenario Selector */}
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {Object.entries(SCENARIOS).map(([key, sc]) => (
                  <button key={key} onClick={() => { setScenario(key); setResult(null); setLogs([]); setAgentStates(AGENTS.map(() => 'idle')); }}
                    style={{
                      background: scenario === key ? sc.color + '22' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${scenario === key ? sc.color + '77' : 'rgba(255,255,255,0.1)'}`,
                      borderRadius: 8, padding: '7px 13px', color: scenario === key ? sc.color : '#8b9bb4',
                      fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s',
                    }}>
                    {sc.label}
                  </button>
                ))}
              </div>

              {/* Resilience Toggle */}
              <label style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer',
                background: resilience ? 'rgba(255,77,77,0.1)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${resilience ? '#FF4D4D55' : 'rgba(255,255,255,0.1)'}`,
                borderRadius: 8, padding: '7px 13px', transition: 'all 0.2s',
              }}>
                <input type="checkbox" checked={resilience}
                  onChange={e => setResilience(e.target.checked)}
                  style={{ accentColor: '#FF4D4D' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: resilience ? '#FF4D4D' : '#8b9bb4' }}>
                  🔴 Resilience Demo
                </span>
              </label>

              {/* Start Button */}
              <button id="start-investigation-btn" onClick={startInvestigation} disabled={running}
                style={{
                  background: running ? 'rgba(255,255,255,0.08)' : 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
                  border: 'none', borderRadius: 10, padding: '11px 26px',
                  color: running ? '#8b9bb4' : '#fff', fontWeight: 800, fontSize: '0.95rem',
                  cursor: running ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', gap: 8,
                  boxShadow: running ? 'none' : '0 4px 20px rgba(255,107,107,0.45)',
                  transition: 'all 0.25s cubic-bezier(0.175,0.885,0.32,1.275)',
                  textTransform: 'uppercase', letterSpacing: '0.08em',
                }}>
                {running ? <><Loader size={15} style={{ animation: 'spin 1s linear infinite' }} />Investigating...</>
                         : <><Play size={15} />Start Investigation</>}
              </button>
            </div>
          </div>

          {/* Problem Statement Bar */}
          <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: '0.75rem' }}>
            {[
              { icon: '📊', label: 'False Positive Rate', val: '95%', sub: 'Traditional rule-based AML', color: '#FF4D4D' },
              { icon: '⏱️', label: 'Manual Investigation', val: '4+ hrs', sub: 'Per case, per analyst', color: '#FFB020' },
              { icon: '⚡', label: 'SentinelFin Resolution', val: '<60 sec', sub: 'Full 8-agent AI pipeline', color: '#10B981' },
              { icon: '🏛️', label: 'Compliance Risk', val: '$10M+', sub: 'Per FinCEN filing failure', color: '#A78BFA' },
            ].map((s, i) => (
              <div key={i} style={{
                background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
                borderLeft: `3px solid ${s.color}`, borderRadius: 10, padding: '0.9rem 1rem',
                display: 'flex', alignItems: 'center', gap: '0.8rem',
              }}>
                <span style={{ fontSize: '1.6rem' }}>{s.icon}</span>
                <div>
                  <div style={{ fontSize: '0.68rem', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{s.label}</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 900, color: s.color, lineHeight: 1.1 }}>{s.val}</div>
                  <div style={{ fontSize: '0.68rem', color: '#4B5563', marginTop: 1 }}>{s.sub}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── MAIN 3-PANEL LAYOUT ── */}
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '1.8rem 2rem' }}>

        {/* Document Upload Panel — Step 1 */}
        <DocumentUploadPanel onTransactionsExtracted={handleDocumentExtracted} />

        {/* Uploaded Document Active Badge */}
        {uploadedCase && (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '0.75rem 1rem', marginBottom: '1.25rem',
            background: 'rgba(0,198,255,0.08)', border: '1px solid rgba(0,198,255,0.3)',
            borderRadius: 10,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '1.1rem' }}>📄</span>
              <div>
                <div style={{ fontWeight: 700, color: '#00C6FF', fontSize: '0.88rem' }}>
                  Document-Driven Investigation Active: {uploadedCase.case_id}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#6B7280' }}>
                  {uploadedCase.description} — Click Start Investigation to analyse
                </div>
              </div>
            </div>
            <button onClick={clearUpload} style={{
              background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 6, padding: '4px 10px', color: '#9CA3AF', cursor: 'pointer', fontSize: '0.76rem',
            }}>
              ✕ Clear Upload
            </button>
          </div>
        )}

        {/* Row 1: Architecture + Case Overview */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
          {/* Architecture */}
          <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 14, padding: '1.4rem' }}>
            <h3 style={{ margin: '0 0 1rem', fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              🏗️ System Architecture — Cross-Platform Integration
            </h3>
            <ArchDiagram />
          </div>

          {/* Case Overview */}
          <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 14, padding: '1.4rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {[
                { l: 'Pattern', v: result ? result.pattern_name : 'Scanning...', c: '#A78BFA' },
                { l: 'Network Depth', v: result ? `${result.network_depth} hops` : 'Analyzing...', c: '#4facfe' },
                { l: 'FinCEN 111', v: result && result.fincen_tracking_id ? 'Ready' : 'Pending...', c: '#10B981' },
                { l: 'Orchestrator Job',  v: result ? `Job ${result.action_center_item_id?.slice(0, 8)}…` : 'Pending...', c: '#34d399' },
              ].map((r, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 8, padding: '0.6rem' }}>
                  <div style={{ fontSize: '0.68rem', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{r.l}</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: r.c }}>{r.v}</div>
                </div>
              ))}
            </div>
            <h3 style={{ margin: '0 0 0.8rem', fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              📋 Active Case — {CASE.case_id}
            </h3>
            <div style={{ marginBottom: '0.8rem' }}>
              <Badge color={CASE.color}>{CASE.badge.replace(/_/g, ' ')}</Badge>
              <span style={{ marginLeft: 8, fontSize: '0.78rem', color: '#6B7280' }}>{CASE.description}</span>
            </div>
            {[
              { l: 'Total Volume',   v: `$${totalAmount.toLocaleString()}`, c: '#FF4D4D' },
              { l: 'Transactions',   v: `${CASE.transactions.length} transfers`, c: '#4facfe' },
              { l: 'Risk Score',     v: result ? `${result.final_risk_score}/100` : 'Pending...', c: result ? riskColor : '#4a5568' },
              { l: 'Sanctions Hit',  v: result ? (result.sanctions_hits ? '⚠️ YES — OFAC SDN' : '✅ None Found') : 'Pending...', c: result?.sanctions_hits ? '#FF4D4D' : '#10B981' },
              { l: 'FinCEN SLA',     v: result ? `${result.sla_status} (${result.days_remaining}d)` : 'Pending...', c: '#FFB020' },
              { l: 'Action Center',  v: result ? `Job ${result.action_center_item_id?.slice(0, 8)}…` : 'Pending...', c: '#34d399' },
            ].map((r, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <span style={{ color: '#6B7280', fontSize: '0.82rem' }}>{r.l}</span>
                <span style={{ color: r.c, fontWeight: 700, fontSize: '0.82rem' }}>{r.v}</span>
              </div>
            ))}
          </div>
        </div>



        {/* Row 3: Agent Pipeline */}
        <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 14, padding: '1.4rem', marginBottom: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            🤖 LangGraph Multi-Agent Pipeline — UiPath Maestro Orchestrated
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '0.7rem' }}>
            {AGENTS.map((agent, idx) => {
              const st = agentStates[idx];
              const Icon = agent.icon;
              const isSuspended = st === 'suspended';
              const isActive = st === 'active' || isSuspended;
              const isDone = st === 'done';
              const isError = st === 'error';
              
              const currentBorderColor = isDone ? agent.color + '55' : isSuspended ? '#FFB020' : isActive ? agent.color + '88' : isError ? '#FF4D4D44' : 'rgba(255,255,255,0.06)';
              const currentBgColor = isDone ? `${agent.color}0F` : isSuspended ? 'rgba(255,176,32,0.1)' : isActive ? `${agent.color}1A` : isError ? 'rgba(255,77,77,0.07)' : 'rgba(255,255,255,0.02)';
              
              return (
                <div key={agent.id} style={{
                  background: currentBgColor,
                  border: `1px solid ${currentBorderColor}`,
                  borderRadius: 10, padding: '0.85rem',
                  boxShadow: isSuspended ? `0 0 20px rgba(255,176,32,0.3), inset 0 0 10px rgba(255,176,32,0.1)` : isActive ? `0 0 20px ${agent.color}33, inset 0 0 10px ${agent.color}11` : 'none',
                  transform: isActive ? 'scale(1.02)' : 'scale(1)',
                  transition: 'all 0.35s cubic-bezier(0.4,0,0.2,1)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
                    {isDone ? <CheckCircle size={15} color={agent.color} />
                     : isSuspended ? <AlertTriangle size={15} color="#FFB020" style={{ animation: 'pulse 1.5s infinite' }} />
                     : isActive ? <Loader size={15} color={agent.color} style={{ animation: 'spin 1s linear infinite' }} />
                     : isError ? <AlertTriangle size={15} color="#FF4D4D" />
                     : <Icon size={15} color="#374151" />}
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: isDone || isActive ? (isSuspended ? '#FFB020' : agent.color) : '#4B5563' }}>
                      {agent.name} {isSuspended ? '(WAITING IN ORCHESTRATOR JOBS)' : ''}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.68rem', color: '#374151', lineHeight: 1.4 }}>{agent.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Row 4: Live Log */}
        {logs.length > 0 && (
          <div style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: '1rem', marginBottom: '1.25rem', fontFamily: 'monospace' }}>
            <div style={{ fontSize: '0.72rem', color: '#4ade80', marginBottom: '0.5rem', fontWeight: 700, letterSpacing: '0.1em' }}>▶ LIVE AGENT LOG</div>
            <div ref={logsRef} style={{ maxHeight: 160, overflowY: 'auto' }}>
              {logs.map((l, i) => (
                <div key={i} style={{
                  fontSize: '0.76rem',
                  color: l.type === 'error' ? '#FF4D4D' : l.type === 'done' ? '#4ade80' : l.type === 'start' ? '#60a5fa' : '#6B7280',
                  marginBottom: '0.12rem',
                }}>
                  <span style={{ color: '#374151', marginRight: 8 }}>[{l.t}]</span>{l.msg}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ background: 'rgba(255,77,77,0.08)', border: '1px solid #FF4D4D44', borderRadius: 10, padding: '1rem', marginBottom: '1.25rem', color: '#FF4D4D' }}>
            <AlertTriangle size={15} style={{ display: 'inline', marginRight: 6 }} />
            <strong>Backend Error:</strong> {error}
            <div style={{ marginTop: 6, fontSize: '0.8rem', opacity: 0.7 }}>
              Run: <code>cd /Users/anilchowdary/Documents/ui_path_agent_hackathon && source venv/bin/activate && export $(cat .env | xargs) && uvicorn main:app --port 8000</code>
            </div>
          </div>
        )}

        {/* ── RESULTS ── */}
        {result && (
          <div style={{ animation: 'fadeIn 0.5s ease' }}>
            {/* Summary Banner */}
            <div style={{
              display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '1.5rem', alignItems: 'center',
              padding: '1.5rem', marginBottom: '1.25rem',
              background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(0,114,255,0.05))',
              border: '1px solid rgba(16,185,129,0.2)', borderRadius: 14,
            }}>
              <RiskGauge score={result.final_risk_score} color={riskColor} />
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem', flexWrap: 'wrap' }}>
                  <CheckCircle color="#10B981" size={20} />
                  <span style={{ fontWeight: 800, color: '#10B981', fontSize: '1.05rem' }}>All 8 Agents Completed</span>
                  <Badge color={riskColor}>{result.final_risk_score >= 85 ? '🚨 CRITICAL' : result.final_risk_score >= 60 ? '⚠️ HIGH' : '✅ LOW'} RISK</Badge>
                  {result.sanctions_hits && <Badge color="#FF4D4D">🔴 OFAC SDN HIT</Badge>}
                  <Badge color="#FFB020">SLA: {result.sla_status} ({result.days_remaining}d)</Badge>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem', fontSize: '0.8rem' }}>
                  {[
                    { l: 'Pattern Detected', v: result.pattern_name, c: '#A78BFA' },
                    { l: 'FinCEN Tracking ID', v: result.fincen_tracking_id, c: '#10B981' },
                    { l: 'Action Center Job', v: result.action_center_item_id?.slice(0, 18) + '…', c: '#FFB020' },
                    { l: 'Network Depth', v: `${result.network_depth} jurisdictions`, c: '#4facfe' },
                  ].map((r, i) => (
                    <div key={i}>
                      <div style={{ color: '#4B5563', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{r.l}</div>
                      <div style={{ color: r.c, fontWeight: 700 }}>{r.v}</div>
                    </div>
                  ))}
                </div>

                <OrchestratorPanel jobKey={result.action_center_item_id} running={running} />
              </div>
            </div>

            <Collapse title="📝 Agent 6 — Llama 3.1 FinCEN SAR Narrative" accent="#60a5fa">
              <pre style={{
                whiteSpace: 'pre-wrap', fontFamily: "'Georgia', serif",
                color: '#C9D5E8', fontSize: '0.88rem', lineHeight: 1.85,
                margin: 0, background: 'rgba(0,0,0,0.3)', padding: '1.2rem',
                borderRadius: 8, borderLeft: '3px solid #60a5fa',
              }}>{result.sar_narrative}</pre>
            </Collapse>

            <Collapse title="📄 Agent 7 — FinCEN Form 111 JSON Payload" accent="#4ade80" defaultOpen={false}>
              <pre style={{
                background: '#090D12', color: '#4ade80', fontFamily: "'Fira Code', monospace",
                fontSize: '0.76rem', padding: '1.2rem', borderRadius: 8, overflow: 'auto', maxHeight: 300, margin: 0,
              }}>{JSON.stringify(result.fincen_form_111, null, 2)}</pre>
            </Collapse>

            <Collapse title="🛡️ Agent 8 — Audit Trail & UiPath Integration Evidence" accent="#f472b6" defaultOpen={false}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px,1fr))', gap: '0.7rem', fontSize: '0.82rem' }}>
                {[
                  { l: 'FinCEN Tracking ID', v: result.fincen_tracking_id, c: '#10B981' },
                  { l: 'Action Center Task', v: `Job Suspended: ${result.action_center_item_id?.slice(0,12)}…`, c: '#FFB020' },
                  { l: 'UiPath Process', v: 'agent_6_sar_signature_hitl', c: '#fa709a' },
                  { l: 'HITL Pattern', v: 'LangGraph interrupt() → Orchestrator suspend', c: '#f59e0b' },
                  { l: 'OFAC Source', v: result.sanctions_hits ? 'Real OFAC SDN API hit' : 'Clean — No OFAC match', c: result.sanctions_hits ? '#FF4D4D' : '#10B981' },
                  { l: 'Statute', v: 'BSA 31 U.S.C. § 5318(g)', c: '#a78bfa' },
                ].map((r, i) => (
                  <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 8, padding: '0.75rem' }}>
                    <div style={{ fontSize: '0.68rem', color: '#4B5563', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{r.l}</div>
                    <div style={{ fontWeight: 700, color: r.c, marginTop: 3, fontSize: '0.83rem' }}>{r.v}</div>
                  </div>
                ))}
              </div>
            </Collapse>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin    { from{transform:rotate(0deg)}   to{transform:rotate(360deg)} }
        @keyframes fadeIn  { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
        @keyframes flowDash{ from{stroke-dashoffset:24}     to{stroke-dashoffset:0} }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        button { font-family: inherit; }
      `}</style>
    </div>
  );
}
