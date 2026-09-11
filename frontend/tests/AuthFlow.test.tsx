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

describe("application authentication flow", () => {
  afterEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.unstubAllGlobals();
    auth.onAuthStateChange.mockReturnValue(() => undefined);
    auth.signOut.mockResolvedValue(undefined);
  });

  it("restores an existing Supabase session", async () => {
    auth.getCurrentSession.mockResolvedValue({ access_token: "restored-token" });
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Add a website" })).toBeVisible();
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
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { id: 7, url: "https://example.com", business_name: "Example Studio", business_context: null, google_ads_connected: false, ga4_connected: false } }),
    }));
    render(<App />);
    fireEvent.change(await screen.findByLabelText("Website URL"), { target: { value: "example.com" } });
    fireEvent.change(screen.getByLabelText("Business or organization name"), { target: { value: "Example Studio" } });
    fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
    fireEvent.click(await screen.findByRole("button", { name: "Sign out" }));
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeVisible();
    expect(auth.signOut).toHaveBeenCalledOnce();
  });
});
