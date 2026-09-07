import type { HealthScoreHistoryResponse } from "./api/contracts";

const WIDTH = 320;
const HEIGHT = 104;
const PADDING = 12;

function trendPoints(history: HealthScoreHistoryResponse[]) {
  return history.map((item, index) => {
    const x = history.length === 1 ? WIDTH / 2 : PADDING + index * ((WIDTH - PADDING * 2) / (history.length - 1));
    const y = PADDING + (100 - item.score) * ((HEIGHT - PADDING * 2) / 100);
    return { ...item, x, y };
  });
}

export function HealthScoreCard({ score, delta, history, disclosure }: { score: number; delta: number | null; history: HealthScoreHistoryResponse[]; disclosure: string }) {
  const points = trendPoints(history);
  const deltaMessage = delta === null
    ? "First scored scan — no prior change yet."
    : `${delta > 0 ? "+" : ""}${delta} points since prior scan`;

  return (
    <section className="health-score-card" aria-labelledby="health-score-title">
      <div>
        <p className="eyebrow">Organic Health Score</p>
        <h3 id="health-score-title" className="health-score-value">{score}<span>/100</span></h3>
        <p className="health-score-delta">{deltaMessage}</p>
        <p className="health-score-disclosure">{disclosure}</p>
      </div>
      <div>
        <p className="health-score-trend-label">Score trend</p>
        <svg className="health-score-chart" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={`Organic Health Score trend: ${history.map((item) => item.score).join(", ")}`}>
          <line x1={PADDING} y1={HEIGHT - PADDING} x2={WIDTH - PADDING} y2={HEIGHT - PADDING} />
          {points.length > 1 && <polyline points={points.map((point) => `${point.x},${point.y}`).join(" ")} />}
          {points.map((point) => <circle key={point.analysis_id} cx={point.x} cy={point.y} r="5"><title>Analysis {point.analysis_id}: {point.score}</title></circle>)}
        </svg>
      </div>
    </section>
  );
}
