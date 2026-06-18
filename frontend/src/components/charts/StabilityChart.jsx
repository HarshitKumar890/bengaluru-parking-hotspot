import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Cell,
} from "recharts";

export default function StabilityChart({
  data,
}) {
  const counts = {};

  data.forEach((item) => {
    counts[item.stability_class] =
      (counts[item.stability_class] || 0) + 1;
  });

  const chartData = Object.entries(
    counts
  ).map(([name, value]) => ({
    name,
    value,
  }));

  const COLORS = [
    "#22c55e",
    "#eab308",
    "#ef4444",
  ];

  return (
    <ResponsiveContainer
      width="100%"
      height={350}
    >
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          outerRadius={120}
          label
        >
          {chartData.map(
            (_, index) => (
              <Cell
                key={index}
                fill={
                  COLORS[
                    index %
                      COLORS.length
                  ]
                }
              />
            )
          )}
        </Pie>

        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}