import { Routes, Route } from "react-router-dom";

import DashboardLayout from "../components/layout/DashboardLayout.jsx";

// Pages
import Dashboard from "../pages/Dashboard.jsx";
import Hotspots from "../pages/Hotspots.jsx";
import Forecast from "../pages/Forecast.jsx";
import Patrol from "../pages/Patrol.jsx";
import RiskZones from "../pages/RiskZones.jsx";
import Stations from "../pages/Stations.jsx";
import Junctions from "../pages/Junctions.jsx";
import Stability from "../pages/Stability.jsx";
import FeatureImportance from "../pages/FeatureImportance.jsx";
import Downloads from "../pages/Downloads.jsx";
import About from "../pages/About.jsx";

const LayoutWrapper = ({ children }) => {
  return (
    <DashboardLayout>
      {children}
    </DashboardLayout>
  );
};

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <LayoutWrapper>
            <Dashboard />
          </LayoutWrapper>
        }
      />

      <Route
        path="/hotspots"
        element={
          <LayoutWrapper>
            <Hotspots />
          </LayoutWrapper>
        }
      />

      <Route
        path="/forecast"
        element={
          <LayoutWrapper>
            <Forecast />
          </LayoutWrapper>
        }
      />

      <Route
        path="/patrol"
        element={
          <LayoutWrapper>
            <Patrol />
          </LayoutWrapper>
        }
      />

      <Route
        path="/risk-zones"
        element={
          <LayoutWrapper>
            <RiskZones />
          </LayoutWrapper>
        }
      />

      <Route
        path="/stations"
        element={
          <LayoutWrapper>
            <Stations />
          </LayoutWrapper>
        }
      />

      <Route
        path="/junctions"
        element={
          <LayoutWrapper>
            <Junctions />
          </LayoutWrapper>
        }
      />

      <Route
        path="/stability"
        element={
          <LayoutWrapper>
            <Stability />
          </LayoutWrapper>
        }
      />

      <Route
        path="/feature-importance"
        element={
          <LayoutWrapper>
            <FeatureImportance />
          </LayoutWrapper>
        }
      />

      <Route
        path="/downloads"
        element={
          <LayoutWrapper>
            <Downloads />
          </LayoutWrapper>
        }
      />

      <Route
        path="/about"
        element={
          <LayoutWrapper>
            <About />
          </LayoutWrapper>
        }
      />
    </Routes>
  );
}