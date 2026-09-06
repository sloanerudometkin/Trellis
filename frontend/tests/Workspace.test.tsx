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
