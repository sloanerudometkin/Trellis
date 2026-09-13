import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthScreen } from "../src/auth/AuthScreen";

describe("Supabase authentication", () => {
  afterEach(() => vi.restoreAllMocks());

  it("signs an existing user in with email and password", async () => {
    const signIn = vi.fn().mockResolvedValue(undefined);
    render(<AuthScreen configured onSignIn={signIn} onSignUp={vi.fn()} />);

    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "sloane@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secure-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(signIn).toHaveBeenCalledWith("sloane@example.com", "secure-password"));
  });

  it("creates an account with name, email, and password", async () => {
    const signUp = vi.fn().mockResolvedValue({ confirmationRequired: true });
    render(<AuthScreen configured onSignIn={vi.fn()} onSignUp={signUp} />);

    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Sloane" } });
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "sloane@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secure-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Create my account" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Check your email");
    expect(signUp).toHaveBeenCalledWith("Sloane", "sloane@example.com", "secure-password");
  });

  it("shows a safe authentication error", async () => {
    const signIn = vi.fn().mockRejectedValue(new Error("Invalid login credentials"));
    render(<AuthScreen configured onSignIn={signIn} onSignUp={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "sloane@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrong-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("email and password");
  });

  it("explains when Supabase configuration is missing", () => {
    render(<AuthScreen configured={false} onSignIn={vi.fn()} onSignUp={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Supabase connection");
    expect(screen.getByRole("button", { name: "Sign in" })).toBeDisabled();
  });
});
