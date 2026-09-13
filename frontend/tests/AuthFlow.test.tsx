import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const auth = vi.hoisted(() => ({
  getCurrentSession: vi.fn(),
  getTestAccessToken: vi.fn(() => null),
  onAuthStateChange: vi.fn(() => () => undefined),
  signInWithPassword: vi.fn(),
  signUpWithPassword: vi.fn(),
  signOut: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("../src/auth/client", () => ({ ...auth, isAuthConfigured: true }));

import App from "../src/App";

const savedWebsite = {
  id: 7,
  url: "https://example.com",
  business_name: "Example Studio",
  business_context: null,
  google_ads_connected: false,
  ga4_connected: false,
};

function websiteListResponse(websites = [savedWebsite]) {
  return { ok: true, json: async () => ({ data: websites }) };
}

describe("application authentication flow", () => {
  afterEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.unstubAllGlobals();
    window.history.replaceState({}, "", "/");
    auth.onAuthStateChange.mockReturnValue(() => undefined);
    auth.signOut.mockResolvedValue(undefined);
  });

  it("restores an existing Supabase session", async () => {
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(websiteListResponse()));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Your websites" })).toBeVisible();
    expect(screen.getByRole("button", { name: /Open Example Studio/ })).toBeVisible();
  });

  it("shows the add form when the account has no websites", async () => {
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(websiteListResponse([])));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Add a website" })).toBeVisible();
  });

  it("opens a saved website and gives it a restorable URL", async () => {
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(websiteListResponse()));
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: /Open Example Studio/ }));
    expect(await screen.findByRole("heading", { name: "Overview" })).toBeVisible();
    expect(window.location.pathname).toBe("/websites/7");
  });

  it("restores a selected website from its URL", async () => {
    window.history.replaceState({}, "", "/websites/7");
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(websiteListResponse()));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Overview" })).toBeVisible();
    expect(screen.getByText("Example Studio", { selector: ".eyebrow" })).toBeVisible();
  });

  it("shows authentication when there is no session", async () => {
    auth.getCurrentSession.mockResolvedValue(null);
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeVisible();
  });

  it("shows authentication when session restoration fails", async () => {
    auth.getCurrentSession.mockRejectedValue(new Error("Session lookup failed"));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeVisible();
  });

  it("signs out of an authenticated workspace", async () => {
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(websiteListResponse()));
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: /Open Example Studio/ }));
    fireEvent.click(await screen.findByRole("button", { name: "Sign out" }));
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeVisible();
    expect(auth.signOut).toHaveBeenCalledOnce();
    expect(window.location.pathname).toBe("/");
  });
});
