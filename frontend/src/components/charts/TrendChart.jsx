import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

const data = [
  { month: "Jan", value: 120 },
  { month: "Feb", value: 180 },
  { month: "Mar", value: 160 },
  { month: "Apr", value: 220 },
  { month: "May", value: 280 },
];

export default function TrendChart() {
  return (
    <ResponsiveContainer
      width="100%"
      height={300}
    >
      <LineChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />

        <Line
          type="monotone"
          dataKey="value"
          stroke="#38BDF8"
          strokeWidth={3}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}