import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";


describe("Trellis application scaffold", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the product identity and reports a healthy API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", service: "trellis-api" }),
      }),
    );

    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Trellis" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("checking");
    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent("ready"),
    );
  });
});
