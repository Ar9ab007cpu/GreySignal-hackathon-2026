export default function RiskGauge({ score }) {
  const cx = 150;
  const cy = 140;
  const r = 110;
  const strokeWidth = 16;

  const clampedScore = Math.max(0, Math.min(100, score));

  /* Full background arc (semicircle, left-to-right through top) */
  const bgPath = `M ${cx - r} ${cy} A ${r} ${r} 0 1 1 ${cx + r} ${cy}`;

  /* Score arc: sweeps from left toward right */
  const scoreAngle = Math.PI * (1 - clampedScore / 100);
  const endX = cx + r * Math.cos(scoreAngle);
  const endY = cy - r * Math.sin(scoreAngle);
  const largeArc = clampedScore > 50 ? 1 : 0;
  const scorePath =
    clampedScore > 0
      ? `M ${cx - r} ${cy} A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY}`
      : '';

  const riskColor = (s) => {
    if (s < 35) return '#34D399';
    if (s < 60) return '#F5B942';
    if (s < 78) return '#FB7185';
    return '#F43F5E';
  };

  const ratingText = (s) => {
    if (s < 35) return 'Low risk';
    if (s < 60) return 'Moderate risk';
    if (s < 78) return 'High risk';
    return 'Critical risk';
  };

  const color = riskColor(clampedScore);

  /* Tick marks */
  const ticks = [0, 25, 50, 75, 100];

  return (
    <div className="gauge-wrapper">
      <svg className="gauge-svg" viewBox="0 0 300 190">
        {/* Background arc */}
        <path
          d={bgPath}
          fill="none"
          stroke="#1A2740"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Colored zone hints (subtle) */}
        {[
          { start: 0, end: 35, color: 'rgba(52,211,153,0.07)' },
          { start: 35, end: 60, color: 'rgba(245,185,66,0.07)' },
          { start: 60, end: 78, color: 'rgba(251,113,133,0.07)' },
          { start: 78, end: 100, color: 'rgba(244,63,94,0.07)' },
        ].map(({ start, end, color: zoneColor }, i) => {
          const a1 = Math.PI * (1 - start / 100);
          const a2 = Math.PI * (1 - end / 100);
          const x1 = cx + r * Math.cos(a1);
          const y1 = cy - r * Math.sin(a1);
          const x2 = cx + r * Math.cos(a2);
          const y2 = cy - r * Math.sin(a2);
          const la = end - start > 50 ? 1 : 0;
          return (
            <path
              key={i}
              d={`M ${x1} ${y1} A ${r} ${r} 0 ${la} 1 ${x2} ${y2}`}
              fill="none"
              stroke={zoneColor}
              strokeWidth={strokeWidth + 10}
              strokeLinecap="butt"
            />
          );
        })}

        {/* Score arc */}
        {scorePath && (
          <path
            d={scorePath}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            style={{
              filter: `drop-shadow(0 0 10px ${color}55)`,
            }}
          />
        )}

        {/* Tick marks */}
        {ticks.map((tick) => {
          const angle = Math.PI * (1 - tick / 100);
          const innerR = r - strokeWidth / 2 - 6;
          const outerR = r - strokeWidth / 2 - 2;
          const x1t = cx + innerR * Math.cos(angle);
          const y1t = cy - innerR * Math.sin(angle);
          const x2t = cx + outerR * Math.cos(angle);
          const y2t = cy - outerR * Math.sin(angle);
          return (
            <line
              key={tick}
              x1={x1t}
              y1={y1t}
              x2={x2t}
              y2={y2t}
              stroke="#344663"
              strokeWidth={1.5}
              strokeLinecap="round"
            />
          );
        })}

        {/* Score text */}
        <text
          x={cx}
          y={cy - 16}
          textAnchor="middle"
          fill={color}
          fontSize="42"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          {Math.round(clampedScore)}
        </text>
        <text
          x={cx}
          y={cy + 10}
          textAnchor="middle"
          fill="#5F7089"
          fontSize="13"
          fontWeight="600"
          fontFamily="Inter, sans-serif"
        >
          / 100
        </text>

        {/* Rating label */}
        <text
          x={cx}
          y={cy + 36}
          textAnchor="middle"
          fill={color}
          fontSize="13"
          fontWeight="700"
          fontFamily="Inter, sans-serif"
          letterSpacing="0.04em"
        >
          {ratingText(clampedScore).toUpperCase()}
        </text>
      </svg>
    </div>
  );
}
