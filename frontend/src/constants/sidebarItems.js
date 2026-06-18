import {
  LayoutDashboard,
  Map,
  LineChart,
  Shield,
  AlertTriangle,
  Building2,
  Route,
  Activity,
  BarChart3,
  Download,
  Info,
} from "lucide-react";

export const sidebarItems = [
  {
    title: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Hotspot Map",
    path: "/hotspots",
    icon: Map,
  },
  {
    title: "Forecast Engine",
    path: "/forecast",
    icon: LineChart,
  },
  {
    title: "Patrol Recommendations",
    path: "/patrol",
    icon: Shield,
  },
  {
    title: "Congestion Risk",
    path: "/risk-zones",
    icon: AlertTriangle,
  },
  {
    title: "Station Analytics",
    path: "/stations",
    icon: Building2,
  },
  {
    title: "Junction Analytics",
    path: "/junctions",
    icon: Route,
  },
  {
    title: "Stability Explorer",
    path: "/stability",
    icon: Activity,
  },
  {
    title: "Feature Importance",
    path: "/feature-importance",
    icon: BarChart3,
  },
  {
    title: "Data Download",
    path: "/downloads",
    icon: Download,
  },
  {
    title: "About",
    path: "/about",
    icon: Info,
  },
];