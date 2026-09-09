import type { Incident } from "./types";

// VITE_WS_URL is used verbatim when set (e.g. local dev, pointing at a
// separately-hosted backend). Left empty, the WS endpoint is derived as
// same-origin — the deployed setup routes /ws through the same CloudFront
// distribution as the frontend (see infra/terraform/modules/frontend-hosting),
// so the frontend never needs to know the backend's real domain at build time.
function resolveWsUrl(): string {
  const explicit = import.meta.env.VITE_WS_URL;
  if (explicit) return explicit;
  if (typeof window === "undefined") return "ws://localhost:8000/ws";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

export const WS_URL = resolveWsUrl();

const RECONNECT_DELAY_MS = 3000;

export type IncidentListener = (incident: Incident) => void;

export class IncidentSocket {
  private socket: WebSocket | null = null;
  private listeners = new Set<IncidentListener>();
  private closedByUser = false;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  connect(): void {
    this.closedByUser = false;
    this.open();
  }

  private open(): void {
    this.socket = new WebSocket(WS_URL);

    this.socket.onmessage = (event) => {
      try {
        const incident = JSON.parse(event.data) as Incident;
        for (const listener of this.listeners) listener(incident);
      } catch {
        // ignore malformed messages
      }
    };

    this.socket.onclose = () => {
      if (this.closedByUser) return;
      this.reconnectTimer = setTimeout(() => this.open(), RECONNECT_DELAY_MS);
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  subscribe(listener: IncidentListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  close(): void {
    this.closedByUser = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.socket?.close();
  }
}
