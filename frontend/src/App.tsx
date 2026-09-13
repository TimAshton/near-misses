import { Navigate, Route, Routes } from "react-router-dom";
import { MapPage } from "./routes/MapPage";
import { Dashboard } from "./routes/Dashboard";
import { Reports } from "./routes/Reports";
import { IncidentDetail } from "./routes/IncidentDetail";
import { About } from "./routes/About";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/dashboard" element={<Navigate to="/" replace />} />
      <Route path="/map" element={<MapPage />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/incidents/:id" element={<IncidentDetail />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
}
