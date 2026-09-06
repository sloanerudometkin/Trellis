import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { OrganizerView } from "../src/OrganizerView";
import type { OrganizerItemResponse } from "../src/api/contracts";

const items: OrganizerItemResponse[] = [
  { id: 1, website_id: 12, suggestion_id: 11, item_type: "aeo", title: "Add FAQ schema", stage: "backlog", published_at: null },
  { id: 2, website_id: 12, suggestion_id: 12, item_type: "seo_content", title: "Publish a garden guide", stage: "in_production", published_at: null },
  { id: 3, website_id: 12, suggestion_id: 13, item_type: "sem", title: "Group local keywords", stage: "in_review", published_at: null },
];

describe("MVP-009 Organizer", () => {
  it("separates the AEO checklist from the combined SEO task board", () => {
    render(<OrganizerView items={items} loading={false} error={null} onStageChange={vi.fn()} />);
    expect(screen.getByRole("heading", { name: "AEO checklist" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Combined SEO task view" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "In Production" })).toHaveTextContent("Publish a garden guide");
    expect(screen.getByRole("region", { name: "In Review" })).toHaveTextContent("Group local keywords");
  });

  it("shows every required board stage and updates a task", () => {
    const onStageChange = vi.fn();
    render(<OrganizerView items={items} loading={false} error={null} onStageChange={onStageChange} />);
    for (const name of ["Backlog", "In Production", "In Review", "Published"]) expect(screen.getByRole("region", { name })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Stage for Publish a garden guide"), { target: { value: "published" } });
    expect(onStageChange).toHaveBeenCalledWith(items[1], "published");
  });
});
