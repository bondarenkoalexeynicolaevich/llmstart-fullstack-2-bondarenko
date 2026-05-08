"use client";

import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ScatterPoint } from "@/lib/api/types";

export type ScatterChartMeta = {
  axis_x_label: string;
  axis_y_label: string;
};

type ScatterDotProps = {
  cx?: number;
  cy?: number;
  payload?: ScatterPoint;
};

function ScatterDotShape({ cx, cy, payload }: ScatterDotProps) {
  if (cx == null || cy == null || !payload) return null;
  const r = payload.rank <= 3 ? 11 : 7;
  let fill = "hsl(var(--primary))";
  if (payload.rank === 1) fill = "#ca8a04";
  else if (payload.rank === 2) fill = "#94a3b8";
  else if (payload.rank === 3) fill = "#ea580c";
  return (
    <circle
      cx={cx}
      cy={cy}
      r={r}
      fill={fill}
      stroke="hsl(var(--background))"
      strokeWidth={2}
      aria-label={`${payload.display_name}, место ${payload.rank}`}
    />
  );
}

export function LeaderboardScatterChart({
  data,
  meta,
}: {
  data: ScatterPoint[];
  meta: ScatterChartMeta;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart margin={{ top: 16, right: 16, bottom: 36, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          type="number"
          dataKey="x"
          name={meta.axis_x_label}
          tick={{ fontSize: 11 }}
          label={{
            value: meta.axis_x_label,
            position: "bottom",
            offset: 12,
            fontSize: 11,
          }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={meta.axis_y_label}
          tick={{ fontSize: 11 }}
          label={{
            value: meta.axis_y_label,
            angle: -90,
            position: "insideLeft",
            fontSize: 11,
          }}
        />
        <Tooltip
          cursor={{ strokeDasharray: "3 3" }}
          content={({ active, payload }) => {
            if (!active || !payload?.[0]) return null;
            const p = payload[0].payload as ScatterPoint;
            return (
              <div className="rounded-md border border-border bg-popover px-3 py-2 text-xs shadow-md">
                <div className="font-medium">{p.display_name}</div>
                <div className="text-muted-foreground">Место: {p.rank}</div>
                <div>
                  {meta.axis_x_label}: {p.x}
                </div>
                <div>
                  {meta.axis_y_label}:{" "}
                  {typeof p.y === "number" ? `${p.y.toFixed(1)}%` : p.y}
                </div>
              </div>
            );
          }}
        />
        <Scatter
          data={data}
          fill="hsl(var(--primary))"
          shape={ScatterDotShape}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
