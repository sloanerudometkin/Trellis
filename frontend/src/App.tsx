import { useEffect, useState } from "react";

import { getApiHealth } from "./api/client";

type ApiState = "checking" | "ready" | "offline";

export default function App() {
  const [apiState, setApiState] = useState<ApiState>("checking");

  useEffect(() => {
    getApiHealth()
      .then(() => setApiState("ready"))
      .catch(() => setApiState("offline"));
  }, []);

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl items-center px-6 py-16">
      <section aria-labelledby="page-title">
        <p className="font-mono text-sm uppercase tracking-[0.18em] text-moss">
          MVP foundation
        </p>
        <h1 id="page-title" className="mt-3 font-display text-5xl text-ink">
          Trellis
        </h1>
        <p className="mt-5 max-w-xl text-lg leading-8 text-ink/80">
          Your paid and organic search growth strategy—all in one place.
        </p>
        <p className="mt-8" role="status">
          API status: <strong>{apiState}</strong>
        </p>
      </section>
    </main>
  );
}
