import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function FeatureImportanceChart({
  data,
}) {
  return (
    <ResponsiveContainer
      width="100%"
      height={600}
    >
      <BarChart
        data={data}
        layout="vertical"
      >
        <CartesianGrid stroke="#1f2937" />

        <XAxis
          type="number"
          stroke="#94a3b8"
        />

        <YAxis
          type="category"
          dataKey="feature"
          width={180}
          stroke="#94a3b8"
        />

        <Tooltip />

        <Bar
          dataKey="importance_pct"
          fill="#0ea5e9"
          radius={[0, 6, 6, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}