import { useEffect, useRef } from "react";
import { IncidentSocket } from "../lib/ws";
import type { Incident } from "../lib/types";

export function useWebSocketIncidents(onIncident: (incident: Incident) => void): void {
  const callbackRef = useRef(onIncident);
  callbackRef.current = onIncident;

  useEffect(() => {
    const socket = new IncidentSocket();
    const unsubscribe = socket.subscribe((incident) => callbackRef.current(incident));
    socket.connect();
    return () => {
      unsubscribe();
      socket.close();
    };
  }, []);
}
