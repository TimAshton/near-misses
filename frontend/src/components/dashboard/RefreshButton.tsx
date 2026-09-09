import { useState } from "react";
import { triggerPoll } from "../../lib/api";

interface RefreshButtonProps {
  onDone?: () => void;
}

export function RefreshButton({ onDone }: RefreshButtonProps) {
  const [state, setState] = useState<"idle" | "loading" | "error">("idle");

  async function handleClick() {
    setState("loading");
    try {
      await triggerPoll();
      setState("idle");
      onDone?.();
    } catch {
      setState("error");
    }
  }

  return (
    <button
      data-testid="refresh-button"
      onClick={handleClick}
      disabled={state === "loading"}
      className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-60"
    >
      {state === "loading" ? "Refreshing…" : state === "error" ? "Retry refresh" : "Refresh now"}
    </button>
  );
}
