import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";

const website = {
  id: 7,
  url: "https://example.com",
  business_name: "Example Studio",
  business_context: "A neighborhood design studio",
  google_ads_connected: false,
  ga4_connected: false,
};

function fillRequiredFields() {
  fireEvent.change(screen.getByLabelText("Website URL"), { target: { value: "example.com" } });
  fireEvent.change(screen.getByLabelText("Business or organization name"), { target: { value: "Example Studio" } });
}

describe("MVP-004 website workspace", () => {
  beforeEach(() => window.localStorage.setItem("trellis_access_token", "test-token"));
  afterEach(() => {
    vi.unstubAllGlobals();
    window.localStorage.clear();
  });

  it("creates a website with optional context and opens all six views", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: website }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fillRequiredFields();
    fireEvent.change(screen.getByLabelText(/Business context/), { target: { value: "A neighborhood design studio" } });
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));

    expect(await screen.findByRole("navigation", { name: "Workspace views" })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/websites"), expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({ Authorization: "Bearer test-token" }),
      body: JSON.stringify({ url: "example.com", business_name: "Example Studio", business_context: "A neighborhood design studio" }),
    }));
    for (const view of ["Overview", "AEO", "SEO/Content", "SEM", "Reports", "Organizer"]) {
      expect(screen.getByRole("button", { name: view })).toBeInTheDocument();
    }
    fireEvent.click(screen.getByRole("button", { name: "SEM" }));
    expect(screen.getByRole("heading", { name: "SEM" })).toBeInTheDocument();
  });

  it("shows a local invalid URL state without calling the API", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fillRequiredFields();
    fireEvent.change(screen.getByLabelText("Website URL"), { target: { value: "not a url" } });
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Enter a valid website URL");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("shows loading while creation is pending", async () => {
    let resolveRequest!: (response: object) => void;
    vi.stubGlobal("fetch", vi.fn(() => new Promise((resolve) => { resolveRequest = resolve; })));
    render(<App />);
    fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    expect(screen.getByRole("button", { name: "Creating workspace…" })).toBeDisabled();
    resolveRequest({ ok: true, json: async () => ({ data: website }) });
    await screen.findByRole("navigation", { name: "Workspace views" });
  });

  it.each([
    ["conflict", "That website is already in your Trellis account."],
    ["internal_server_error", "We couldn't create your workspace. Please try again."],
  ])("shows the %s failure state", async (code, expected) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, json: async () => ({ error: code, message: "API detail" }) }));
    render(<App />);
    fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(expected));
  });
});

describe("MVP-006 visible analysis flow", () => {
  beforeEach(() => window.localStorage.setItem("trellis_access_token", "test-token"));
  afterEach(() => {
    vi.unstubAllGlobals();
    window.localStorage.clear();
  });

  it("polls understandable stages and displays persisted results", async () => {
    const run = (status: string) => ({
      id: 20, website_id: 7, status, last_completed_stage: null,
      pages_scanned_count: status === "completed" ? 3 : 0,
      error_message: null, started_at: "2026-09-06T12:00:00Z",
      completed_at: status === "completed" ? "2026-09-06T12:01:00Z" : null,
      keywords: status === "completed" ? [{ phrase: "community garden", frequency: 5, tfidf_score: 0.8 }] : [],
    });
    const responses = [
      { data: website },
      { data: run("queued") },
      { data: run("scraping") },
      { data: run("analyzing") },
      { data: run("generating") },
      { data: run("completed") },
    ];
    vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => ({ ok: true, json: async () => responses.shift() })));
    render(<App />);
    fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    await screen.findByRole("button", { name: "Analyze website" });
    fireEvent.click(screen.getByRole("button", { name: "Analyze website" }));
    expect(await screen.findByRole("status")).toHaveTextContent("queued");
    expect(await screen.findByTestId("analysis-results", {}, { timeout: 5000 })).toHaveTextContent("3 pages analyzed");
    expect(screen.getByTestId("analysis-results")).toHaveTextContent("community garden ×5");
  });

  it("offers retry after a failed run", async () => {
    const failed = { id: 20, website_id: 7, status: "failed", last_completed_stage: "analyzing", pages_scanned_count: 2, error_message: "The site timed out.", started_at: "2026-09-06T12:00:00Z", completed_at: "2026-09-06T12:01:00Z", keywords: [] };
    const queued = { ...failed, status: "queued", error_message: null, completed_at: null };
    const responses = [{ data: website }, { data: failed }, { data: queued }];
    vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => ({ ok: true, json: async () => responses.shift() })));
    render(<App />);
    fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    await screen.findByRole("button", { name: "Analyze website" });
    fireEvent.click(screen.getByRole("button", { name: "Analyze website" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("The site timed out.");
    fireEvent.click(screen.getByRole("button", { name: "Retry analysis" }));
    expect(await screen.findByRole("status")).toHaveTextContent("queued");
  });
});

describe("MVP-008 persisted recommendation views", () => {
  beforeEach(() => window.localStorage.setItem("trellis_access_token", "test-token"));
  afterEach(() => { vi.unstubAllGlobals(); window.localStorage.clear(); });

  it("loads completed AEO and SEO/content suggestions into their workspace views", async () => {
    const completed = {
      id: 20, website_id: 7, status: "completed", last_completed_stage: "generating", pages_scanned_count: 3,
      error_message: null, started_at: "2026-09-06T12:00:00Z", completed_at: "2026-09-06T12:01:00Z", keywords: [],
      suggestions: [
        { id: 1, category: "aeo", title: "Add a direct answer", description: "Answer the main question clearly.", rationale: "It makes this page easier for answer engines to interpret.", priority: "high", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: "https://example.com/", starter_outline: null, target_keywords: [] },
        { id: 2, category: "seo_content", title: "Publish a garden guide", description: "Create a useful gardening resource.", rationale: "It fills a gap in the existing website content.", priority: "medium", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: null, starter_outline: ["Choose plants"], target_keywords: [{ phrase: "community garden", recommended_usage_count: 4 }] },
      ],
    };
    const responses = [{ data: website }, { data: completed }];
    vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => ({ ok: true, json: async () => responses.shift() })));
    render(<App />); fillRequiredFields(); fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    fireEvent.click(await screen.findByRole("button", { name: "Analyze website" }));
    await screen.findByTestId("analysis-results");
    fireEvent.click(screen.getByRole("button", { name: "AEO" }));
    expect(screen.getByText("Add a direct answer")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "SEO/Content" }));
    expect(screen.getByText("Publish a garden guide")).toBeInTheDocument();
    expect(screen.getByText("Use about 4×")).toBeInTheDocument();
  });
});
