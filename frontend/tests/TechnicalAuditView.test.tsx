import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TechnicalAuditView } from "../src/TechnicalAuditView";

describe("MVP-010 technical audit", () => {
  it("leads with a plain-language summary and shows prioritized findings", () => {
    render(<TechnicalAuditView audit={{ summary: "Fix first: Add one clear H1 because it defines the page topic.", findings: [
      { id: 1, finding_type: "missing_h1", severity: "high", explanation: "Add one clear H1 heading.", affected_page_url: "https://example.com/", related_page_url: null, resolution_status: "open" },
      { id: 2, finding_type: "thin_content", severity: "medium", explanation: "Add useful original detail.", affected_page_url: "https://example.com/about", related_page_url: null, resolution_status: "open" },
    ] }} />);
    expect(screen.getByTestId("fix-first-summary")).toHaveTextContent("Fix first");
    const findings = screen.getAllByRole("listitem");
    expect(findings[0]).toHaveTextContent("Missing H1");
    expect(findings[1]).toHaveTextContent("Thin content");
  });
});
