import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function JunctionChart({
  data,
}) {
  return (
    <ResponsiveContainer
      width="100%"
      height={400}
    >
      <BarChart data={data}>
        <CartesianGrid stroke="#1f2937" />

        <XAxis
          dataKey="junction_name"
          stroke="#94a3b8"
        />

        <YAxis stroke="#94a3b8" />

        <Tooltip />

        <Bar
          dataKey="total_cases"
          fill="#0ea5e9"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}