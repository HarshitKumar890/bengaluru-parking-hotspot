import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function StationChart({ data }) {
  return (
    <ResponsiveContainer
      width="100%"
      height={350}
    >
      <BarChart data={data}>
        <CartesianGrid stroke="#1F2937" />

        <XAxis
          dataKey="police_station"
          stroke="#CBD5E1"
        />

        <YAxis stroke="#CBD5E1" />

        <Tooltip />

        <Bar
          dataKey="total_cases"
          fill="#38BDF8"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}