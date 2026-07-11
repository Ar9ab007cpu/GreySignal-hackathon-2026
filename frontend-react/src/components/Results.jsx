import { useState, useRef, useEffect, useCallback } from 'react';
import RiskGauge from './RiskGauge';

/* ================================================================
   COLOUR HELPERS
   ================================================================ */

function riskColor(score) {
  if (score < 35) return '#34D399';
  if (score < 60) return '#F5B942';
  if (score < 78) return '#FB7185';
  return '#F43F5E';
}

function statusClass(status) {
  if (status === 'ok') return 'status-ok';
  if (status === 'cached') return 'status-cached';
  return 'status-unavailable';
}

const NODE_COLORS = {
  country: '#22D3EE',
  decision: '#F5B942',
  risk_factor: '#FB7185',
  evidence: '#34D399',
  agent: '#A78BFA',
  forecast: '#38BDF8',
  model: '#F472B6',
};

function nodeColor(type) {
  return NODE_COLORS[type] || '#67E8F9';
}

/* ================================================================
   REUSABLE SUB-COMPONENTS
   ================================================================ */

function MarkdownText({ text }) {
  if (!text) return null;

  /* Convert markdown to HTML string */
  const toHtml = (md) => {
    let html = md
      /* Escape HTML entities */
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      /* Bold  **text** or __text__ */
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.+?)__/g, '<strong>$1</strong>')
      /* Italic *text* or _text_ (not inside bold) */
      .replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
      /* Numbered list items:  "1. text" at start of line */
      .replace(/^(\d+)\.\s+(.+)$/gm, '<li value="$1">$2</li>')
      /* Bullet list items: "- text" */
      .replace(/^[-]\s+(.+)$/gm, '<li>$1</li>')
      /* Wrap consecutive <li> in <ol> */
      .replace(/((?:<li[^>]*>.*?<\/li>\s*)+)/g, '<ol>$1</ol>')
      /* Paragraphs: double newlines */
      .replace(/\n\n+/g, '</p><p>')
      /* Single newlines inside paragraphs */
      .replace(/\n/g, '<br/>');

    return `<p>${html}</p>`;
  };

  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: toHtml(text) }}
    />
  );
}

function DataTable({ columns, rows }) {
  if (!rows || rows.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No data available.</p>;
  }
  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>{columns.map((col) => <th key={col.key}>{col.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((col) => (
                <td key={col.key}>
                  {col.key === 'status' ? (
                    <span className={`status-badge ${statusClass(row[col.key])}`}>
                      {row[col.key]}
                    </span>
                  ) : col.key === 'score' || col.key === 'weight' || col.key === 'weighted_contribution' || col.key === 'confidence' ? (
                    typeof row[col.key] === 'number' ? row[col.key].toFixed(2) : row[col.key]
                  ) : (
                    String(row[col.key] ?? '')
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RiskBars({ factors }) {
  return (
    <div className="risk-bar-list">
      {factors.map((f) => (
        <div className="risk-bar-item" key={f.name}>
          <div className="risk-bar-header">
            <span className="risk-bar-name">{f.name}</span>
            <span className="risk-bar-score">{f.score}</span>
          </div>
          <div className="risk-bar-track">
            <div
              className="risk-bar-fill"
              style={{
                width: `${f.score}%`,
                background: riskColor(f.score),
                boxShadow: `0 0 8px ${riskColor(f.score)}40`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

/* ================================================================
   SVG BAR CHART  (Model Outputs, SHAP)
   ================================================================ */

function BarChart({ data, title, colorFn, formatValue, height: barH = 32 }) {
  if (!data || Object.keys(data).length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No data available.</p>;
  }

  const entries = Object.entries(data).map(([k, v]) => ({ key: k, value: Number(v) }));
  const maxVal = Math.max(...entries.map((e) => Math.abs(e.value)), 0.01);
  const chartW = 520;
  const labelW = 180;
  const barAreaW = chartW - labelW - 40;
  const totalH = entries.length * (barH + 12) + 10;
  const [hovered, setHovered] = useState(null);

  return (
    <div className="chart-container">
      {title && <div className="chart-title">{title}</div>}
      <svg
        viewBox={`0 0 ${chartW} ${totalH}`}
        className="bar-chart-svg"
        style={{ width: '100%', maxHeight: 400 }}
      >
        {entries.map((entry, i) => {
          const y = i * (barH + 12) + 6;
          const barW = (Math.abs(entry.value) / maxVal) * barAreaW;
          const color = colorFn ? colorFn(entry.key, entry.value) : '#22D3EE';
          const isHover = hovered === i;

          return (
            <g
              key={entry.key}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              style={{ cursor: 'default' }}
            >
              {/* Label */}
              <text
                x={labelW - 8}
                y={y + barH / 2 + 1}
                textAnchor="end"
                fill={isHover ? '#F8FAFC' : '#91A2BA'}
                fontSize="12"
                fontWeight="600"
                fontFamily="Inter, sans-serif"
                dominantBaseline="middle"
              >
                {entry.key}
              </text>

              {/* Bar background */}
              <rect
                x={labelW}
                y={y}
                width={barAreaW}
                height={barH}
                rx={6}
                fill="#0F1825"
              />

              {/* Bar fill */}
              <rect
                x={labelW}
                y={y}
                width={barW}
                height={barH}
                rx={6}
                fill={color}
                opacity={isHover ? 1 : 0.85}
                style={{
                  filter: isHover ? `drop-shadow(0 0 8px ${color}60)` : 'none',
                  transition: 'all 200ms ease',
                }}
              />

              {/* Value */}
              <text
                x={labelW + barW + 8}
                y={y + barH / 2 + 1}
                fill={isHover ? '#F8FAFC' : '#B9C7D9'}
                fontSize="12"
                fontWeight="700"
                fontFamily="Inter, sans-serif"
                dominantBaseline="middle"
              >
                {formatValue ? formatValue(entry.value) : entry.value}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* ================================================================
   CONFIDENCE INTERVAL VISUALISER
   ================================================================ */

function ConfidenceVisual({ data }) {
  if (!data || (!data.lower && data.lower !== 0)) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No confidence data.</p>;
  }

  const lower = data.lower ?? 0;
  const upper = data.upper ?? 100;
  const point = data.point ?? data.predicted ?? ((lower + upper) / 2);
  const min = Math.max(0, Math.floor(lower - 10));
  const max = Math.min(100, Math.ceil(upper + 10));
  const range = max - min || 1;

  const toX = (v) => ((v - min) / range) * 100;

  return (
    <div className="chart-container">
      <div className="chart-title">MAPIE Confidence Interval</div>
      <div className="confidence-track">
        {/* Tick marks */}
        {[min, Math.round(min + range * 0.25), Math.round(min + range * 0.5), Math.round(min + range * 0.75), max].map((tick) => (
          <div key={tick} className="confidence-tick" style={{ left: `${toX(tick)}%` }}>
            <span className="confidence-tick-label">{tick}</span>
          </div>
        ))}

        {/* Interval range */}
        <div
          className="confidence-range"
          style={{
            left: `${toX(lower)}%`,
            width: `${toX(upper) - toX(lower)}%`,
          }}
        />

        {/* Lower bound */}
        <div className="confidence-bound confidence-lower" style={{ left: `${toX(lower)}%` }}>
          <span className="confidence-bound-label">{lower.toFixed(1)}</span>
        </div>

        {/* Point estimate */}
        <div className="confidence-point" style={{ left: `${toX(point)}%` }}>
          <span className="confidence-point-label">{point.toFixed(1)}</span>
        </div>

        {/* Upper bound */}
        <div className="confidence-bound confidence-upper" style={{ left: `${toX(upper)}%` }}>
          <span className="confidence-bound-label">{upper.toFixed(1)}</span>
        </div>
      </div>
      <div className="confidence-legend">
        <span><span className="confidence-legend-dot" style={{ background: '#22D3EE' }} /> Point estimate</span>
        <span><span className="confidence-legend-dot" style={{ background: 'rgba(34,211,238,0.25)' }} /> Prediction interval</span>
      </div>
    </div>
  );
}

/* ================================================================
   FORECAST CHART
   ================================================================ */

function ForecastChart({ forecasts }) {
  if (!forecasts || forecasts.length === 0) return null;
  const [hovered, setHovered] = useState(null);

  const chartW = 600;
  const barH = 38;
  const labelW = 130;
  const totalH = forecasts.length * (barH + 16) + 10;
  const maxVal = Math.max(...forecasts.flatMap((f) => [Math.abs(Number(f.current) || 0), Math.abs(Number(f.forecast) || 0)]), 0.01);
  const barAreaW = chartW - labelW - 80;

  return (
    <div className="chart-container mb-4">
      <div className="chart-title">Current vs Forecast Comparison</div>
      <svg viewBox={`0 0 ${chartW} ${totalH}`} className="bar-chart-svg" style={{ width: '100%' }}>
        {forecasts.map((f, i) => {
          const y = i * (barH + 16) + 6;
          const curVal = Math.abs(Number(f.current) || 0);
          const fcsVal = Math.abs(Number(f.forecast) || 0);
          const curW = (curVal / maxVal) * barAreaW;
          const fcsW = (fcsVal / maxVal) * barAreaW;
          const isHover = hovered === i;
          const dir = f.direction;
          const dirColor = dir === 'improving' ? '#34D399' : dir === 'rising' || dir === 'worsening' ? '#FB7185' : '#F5B942';

          return (
            <g key={i} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)}>
              <text
                x={labelW - 8}
                y={y + barH / 2}
                textAnchor="end"
                fill={isHover ? '#F8FAFC' : '#91A2BA'}
                fontSize="12"
                fontWeight="600"
                fontFamily="Inter, sans-serif"
                dominantBaseline="middle"
              >
                {f.label}
              </text>

              {/* Current bar */}
              <rect x={labelW} y={y} width={barAreaW} height={barH / 2 - 2} rx={4} fill="#0F1825" />
              <rect
                x={labelW} y={y} width={curW} height={barH / 2 - 2} rx={4}
                fill="#344663" opacity={isHover ? 1 : 0.75}
                style={{ transition: 'all 200ms ease' }}
              />
              <text x={labelW + curW + 6} y={y + barH / 4 - 1} fill="#91A2BA" fontSize="10" fontWeight="600" fontFamily="Inter, sans-serif" dominantBaseline="middle">
                {curVal.toFixed(2)}
              </text>

              {/* Forecast bar */}
              <rect x={labelW} y={y + barH / 2 + 2} width={barAreaW} height={barH / 2 - 2} rx={4} fill="#0F1825" />
              <rect
                x={labelW} y={y + barH / 2 + 2} width={fcsW} height={barH / 2 - 2} rx={4}
                fill="#22D3EE" opacity={isHover ? 1 : 0.75}
                style={{ filter: isHover ? 'drop-shadow(0 0 6px rgba(34,211,238,0.4))' : 'none', transition: 'all 200ms ease' }}
              />
              <text x={labelW + fcsW + 6} y={y + barH * 0.75 + 1} fill="#67E8F9" fontSize="10" fontWeight="700" fontFamily="Inter, sans-serif" dominantBaseline="middle">
                {fcsVal.toFixed(2)}
              </text>

              {/* Direction badge */}
              <text x={chartW - 10} y={y + barH / 2} textAnchor="end" fill={dirColor} fontSize="10" fontWeight="700" fontFamily="Inter, sans-serif" dominantBaseline="middle">
                {dir ? dir.toUpperCase() : ''}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="confidence-legend" style={{ marginTop: 8 }}>
        <span><span className="confidence-legend-dot" style={{ background: '#344663' }} /> Current</span>
        <span><span className="confidence-legend-dot" style={{ background: '#22D3EE' }} /> Forecast</span>
      </div>
    </div>
  );
}

/* ================================================================
   INTERACTIVE FORCE-DIRECTED KNOWLEDGE GRAPH
   ================================================================ */

function ForceGraph({ graphData }) {
  const canvasRef = useRef(null);
  const simRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);
  const [dimensions, setDimensions] = useState({ w: 800, h: 500 });

  const nodes = (graphData?.nodes || []).map((n, i) => ({
    id: n.id,
    type: n.type || 'default',
    x: 400 + (Math.random() - 0.5) * 300,
    y: 250 + (Math.random() - 0.5) * 200,
    vx: 0,
    vy: 0,
    r: n.type === 'country' ? 24 : n.type === 'decision' ? 20 : 14,
  }));

  const edges = (graphData?.edges || []).map((e) => ({
    source: e.source,
    target: e.target,
    label: e.relation || e.label || '',
  }));

  const nodeMap = {};
  nodes.forEach((n) => { nodeMap[n.id] = n; });

  const resolvedEdges = edges
    .filter((e) => nodeMap[e.source] && nodeMap[e.target])
    .map((e) => ({ ...e, sourceNode: nodeMap[e.source], targetNode: nodeMap[e.target] }));

  /* Force simulation */
  const simulate = useCallback(() => {
    const ALPHA = 0.3;
    const REPULSION = 2800;
    const SPRING = 0.012;
    const SPRING_LEN = 120;
    const DAMPING = 0.88;
    const CX = dimensions.w / 2;
    const CY = dimensions.h / 2;
    const GRAVITY = 0.008;

    for (let iter = 0; iter < 80; iter++) {
      // Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const force = REPULSION / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          nodes[i].vx -= fx;
          nodes[i].vy -= fy;
          nodes[j].vx += fx;
          nodes[j].vy += fy;
        }
      }

      // Spring attraction
      resolvedEdges.forEach((e) => {
        const dx = e.targetNode.x - e.sourceNode.x;
        const dy = e.targetNode.y - e.sourceNode.y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = (dist - SPRING_LEN) * SPRING;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        e.sourceNode.vx += fx;
        e.sourceNode.vy += fy;
        e.targetNode.vx -= fx;
        e.targetNode.vy -= fy;
      });

      // Gravity to center
      nodes.forEach((n) => {
        n.vx += (CX - n.x) * GRAVITY;
        n.vy += (CY - n.y) * GRAVITY;
      });

      // Update positions
      nodes.forEach((n) => {
        n.vx *= DAMPING;
        n.vy *= DAMPING;
        n.x += n.vx * ALPHA;
        n.y += n.vy * ALPHA;
        n.x = Math.max(n.r + 10, Math.min(dimensions.w - n.r - 10, n.x));
        n.y = Math.max(n.r + 10, Math.min(dimensions.h - n.r - 10, n.y));
      });
    }
  }, [nodes, resolvedEdges, dimensions]);

  useEffect(() => {
    const container = canvasRef.current?.parentElement;
    if (container) {
      const w = container.clientWidth;
      setDimensions({ w, h: Math.max(450, Math.min(600, w * 0.6)) });
    }
  }, []);

  useEffect(() => {
    if (nodes.length === 0) return;
    simulate();
    drawGraph();
  }, [dimensions]);

  const drawGraph = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.w * dpr;
    canvas.height = dimensions.h * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, dimensions.w, dimensions.h);

    // Edges
    resolvedEdges.forEach((e) => {
      ctx.beginPath();
      ctx.moveTo(e.sourceNode.x, e.sourceNode.y);
      ctx.lineTo(e.targetNode.x, e.targetNode.y);
      ctx.strokeStyle = 'rgba(52,70,99,0.5)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Edge label
      if (e.label) {
        const mx = (e.sourceNode.x + e.targetNode.x) / 2;
        const my = (e.sourceNode.y + e.targetNode.y) / 2;
        ctx.font = '9px Inter, sans-serif';
        ctx.fillStyle = '#5F7089';
        ctx.textAlign = 'center';
        ctx.fillText(e.label, mx, my - 4);
      }
    });

    // Nodes
    nodes.forEach((n) => {
      const color = nodeColor(n.type);

      // Glow
      const gradient = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r + 12);
      gradient.addColorStop(0, color + '30');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r + 12, 0, Math.PI * 2);
      ctx.fill();

      // Circle
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = '#0B1120';
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Inner fill
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r - 3, 0, Math.PI * 2);
      ctx.fillStyle = color + '15';
      ctx.fill();

      // Label
      ctx.font = `${n.r > 18 ? '11' : '9'}px Inter, sans-serif`;
      ctx.fillStyle = '#DCE6F2';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      const label = n.id.length > 16 ? n.id.slice(0, 14) + '..' : n.id;
      ctx.fillText(label, n.x, n.y + n.r + 14);
    });
  }, [nodes, resolvedEdges, dimensions]);

  const handleMouseMove = useCallback((e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (dimensions.w / rect.width);
    const my = (e.clientY - rect.top) * (dimensions.h / rect.height);

    const hit = nodes.find((n) => {
      const dx = n.x - mx;
      const dy = n.y - my;
      return Math.sqrt(dx * dx + dy * dy) <= n.r + 4;
    });

    if (hit) {
      setTooltip({ x: e.clientX, y: e.clientY, node: hit });
    } else {
      setTooltip(null);
    }
  }, [nodes, dimensions]);

  if (nodes.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No graph data available.</p>;
  }

  return (
    <div className="graph-canvas-wrapper" style={{ position: 'relative' }}>
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: dimensions.h, borderRadius: 12, background: '#070B14' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip(null)}
      />
      {tooltip && (
        <div
          className="graph-tooltip"
          style={{
            position: 'fixed',
            left: tooltip.x + 12,
            top: tooltip.y - 30,
          }}
        >
          <strong>{tooltip.node.id}</strong>
          <span className="graph-tooltip-type" style={{ color: nodeColor(tooltip.node.type) }}>
            {tooltip.node.type}
          </span>
        </div>
      )}
      {/* Legend */}
      <div className="graph-legend">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <span key={type} className="graph-legend-item">
            <span className="graph-legend-dot" style={{ background: color }} />
            {type.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ================================================================
   MAIN RESULTS COMPONENT
   ================================================================ */

const TAB_LIST = ['AI Brief', 'Agents', 'Retrieval', 'Events', 'Forecasts', 'Models', 'Graph'];

export default function Results({ assessment }) {
  const [activeTab, setActiveTab] = useState(0);
  const [jsonExpanded, setJsonExpanded] = useState(false);

  const { overall_score: score, rating, recommendation, summary, factors, evidence } = assessment;

  const factorsWithContrib = factors.map((f) => ({
    ...f,
    weighted_contribution: +(f.score * f.weight).toFixed(2),
  }));

  return (
    <div>
      {/* Hero: Gauge + Metrics */}
      <div className="results-hero">
        <div>
          <RiskGauge score={score} />
        </div>
        <div>
          <div className="metrics-row mb-4">
            <div className="metric-card">
              <div className="metric-label">Country</div>
              <div className="metric-value">{assessment.country}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Risk Rating</div>
              <div className="metric-value" style={{ color: riskColor(score) }}>{rating}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Score</div>
              <div className="metric-value">{score} / 100</div>
            </div>
          </div>

          <div className="section-label">Recommendation</div>
          <div className="recommendation-box">
            <p style={{ fontWeight: 600, marginBottom: 8, color: 'var(--text-heading)' }}>{recommendation}</p>
            <p>{summary}</p>
          </div>
        </div>
      </div>

      <hr className="divider" />

      {/* Risk Factors */}
      <div className="results-factors">
        <div>
          <div className="section-label">Risk Factors</div>
          <DataTable
            columns={[
              { key: 'name', label: 'Factor' },
              { key: 'score', label: 'Score' },
              { key: 'weight', label: 'Weight' },
              { key: 'weighted_contribution', label: 'Contribution' },
              { key: 'rationale', label: 'Rationale' },
            ]}
            rows={factorsWithContrib}
          />
        </div>
        <div>
          <div className="section-label">Score Distribution</div>
          <div className="card">
            <RiskBars factors={factors} />
          </div>
        </div>
      </div>

      <hr className="divider" />

      {/* Evidence */}
      <div className="section-label">Supporting Evidence</div>
      <DataTable
        columns={[
          { key: 'source', label: 'Source' },
          { key: 'label', label: 'Label' },
          { key: 'value', label: 'Value' },
          { key: 'status', label: 'Status' },
          { key: 'detail', label: 'Detail' },
        ]}
        rows={evidence}
      />

      <hr className="divider" />

      {/* Detail Tabs */}
      <div className="tabs-header mb-4">
        {TAB_LIST.map((tab, i) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === i ? 'active' : ''}`}
            onClick={() => setActiveTab(i)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="tab-panel">
        {/* AI Brief */}
        {activeTab === 0 && (
          <div className="ai-brief">
            <MarkdownText text={assessment.ai_summary || 'AI summary is not available. Check GROQ_API_KEY in .env.'} />
            <div className="section-label mt-6">Workflow</div>
            <div className="workflow-steps">
              {(assessment.workflow_steps || []).map((s, i) => (
                <div className="workflow-step" key={i}>
                  <div className="workflow-step-num">{i + 1}</div>
                  <div className="workflow-step-text">{s}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Agents */}
        {activeTab === 1 && (
          <DataTable
            columns={[
              { key: 'agent', label: 'Agent' },
              { key: 'finding', label: 'Finding' },
              { key: 'confidence', label: 'Confidence' },
            ]}
            rows={assessment.agent_outputs || []}
          />
        )}

        {/* Retrieval */}
        {activeTab === 2 && (
          <DataTable
            columns={[
              { key: 'source', label: 'Source' },
              { key: 'text', label: 'Text' },
              { key: 'score', label: 'Score' },
            ]}
            rows={assessment.retrieval_results || []}
          />
        )}

        {/* Events */}
        {activeTab === 3 && (
          <div>
            {/* Sentiment as visual cards */}
            <div className="section-label">Sentiment Analysis</div>
            {assessment.sentiment && Object.keys(assessment.sentiment).length > 0 ? (
              <div className="metrics-row mb-4">
                {Object.entries(assessment.sentiment).map(([key, val]) => (
                  <div className="metric-card" key={key}>
                    <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                    <div className="metric-value" style={{
                      color: typeof val === 'number' ? (val > 0 ? '#34D399' : val < 0 ? '#FB7185' : '#F5B942') : '#DCE6F2'
                    }}>
                      {typeof val === 'number' ? val.toFixed(3) : String(val)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 20 }}>No sentiment data.</p>
            )}
            <div className="section-label mt-6">Extracted Event Signals</div>
            <DataTable
              columns={[
                { key: 'category', label: 'Category' },
                { key: 'entity', label: 'Entity' },
                { key: 'evidence', label: 'Evidence' },
              ]}
              rows={assessment.event_signals || []}
            />
          </div>
        )}

        {/* Forecasts */}
        {activeTab === 4 && (
          <div>
            <ForecastChart forecasts={assessment.forecasts || []} />
            <DataTable
              columns={[
                { key: 'label', label: 'Indicator' },
                { key: 'current', label: 'Current' },
                { key: 'forecast', label: 'Forecast' },
                { key: 'direction', label: 'Direction' },
              ]}
              rows={assessment.forecasts || []}
            />
          </div>
        )}

        {/* Models */}
        {activeTab === 5 && (
          <div>
            <div className="results-factors">
              <div>
                <div className="section-label">Model Predictions</div>
                <BarChart
                  data={assessment.model_outputs || {}}
                  colorFn={(key, val) => {
                    const colors = { xgboost: '#22D3EE', catboost: '#A78BFA', lightgbm: '#34D399', ensemble: '#F5B942' };
                    return colors[key] || '#22D3EE';
                  }}
                  formatValue={(v) => v.toFixed(1)}
                  height={38}
                />
              </div>
              <div>
                <div className="section-label">Feature Importance (SHAP)</div>
                <BarChart
                  data={assessment.shap_explanation || {}}
                  colorFn={(key, val) => val > 0.1 ? '#F5B942' : val > 0.05 ? '#22D3EE' : '#344663'}
                  formatValue={(v) => v.toFixed(3)}
                  height={28}
                />
              </div>
            </div>

            <hr className="divider" />

            <ConfidenceVisual data={assessment.confidence_interval || {}} />
          </div>
        )}

        {/* Graph */}
        {activeTab === 6 && (
          <div>
            <div className="metrics-row mb-4">
              <div className="metric-card">
                <div className="metric-label">Graph Nodes</div>
                <div className="metric-value">
                  {(assessment.knowledge_graph?.nodes || []).length}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Graph Edges</div>
                <div className="metric-value">
                  {(assessment.knowledge_graph?.edges || []).length}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Visualisation</div>
                <div className="metric-value">Force-directed</div>
              </div>
            </div>

            <ForceGraph graphData={assessment.knowledge_graph} />
          </div>
        )}
      </div>

      {/* Raw JSON Expander */}
      <div className="expander">
        <div
          className="expander-header"
          onClick={() => setJsonExpanded(!jsonExpanded)}
        >
          <span>Raw assessment JSON</span>
          <span className={`expander-arrow ${jsonExpanded ? 'open' : ''}`}>&#9660;</span>
        </div>
        {jsonExpanded && (
          <div className="expander-body">
            <pre className="json-viewer">
              {JSON.stringify(assessment, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
