import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function PatrolChart({
  data,
}) {
  return (
    <ResponsiveContainer
      width="100%"
      height={450}
    >
      <BarChart data={data}>
        <CartesianGrid stroke="#1f2937" />

        <XAxis
          dataKey="patrol_rank"
          stroke="#94a3b8"
        />

        <YAxis stroke="#94a3b8" />

        <Tooltip />

        <Bar
          dataKey="priority_score"
          fill="#f59e0b"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}