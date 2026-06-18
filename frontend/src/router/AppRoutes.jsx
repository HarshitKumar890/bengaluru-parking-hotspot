import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";
import Hotspots from "../pages/Hotspots";
import Forecast from "../pages/Forecast";
import Patrol from "../pages/Patrol";
import RiskZones from "../pages/RiskZones";
import Stations from "../pages/Stations";
import Junctions from "../pages/Junctions";
import Stability from "../pages/Stability";
import FeatureImportance from "../pages/FeatureImportance";
import Downloads from "../pages/Downloads";
import About from "../pages/About";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/hotspots" element={<Hotspots />} />
      <Route path="/forecast" element={<Forecast />} />
      <Route path="/patrol" element={<Patrol />} />
      <Route path="/risk-zones" element={<RiskZones />} />
      <Route path="/stations" element={<Stations />} />
      <Route path="/junctions" element={<Junctions />} />
      <Route path="/stability" element={<Stability />} />
      <Route path="/feature-importance" element={<FeatureImportance />} />
      <Route path="/downloads" element={<Downloads />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
}