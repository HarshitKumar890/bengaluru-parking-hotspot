import { Routes, Route } from "react-router-dom";

import DashboardLayout from "../components/layout/DashboardLayout";

// Pages
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