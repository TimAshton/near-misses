import { Route, Routes } from "react-router-dom";
import { Home } from "./routes/Home";
import { MapPage } from "./routes/MapPage";
import { Dashboard } from "./routes/Dashboard";
import { Reports } from "./routes/Reports";
import { IncidentDetail } from "./routes/IncidentDetail";
import { About } from "./routes/About";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/map" element={<MapPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/incidents/:id" element={<IncidentDetail />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
}
