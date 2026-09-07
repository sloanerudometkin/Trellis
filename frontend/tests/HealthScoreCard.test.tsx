import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { HealthScoreCard } from "../src/HealthScoreCard";

const disclosure = "Organic snapshot: 35% AEO, 35% technical, and 30% SEO/content. SEM is excluded.";

describe("MVP-012 organic Health Score", () => {
  it("shows a first-run score with no misleading delta", () => {
    render(<HealthScoreCard score={42} delta={null} history={[{ analysis_id: 1, score: 42, completed_at: null }]} disclosure={disclosure} />);
    expect(screen.getByRole("heading", { name: "42/100" })).toBeInTheDocument();
    expect(screen.getByText("First scored scan — no prior change yet.")).toBeInTheDocument();
    expect(screen.getByText(/SEM is excluded/)).toBeInTheDocument();
  });

  it("shows later-run change and an accessible trend", () => {
    render(<HealthScoreCard score={70} delta={28} history={[{ analysis_id: 1, score: 42, completed_at: null }, { analysis_id: 2, score: 70, completed_at: null }]} disclosure={disclosure} />);
    expect(screen.getByText("+28 points since prior scan")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Organic Health Score trend: 42, 70" })).toBeInTheDocument();
  });
});
