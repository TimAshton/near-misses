import { useState } from "react";
import { stormSatelliteImageUrl } from "../../lib/satelliteImage";

interface StormSatelliteImageProps {
  lat: number;
  lng: number;
  occurredAt: string;
}

/** Recent GOES-East satellite capture around a storm's reported center —
 * see lib/satelliteImage.ts for why NASA GIBS rather than Google/Mapbox. */
export function StormSatelliteImage({ lat, lng, occurredAt }: StormSatelliteImageProps) {
  const [failed, setFailed] = useState(false);
  const url = stormSatelliteImageUrl(lat, lng, occurredAt);

  return (
    <div
      data-testid="incident-satellite-image"
      className="flex h-64 w-full items-center justify-center overflow-hidden rounded-lg border border-gray-800 bg-gray-900"
    >
      {failed ? (
        <p className="px-4 text-center text-xs text-gray-500">Satellite image unavailable</p>
      ) : (
        <img
          src={url}
          alt="Recent satellite image of the storm"
          className="h-full w-full object-cover"
          onError={() => setFailed(true)}
        />
      )}
    </div>
  );
}
