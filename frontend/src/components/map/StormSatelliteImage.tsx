import { useEffect, useState } from "react";
import { candidateSatelliteDates, stormSatelliteImageUrl } from "../../lib/satelliteImage";

interface StormSatelliteImageProps {
  lat: number;
  lng: number;
  occurredAt: string;
}

/** Recent satellite capture around a storm's reported center. Tries each of
 * candidateSatelliteDates() in turn and checks the `Data-Present` response
 * header rather than trusting the image alone — see lib/satelliteImage.ts
 * for why a "no data" response still comes back as a valid, blank JPEG. */
export function StormSatelliteImage({ lat, lng, occurredAt }: StormSatelliteImageProps) {
  const [src, setSrc] = useState<string | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "unavailable">("loading");

  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;
    setStatus("loading");
    setSrc(null);

    async function load() {
      for (const date of candidateSatelliteDates(occurredAt)) {
        try {
          const res = await fetch(stormSatelliteImageUrl(lat, lng, date));
          if (!res.ok || res.headers.get("data-present") === "false") continue;
          const blob = await res.blob();
          if (cancelled) return;
          objectUrl = URL.createObjectURL(blob);
          setSrc(objectUrl);
          setStatus("ready");
          return;
        } catch {
          // network error on this date — fall through to the next candidate
        }
      }
      if (!cancelled) setStatus("unavailable");
    }

    load();
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [lat, lng, occurredAt]);

  return (
    <div
      data-testid="incident-satellite-image"
      className="flex h-64 w-full items-center justify-center overflow-hidden rounded-lg border border-gray-800 bg-gray-900"
    >
      {status === "ready" && src ? (
        <img
          src={src}
          alt="Recent satellite image of the storm"
          className="h-full w-full object-cover"
        />
      ) : (
        <p className="px-4 text-center text-xs text-gray-500">
          {status === "loading" ? "Loading satellite image…" : "Satellite image unavailable"}
        </p>
      )}
    </div>
  );
}
