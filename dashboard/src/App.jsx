import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  ShieldAlert, UserCheck, Activity, Share2, BookOpen, Edit3,
  FileText, UploadCloud, CheckCircle, Loader, AlertTriangle,
  Play, Zap, ChevronDown, ChevronUp, Globe, Database, Eye,
  RefreshCw, Clock, TrendingUp, Lock, ArrowRight, Search,
  Upload, X, FilePlus, FileCode, FileSpreadsheet, AlertCircle, Sun, Moon, Mail, Copy, PieChart, BarChart2
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

  const processFiles = async (files) => {
    setUploading(true); setError(null); setUploadResult(null);
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

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
    const files = Array.from(e.dataTransfer?.files || []);
    if (files.length) processFiles(files);
  }, []);

  const loadSample = async (type) => {
    setLoadingSample(type); setError(null);
    try {
      const r = await fetch(`http://localhost:8000/api/sample-document/${type}`);
      const data = await r.json();
      // Convert sample text to a Blob and upload
      const blob = new Blob([data.content], { type: 'text/plain' });
      const file = new File([blob], data.filename);
      await processFiles([file]);
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
          <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Document Intelligence — Step 1: Upload Evidence
          </h3>
          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
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
              <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: 2 }}>{f.desc}</div>
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
        <input ref={inputRef} type="file" multiple
          accept=".pdf,.csv,.txt,.json,.swift,.mt103"
          style={{ display: 'none' }}
          onChange={(e) => { const files = Array.from(e.target.files || []); if (files.length) processFiles(files); }} />

        {uploading ? (
          <div style={{ color: '#00C6FF' }}>
            <Loader size={28} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
            <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>Parsing document...</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>Extracting transaction data with AI</div>
          </div>
        ) : (
          <>
            <UploadCloud size={28} color={dragging ? '#00C6FF' : 'var(--text-secondary)'} style={{ marginBottom: 8 }} />
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: dragging ? '#00C6FF' : 'var(--text-secondary)' }}>
              {dragging ? 'Drop to parse document' : 'Drop file here or click to browse'}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              PDF, CSV, SWIFT MT103, JSON — max 10MB
            </div>
          </>
        )}
      </div>

      {/* Sample Documents */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Try a sample:</span>
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
                  background: 'var(--panel-bg)', borderRadius: 6,
                  fontSize: '0.75rem',
                }}>
                  <div>
                    <span style={{ color: 'var(--text-secondary)', marginRight: 8 }}>{t.txn_id}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
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
    color: '#3B82F6',
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
  { id:'maestro',    name:'UiPath Maestro',          icon:Zap,         desc:'Orchestrator Case Plan + HITL Gate', color:'#0EA5E9' },
  { id:'triage',     name:'1. Triage Analyst',        icon:ShieldAlert,  desc:'Entity extraction & case context',   color:'#3B82F6' },
  { id:'sanctions',  name:'2. Sanctions Screener',    icon:Search,       desc:'REAL OFAC SDN API — exponential backoff', color:'#F59E0B' },
  { id:'pattern',    name:'3. Pattern Detection',     icon:Activity,     desc:'Llama 3.1 writes live detection code', color:'#06B6D4' },
  { id:'network',    name:'4. Network Investigator',  icon:Share2,       desc:'BFS graph traversal across jurisdictions', color:'#10B981' },
  { id:'regulatory', name:'5. Regulatory Intel',      icon:BookOpen,     desc:'FinCEN 30-day SLA + BSA statute',    color:'#F97316' },
  { id:'writer',     name:'6. SAR Writer',             icon:Edit3,        desc:'Llama 3.1 → FinCEN 6-question SAR', color:'#60A5FA' },
  { id:'populator',  name:'7. Form 111 Populator',    icon:FileText,     desc:'FinCEN Form 111 JSON schema mapping', color:'#34D399' },
  { id:'submission', name:'8. Audit & Action Center', icon:UploadCloud,  desc:'Tracking ID + Action Center HITL task', color:'#059669' },
  { id:'dataservice',name:'9. Data Service Sync',     icon:Database,     desc:'Push entities & risk profiles to Data Service', color:'#8B5CF6' },
  { id:'integrations',name:'10. Integration Service', icon:Share2,       desc:'Dispatch Jira Ticket & Slack Alert', color:'#EC4899' },
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
        border: 'none', color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.9rem',
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

// ── Asset Tracking Ledger ───────────────────────────────────────────────────
function AssetTrackingLedger({ transactions, running, done }) {
  if (!transactions || transactions.length === 0) return null;
  const flag = (c) => JURISDICTION_FLAGS[c] || '🏳️';
  return (
    <div style={{ 
      display: 'flex', flexDirection: 'column', gap: '0.5rem',
      maxHeight: '300px', overflowY: 'auto', paddingRight: '0.5rem'
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1.5fr', gap: '1rem', 
                    padding: '0.5rem 1rem', background: 'var(--panel-bg)', borderRadius: 8,
                    fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '0.05em' }}>
        <div>ORIGINATOR</div>
        <div style={{ textAlign: 'center' }}>TRANSFER</div>
        <div>BENEFICIARY</div>
      </div>
      
      {transactions.map((t, i) => {
        const animated = running || done;
        return (
          <div key={i} style={{ 
            display: 'grid', gridTemplateColumns: '1.5fr 1fr 1.5fr', gap: '1rem', 
            padding: '1rem', background: 'var(--bg-gradient)', borderRadius: 8,
            border: '1px solid var(--panel-border)', alignItems: 'center',
            opacity: animated ? 1 : 0.4, transition: 'opacity 0.5s',
          }}>
            {/* Originator */}
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-color)' }}>
                {t.originator?.name || t.originator?.account || '?'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {flag(t.originator?.country)} {t.originator?.country || 'Unknown'}
              </div>
            </div>

            {/* Transfer Amount & Arrow */}
            <div style={{ textAlign: 'center', position: 'relative' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFB020' }}>
                ${(t.amount || 0).toLocaleString()}
              </div>
              <div style={{ 
                height: 2, background: 'linear-gradient(90deg, #FF4D4D, #FFB020)',
                margin: '8px auto', position: 'relative', width: '80%',
                borderRadius: 2, overflow: 'hidden'
              }}>
                {animated && (
                  <div style={{
                    position: 'absolute', top: 0, left: '-100%', width: '100%', height: '100%',
                    background: 'rgba(255,255,255,0.4)',
                    animation: 'flowDash 1.5s infinite linear'
                  }} />
                )}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>{t.type}</div>
            </div>

            {/* Beneficiary */}
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-color)' }}>
                {t.beneficiary?.name || t.beneficiary?.account || '?'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {flag(t.beneficiary?.country)} {t.beneficiary?.country || 'Unknown'}
              </div>
            </div>
          </div>
        );
      })}
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
  const sc = stateColor[status?.state] || 'var(--text-secondary)';

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
          borderRadius: 6, padding: '4px 10px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.78rem',
        }}>
          {loading ? '...' : '↻ Refresh'}
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.6rem', fontSize: '0.8rem' }}>
        {[
          { l: 'Process', v: 'agent_6_sar_signature_hitl', c: '#60a5fa' },
          { l: 'Job Key', v: jobKey.slice(0, 8) + '...', c: 'var(--text-secondary)' },
          { l: 'State', v: status?.state || 'Checking...', c: sc },
        ].map((r, i) => (
          <div key={i} style={{ background: 'var(--panel-bg)', borderRadius: 8, padding: '0.6rem' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{r.l}</div>
            <div style={{ fontWeight: 700, color: r.c, marginTop: 2 }}>{r.v}</div>
          </div>
        ))}
      </div>
      {status?.state === 'Suspended' && (
        <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(255,176,32,0.1)',
          border: '1px solid rgba(255,176,32,0.3)', borderRadius: 8, fontSize: '0.82rem', color: '#FFB020' }}>
          🔔 <strong>Waiting in Action Center</strong> — BSA Officer must review and approve the SAR before filing proceeds.
          <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>
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
    { x: 10,  y: 20,  w: 120, h: 38, label: 'React Dashboard',    sub: 'Doc Upload + Analyst', color: '#3B82F6' },
    { x: 180, y: 20,  w: 130, h: 38, label: 'FastAPI + LangGraph', sub: '8-Agent Pipeline',     color: '#0EA5E9' },
    { x: 360, y: 20,  w: 130, h: 38, label: 'AWS Bedrock',         sub: 'Llama 3.1 70B',        color: '#F59E0B' },
    { x: 10,  y: 98,  w: 120, h: 38, label: 'Doc Intelligence',    sub: 'PDF·CSV·SWIFT·JSON',   color: '#00C6FF' },
    { x: 180, y: 98,  w: 130, h: 38, label: 'UiPath Maestro',      sub: 'Case Orchestrator',    color: '#10B981' },
    { x: 360, y: 98,  w: 130, h: 38, label: 'Action Center',       sub: 'BSA Officer HITL',     color: '#059669' },
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

// ── Autopilot Widget ──────────────────────────────────────────────────────────
function AutopilotWidget({ caseData }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState([{ role: 'assistant', content: 'Hi! I am UiPath Autopilot. How can I help you analyze this case?' }]);
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => { if (endRef.current) endRef.current.scrollIntoView({ behavior: 'smooth' }); }, [chat]);

  const sendQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    const userQ = query;
    setQuery('');
    setChat(prev => [...prev, { role: 'user', content: userQ }]);
    setLoading(true);

    try {
      const resp = await fetch('http://localhost:8000/api/autopilot-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQ, case_id: caseData?.case_id || 'UNKNOWN', context: caseData }),
      });
      const data = await resp.json();
      setChat(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      setChat(prev => [...prev, { role: 'assistant', content: 'Error connecting to Autopilot.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button onClick={() => setOpen(!open)} style={{
        position: 'fixed', bottom: 30, right: 30, background: 'linear-gradient(135deg, #00C6FF, #0072FF)',
        border: 'none', borderRadius: '50%', width: 60, height: 60, color: '#fff',
        boxShadow: '0 8px 30px rgba(0, 198, 255, 0.4)', cursor: 'pointer', zIndex: 1000,
        display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'transform 0.2s'
      }} onMouseOver={e => e.currentTarget.style.transform = 'scale(1.1)'} onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}>
        {open ? <X size={28} /> : <Zap size={28} fill="#fff" />}
      </button>

      {/* Chat Panel */}
      {open && (
        <div style={{
          position: 'fixed', bottom: 100, right: 30, width: 380, height: 500,
          background: 'var(--panel-bg)', border: '1px solid var(--panel-border)', borderRadius: 16,
          boxShadow: '0 10px 40px rgba(0,0,0,0.5)', zIndex: 999, display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
        }}>
          <div style={{ padding: '1rem', background: 'linear-gradient(135deg, #00C6FF22, #0072FF22)', borderBottom: '1px solid var(--panel-border)', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Zap size={20} color="#00C6FF" fill="#00C6FF" />
            <div>
              <div style={{ fontWeight: 800, color: '#00C6FF', fontSize: '1rem' }}>UiPath Autopilot</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>GenAI Assistant for Analysts</div>
            </div>
          </div>

          <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {chat.map((msg, i) => (
              <div key={i} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                <div style={{
                  background: msg.role === 'user' ? '#0072FF' : 'var(--bg-gradient)',
                  color: '#fff', padding: '0.8rem 1rem', borderRadius: 12,
                  borderBottomRightRadius: msg.role === 'user' ? 2 : 12,
                  borderBottomLeftRadius: msg.role === 'assistant' ? 2 : 12,
                  fontSize: '0.85rem', lineHeight: 1.5, border: msg.role === 'assistant' ? '1px solid var(--panel-border)' : 'none'
                }}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', background: 'var(--bg-gradient)', padding: '0.8rem', borderRadius: 12, border: '1px solid var(--panel-border)' }}>
                <Loader size={16} color="#00C6FF" style={{ animation: 'spin 1s linear infinite' }} />
              </div>
            )}
            <div ref={endRef} />
          </div>

          <form onSubmit={sendQuery} style={{ padding: '1rem', borderTop: '1px solid var(--panel-border)', display: 'flex', gap: 10, background: 'var(--bg-color)' }}>
            <input type="text" value={query} onChange={e => setQuery(e.target.value)} placeholder="Ask Autopilot about this case..."
              style={{ flex: 1, background: 'var(--bg-gradient)', border: '1px solid var(--panel-border)', borderRadius: 20, padding: '0.6rem 1rem', color: 'var(--text-color)', outline: 'none' }} />
            <button type="submit" disabled={loading || !query.trim()} style={{ background: '#0072FF', border: 'none', borderRadius: '50%', width: 40, height: 40, color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowRight size={18} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// Main App
// ══════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [isLightMode,  setIsLightMode]  = useState(false);
  const [scenario,     setScenario]     = useState('layering');
  const [agentStates,  setAgentStates]  = useState(AGENTS.map(() => 'idle'));
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState(null);
  const [running,      setRunning]      = useState(false);
  const [resilience,   setResilience]   = useState(false);
  const [logs,         setLogs]         = useState([]);
  const [uploadedCase, setUploadedCase] = useState(null); // From document upload
  const [uploadedDocs, setUploadedDocs] = useState([]);   // Evidence locker
  
  // New UI Flow States
  const [caseLoaded,   setCaseLoaded]   = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const logsRef = useRef(null);

  // The active case: uploaded doc takes priority over preset scenario
  const CASE = uploadedCase || SCENARIOS[scenario];
  const totalAmount = CASE.transactions.reduce((s, t) => s + t.amount, 0);

  const handleDocumentExtracted = (uploadResult) => {
    setIsExtracting(true);
    setTimeout(() => {
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
      
      setIsExtracting(false);
      setCaseLoaded(true);
    }, 1500); // Simulate extraction animation delay
  };

  const handleClipboardAI = () => {
    if (!result || !result.fincen_form_111) return;
    const form = result.fincen_form_111;
    const text = `
========================================
[UiPath Clipboard AI] Legacy Mainframe Mapping
========================================
TRACKING_ID:    ${result.fincen_tracking_id}
RISK_SCORE:     ${result.final_risk_score}/100
PATTERN:        ${result.pattern_name}
SAR_SUBJECT:    ${form.part_1_subject_information?.primary_subject || 'UNKNOWN'}
SAR_AMOUNT:     $${form.part_2_suspicious_activity_information?.amount_involved || 0}
SAR_NARRATIVE:  ${result.sar_narrative.split('\n')[0]}...
========================================
READY FOR LEGACY TERMINAL PASTE
========================================`;
    navigator.clipboard.writeText(text.trim());
    addLog(`📋 Copied formatted data to clipboard via Clipboard AI`, 'done');
    // Briefly change button text or show toast if needed
  };

  const clearUpload = () => { setUploadedCase(null); setCaseLoaded(false); };

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

  const handleDownloadReport = () => {
    if (!result) return;
    const content = `FINCEN SAR REPORT\n====================\n\n${result.sar_narrative}\n\nFORM 111 JSON DATA\n====================\n${JSON.stringify(result.fincen_form_111, null, 2)}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SAR_Report_${result.fincen_tracking_id || 'export'}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const riskColor = result ? getRiskColor(result.final_risk_score) : '#4facfe';
  const uniqueJurisdictions = [...new Set(
    CASE.transactions.flatMap(t => [t.originator?.country, t.beneficiary?.country].filter(Boolean))
  )];

  return (
    <div className={isLightMode ? 'light-mode' : ''} style={{
      display: 'flex', height: '100vh', overflow: 'hidden',
      background: 'var(--bg-gradient)', fontFamily: "'Inter', system-ui, sans-serif",
      color: 'var(--text-primary)', transition: 'all 0.5s ease',
    }}>
      {/* ── LEFT SIDEBAR ── */}
      <div style={{
        width: 300, background: 'var(--header-bg)', borderRight: '1px solid var(--border-color)',
        display: 'flex', flexDirection: 'column', padding: '1.5rem', zIndex: 10,
        boxShadow: '4px 0 20px var(--shadow-color)', flexShrink: 0,
      }}>
        {/* Brand */}
        <div style={{ marginBottom: '2.5rem' }}>
          <h1 style={{
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            margin: 0, fontSize: '2.2rem', fontWeight: 900, letterSpacing: '-1px',
          }}>🛡️ SentinelFin</h1>
          <p style={{ margin: '0.3rem 0 0', color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Autonomous AML Compliance
          </p>
        </div>

        {/* Controls */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
          <h3 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1rem' }}>Investigation Scenarios</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginBottom: '2rem' }}>
            {Object.entries(SCENARIOS).map(([key, sc]) => (
              <button key={key} onClick={() => { 
                  setScenario(key); setResult(null); setLogs([]); setAgentStates(AGENTS.map(() => 'idle')); clearUpload(); 
                  setCaseLoaded(false); setIsExtracting(true);
                  setTimeout(() => { setIsExtracting(false); setCaseLoaded(true); }, 1200);
                }}
                style={{
                  textAlign: 'left', background: scenario === key && !uploadedCase ? sc.color + '22' : 'var(--btn-bg)',
                  border: `1px solid ${scenario === key && !uploadedCase ? sc.color + '77' : 'var(--border-color)'}`,
                  borderRadius: 10, padding: '12px 14px', color: scenario === key && !uploadedCase ? sc.color : 'var(--text-secondary)',
                  fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s',
                  display: 'flex', alignItems: 'center', gap: '0.6rem'
                }}>
                <span style={{ fontSize: '1.2rem' }}>{sc.label.split(' ')[0]}</span>
                <span>{sc.label.split(' ').slice(1).join(' ')}</span>
              </button>
            ))}
          </div>

          <h3 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1rem' }}>System Settings</h3>

          <button onClick={() => setIsLightMode(!isLightMode)}
            style={{
              width: '100%', background: 'var(--btn-bg)', border: '1px solid var(--border-color)',
              borderRadius: 10, padding: '12px 14px', color: 'var(--text-secondary)',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.6rem', transition: 'all 0.2s',
              fontSize: '0.85rem', fontWeight: 600
            }}>
            {isLightMode ? <Moon size={16} /> : <Sun size={16} />}
            {isLightMode ? 'Dark Mode' : 'Light Mode'}
          </button>
        </div>

        {/* Start Button at bottom of sidebar */}
        <div style={{ marginTop: '1.5rem' }}>
          <button id="start-investigation-btn" onClick={startInvestigation} disabled={running || !caseLoaded}
            style={{
              width: '100%', background: running ? 'var(--btn-bg)' : 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%)',
              border: running ? '1px solid var(--border-color)' : 'none', borderRadius: 12, padding: '14px',
              color: running ? 'var(--text-secondary)' : '#fff', fontWeight: 800, fontSize: '0.95rem',
              cursor: running ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              boxShadow: running ? 'none' : '0 8px 25px rgba(14,165,233,0.4)', transition: 'all 0.2s', textTransform: 'uppercase', letterSpacing: '0.05em',
            }}>
            {running ? <><Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />Running...</> : <><Play size={16} />Start AI Engine</>}
          </button>
        </div>
      </div>

      {/* ── MAIN CANVAS ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '2rem 3rem', display: 'flex', flexDirection: 'column' }}>
        
        {!caseLoaded ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', animation: 'fadeIn 0.5s ease' }}>
            {isExtracting ? (
              <div style={{ textAlign: 'center' }}>
                 <Loader size={60} color="var(--accent-blue)" style={{ animation: 'spin 1.5s linear infinite', marginBottom: '1.5rem', display: 'inline-block' }} />
                 <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '0.5rem', fontWeight: 800 }}>Extracting Intelligence...</h2>
                 <p style={{ color: 'var(--text-secondary)' }}>Parsing structured entities, transactions, and risk scores using OCR & LLMs.</p>
              </div>
            ) : (
              <div style={{ width: '100%', maxWidth: 800, textAlign: 'center' }}>
                 <div style={{ fontSize: '3.5rem', marginBottom: '1rem', animation: 'fadeIn 1s ease' }}>📥</div>
                 <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '1rem', color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>Upload Evidence to Begin</h1>
                 <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '3rem', lineHeight: 1.6 }}>
                   Upload bank statements, SWIFT MT103 logs, or TM alerts. <br/> SentinelFin will instantly structure the data and prepare the Agentic Pipeline.
                 </p>
                 <div className="glass-card" style={{ padding: '2.5rem', textAlign: 'left', background: 'var(--panel-bg)' }}>
                   <DocumentUploadPanel onTransactionsExtracted={handleDocumentExtracted} />
                 </div>
                 <p style={{ marginTop: '2rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                   Or select a pre-configured <strong style={{ color: 'var(--accent-cyan)' }}>Investigation Scenario</strong> from the sidebar.
                 </p>
              </div>
            )}
          </div>
        ) : (
          <div style={{ animation: 'fadeIn 0.5s ease' }}>
            {/* Top Stats Bar */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
              {[
                { icon: '📊', label: 'False Positive Rate', val: '95%', sub: 'Traditional Rules', color: 'var(--accent-red)' },
                { icon: '⏱️', label: 'Manual Investigation', val: '4+ hrs', sub: 'Per Case', color: 'var(--accent-orange)' },
                { icon: '⚡', label: 'SentinelFin Agentic', val: '<60 sec', sub: '8-Agent Pipeline', color: 'var(--accent-green)' },
                { icon: '🏛️', label: 'Compliance Risk', val: '$10M+', sub: 'Per FinCEN Failure', color: 'var(--accent-blue)' },
              ].map((s, i) => (
                <div key={i} className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.2rem' }}>
                  <span style={{ fontSize: '2.2rem' }}>{s.icon}</span>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{s.label}</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 900, color: s.color, lineHeight: 1.1, marginTop: 4 }}>{s.val}</div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: 4 }}>{s.sub}</div>
                  </div>
                </div>
              ))}
            </div>

        {/* BENTO GRID */}
        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '2rem', alignItems: 'start' }}>
          
          {/* Left Column: Vertical Agent Pipeline */}
          <div className="glass-card" style={{ padding: '1.8rem', position: 'sticky', top: '2.5rem' }}>
            <h3 style={{ margin: '0 0 1.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Activity size={16} /> Agentic Pipeline
            </h3>
            <div style={{ position: 'relative' }}>
              {/* Vertical line connecting nodes */}
              <div style={{ position: 'absolute', left: '21px', top: '20px', bottom: '30px', width: '2px', background: 'var(--border-color)', zIndex: 0 }} />
              
              {AGENTS.map((agent, idx) => {
                const st = agentStates[idx];
                const Icon = agent.icon;
                const isSuspended = st === 'suspended';
                const isActive = st === 'active' || isSuspended;
                const isDone = st === 'done';
                const isError = st === 'error';
                const cColor = isDone || isActive ? (isSuspended ? 'var(--accent-orange)' : agent.color) : 'var(--text-secondary)';
                
                return (
                  <div key={agent.id} style={{ display: 'flex', gap: '1.2rem', marginBottom: '1.8rem', position: 'relative', zIndex: 1, opacity: isDone || isActive ? 1 : 0.4 }}>
                    {/* Node Icon */}
                    <div style={{
                      width: '44px', height: '44px', borderRadius: '50%', background: isDone ? `${agent.color}22` : isActive ? `${agent.color}33` : 'var(--card-bg)',
                      border: `2px solid ${cColor}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                      boxShadow: isActive ? `0 0 15px ${agent.color}66` : 'none', transition: 'all 0.3s ease'
                    }}>
                      {isDone ? <CheckCircle size={20} color={agent.color} /> : isSuspended ? <AlertTriangle size={20} color="var(--accent-orange)" /> : isActive ? <Loader size={20} color={agent.color} style={{ animation: 'spin 1s linear infinite' }} /> : <Icon size={20} color="var(--text-secondary)" />}
                    </div>
                    {/* Details */}
                    <div style={{ paddingTop: '0.4rem' }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: cColor }}>{agent.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.3rem', lineHeight: 1.4 }}>{agent.desc}</div>
                      {isSuspended && <div style={{ fontSize: '0.65rem', color: 'var(--accent-orange)', fontWeight: 800, marginTop: '0.4rem', background: 'rgba(245,158,11,0.1)', padding: '4px 8px', borderRadius: '4px', display: 'inline-block', letterSpacing: '0.05em' }}>WAITING IN ORCHESTRATOR</div>}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Live Log */}
            {logs.length > 0 && (
              <div style={{ marginTop: '2rem', background: 'var(--panel-bg)', borderRadius: 10, padding: '1.2rem', border: '1px solid var(--border-color)', boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.1)' }}>
                <div style={{ fontSize: '0.65rem', color: 'var(--accent-green)', marginBottom: '0.8rem', fontWeight: 800, letterSpacing: '0.1em' }}>▶ EXECUTION LOG</div>
                <div ref={logsRef} style={{ maxHeight: 250, overflowY: 'auto', fontFamily: "'Fira Code', monospace" }}>
                  {logs.map((l, i) => (
                    <div key={i} style={{ fontSize: '0.7rem', color: l.type === 'error' ? 'var(--accent-red)' : l.type === 'done' ? 'var(--accent-green)' : l.type === 'start' ? 'var(--accent-blue)' : 'var(--text-secondary)', marginBottom: '0.3rem', lineHeight: 1.5 }}>
                      <span style={{ opacity: 0.5, marginRight: 8 }}>[{l.t}]</span>{l.msg}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Evidence & Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            
            {/* Evidence & Case Overview */}
            <div className="glass-card" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Active Investigation Context</h3>
                <Badge color={CASE.color}>{CASE.badge.replace(/_/g, ' ')}</Badge>
              </div>
              <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>{CASE.case_id}</div>
                  <div style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{CASE.description}</div>
                </div>
                <div style={{ textAlign: 'right', borderLeft: '1px solid var(--border-color)', paddingLeft: '2rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Exposure</div>
                  <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-red)', marginTop: '0.4rem' }}>${totalAmount.toLocaleString()}</div>
                </div>
              </div>
              
              {uploadedCase && (
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
                  <button onClick={clearUpload} style={{ background: 'var(--panel-bg)', border: '1px solid var(--border-color)', borderRadius: 6, padding: '6px 12px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>✕ Clear Document Data</button>
                </div>
              )}
            </div>

            {/* Money Flow Graph */}
            <div className="glass-card" style={{ padding: '2rem' }}>
               <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-secondary)', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
              GLOBAL ASSET TRACING
            </h3>
            <AssetTrackingLedger transactions={CASE.transactions} running={running} done={result !== null} />
          </div>

            {/* Architecture SVG Panel */}
            <div className="glass-card" style={{ padding: '2rem' }}>
               <h3 style={{ margin: '0 0 1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                Enterprise Architecture Routing
              </h3>
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <ArchDiagram />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid var(--accent-red)', borderRadius: 12, padding: '1.5rem', color: 'var(--accent-red)' }}>
                <AlertTriangle size={18} style={{ display: 'inline', marginRight: 8 }} />
                <strong>Backend Error:</strong> {error}
              </div>
            )}

            {/* Results Bento Box */}
            {result && (
              <div style={{ animation: 'fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1)' }}>
                <div className="glass-card" style={{ padding: '2rem', background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(14,165,233,0.03))', border: '1px solid var(--accent-green)' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '2.5rem', alignItems: 'center' }}>
                    <RiskGauge score={result.final_risk_score} color={riskColor} />
                    
                    <div>
                      <h2 style={{ margin: '0 0 1.5rem', display: 'flex', alignItems: 'center', gap: '0.8rem', color: 'var(--accent-green)', fontSize: '1.6rem' }}>
                        <CheckCircle size={28} /> Investigation Complete
                      </h2>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.2rem', marginBottom: '1.5rem' }}>
                        <div style={{ background: 'var(--panel-bg)', borderRadius: 10, padding: '1rem', border: '1px solid var(--border-color)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>FinCEN Tracking ID</div>
                          <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '0.4rem' }}>{result.fincen_tracking_id}</div>
                        </div>
                        <div style={{ background: 'var(--panel-bg)', borderRadius: 10, padding: '1rem', border: '1px solid var(--border-color)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Detection Pattern</div>
                          <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-blue)', marginTop: '0.4rem' }}>{result.pattern_name}</div>
                        </div>
                        <div style={{ background: 'var(--panel-bg)', borderRadius: 10, padding: '1rem', border: '1px solid var(--border-color)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>OFAC Screening</div>
                          <div style={{ fontSize: '1rem', fontWeight: 800, color: result.sanctions_hits ? 'var(--accent-red)' : 'var(--accent-green)', marginTop: '0.4rem' }}>
                            {result.sanctions_hits ? '🚨 SANCTIONS HIT' : '✅ Clean Profile'}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.2rem', marginBottom: '1.5rem' }}>
                        <div style={{ background: 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(139,92,246,0.02))', borderRadius: 10, padding: '1rem', border: '1px solid rgba(139,92,246,0.3)' }}>
                          <div style={{ fontSize: '0.7rem', color: '#A78BFA', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 6 }}><Database size={12}/> UiPath Data Service</div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.4rem' }}>
                            ✅ Entity Records Synced<br/>
                            ✅ SAR Payload Persisted
                          </div>
                        </div>
                        <div style={{ background: 'linear-gradient(135deg, rgba(236,72,153,0.1), rgba(236,72,153,0.02))', borderRadius: 10, padding: '1rem', border: '1px solid rgba(236,72,153,0.3)' }}>
                          <div style={{ fontSize: '0.7rem', color: '#F472B6', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 6 }}><Share2 size={12}/> UiPath Integration Service</div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.4rem' }}>
                            🎫 Jira Ticket: AML-{result.fincen_tracking_id?.split('-')[1] || '4921'}<br/>
                            💬 Slack Alert: #aml-escalations
                          </div>
                        </div>
                      </div>

                      <OrchestratorPanel jobKey={result.action_center_item_id} running={running} />
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
                  <Collapse title="📝 View FinCEN SAR Narrative (Agent 6)" accent="var(--accent-blue)">
                    <pre style={{
                      whiteSpace: 'pre-wrap', fontFamily: "'Georgia', serif",
                      color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: 1.8,
                      margin: 0, background: 'var(--panel-bg)', padding: '2rem',
                      borderRadius: 10, borderLeft: '4px solid var(--accent-blue)',
                    }}>{result.sar_narrative}</pre>
                  </Collapse>

                  <Collapse title="📄 View FinCEN Form 111 JSON Data (Agent 7)" accent="var(--accent-green)" defaultOpen={false}>
                    <pre style={{
                      background: 'var(--sar-bg)', color: '#4ade80', fontFamily: "'Fira Code', monospace",
                      fontSize: '0.8rem', padding: '2rem', borderRadius: 10, overflow: 'auto', maxHeight: 400, margin: 0,
                    }}>{JSON.stringify(result.fincen_form_111, null, 2)}</pre>
                  </Collapse>
                </div>
                
                <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                  <button onClick={handleDownloadReport}
                    style={{
                      background: 'linear-gradient(135deg, var(--accent-green) 0%, #059669 100%)',
                      border: 'none', borderRadius: 12, padding: '16px 32px',
                      color: '#fff', fontWeight: 800, fontSize: '1.1rem',
                      cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 10,
                      boxShadow: '0 8px 25px rgba(16,185,129,0.3)', transition: 'all 0.2s', textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>
                    <FileText size={20} /> Download Final SAR Report
                  </button>
                  <button onClick={handleClipboardAI}
                    style={{
                      background: 'linear-gradient(135deg, var(--accent-orange) 0%, #F59E0B 100%)',
                      border: 'none', borderRadius: 12, padding: '16px 32px',
                      color: '#fff', fontWeight: 800, fontSize: '1.1rem',
                      cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 10,
                      boxShadow: '0 8px 25px rgba(245,158,11,0.3)', transition: 'all 0.2s', textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>
                    <Copy size={20} /> Copy to Clipboard AI
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      )}
      </div>

      <style>{`
        @keyframes spin    { from{transform:rotate(0deg)}   to{transform:rotate(360deg)} }
        @keyframes fadeIn  { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
        @keyframes flowDash{ from{stroke-dashoffset:24}     to{stroke-dashoffset:0} }
        * { box-sizing: border-box; }
        button { font-family: inherit; }
      `}</style>

      {/* Render Autopilot Widget when a case is loaded or completed */}
      {result && <AutopilotWidget caseData={result} />}
    </div>
  );
}

