"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Alert, AlertAction, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { fetchFlowLeaderboard } from "@/lib/api/flow-teacher";
import type {
  LeaderboardResponse,
  LeaderboardRow,
  ScatterPoint,
} from "@/lib/api/types";
import { getSession } from "@/lib/session";
import type { WebClientSession } from "@/lib/types";
import type { ScatterChartMeta } from "@/components/charts/leaderboard-scatter-chart";

const LeaderboardScatterChart = dynamic(
  () =>
    import("@/components/charts/leaderboard-scatter-chart").then(
      (m) => m.LeaderboardScatterChart,
    ),
  {
    ssr: false,
    loading: () => <Skeleton className="h-[420px] w-full" />,
  },
);

type ViewMode = "table" | "chart";

function MedalCell({ medal }: { medal: LeaderboardRow["medal"] }) {
  if (!medal) {
    return <span className="text-muted-foreground">—</span>;
  }
  const label =
    medal === "gold" ? "Золото" : medal === "silver" ? "Серебро" : "Бронза";
  const emoji = medal === "gold" ? "🥇" : medal === "silver" ? "🥈" : "🥉";
  return (
    <span aria-label={label} title={label}>
      <span aria-hidden>{emoji}</span>
    </span>
  );
}

function LessonDots({
  statuses,
}: {
  statuses: LeaderboardRow["lesson_statuses"];
}) {
  return (
    <div className="flex flex-wrap gap-1" aria-label="Прогресс по урокам">
      {statuses.map((ls, i) => (
        <span
          key={ls.lesson_id}
          title={`Урок ${i + 1}`}
          className={cn(
            "inline-block size-2 shrink-0 rounded-full",
            ls.state === "done" && "bg-emerald-500",
            ls.state === "partial" && "bg-amber-500",
            ls.state === "none" &&
              "border border-muted-foreground/60 bg-transparent",
          )}
        />
      ))}
    </div>
  );
}

function ProgressBar({ value }: { value: number }) {
  const v = Math.min(100, Math.max(0, value));
  return (
    <div className="flex min-w-[120px] items-center gap-2">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-[width]"
          style={{ width: `${v}%` }}
        />
      </div>
      <span className="tabular-nums text-xs text-muted-foreground">
        {v.toFixed(1)}%
      </span>
    </div>
  );
}

export function LeaderboardClient() {
  const [session, setSession] = useState<WebClientSession | null>(() =>
    getSession(),
  );

  useEffect(() => {
    queueMicrotask(() => {
      setSession(getSession());
    });
  }, []);

  const [mode, setMode] = useState<ViewMode>("table");
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const flowId = session?.flow_id ?? "";

  const load = useCallback(async () => {
    if (!flowId) return;
    setBusy(true);
    setError(null);
    try {
      setData(await fetchFlowLeaderboard(flowId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setBusy(false);
      setLoading(false);
    }
  }, [flowId]);

  useEffect(() => {
    if (!flowId) return;
    queueMicrotask(() => {
      void load();
    });
  }, [flowId, load]);

  if (!session) {
    return (
      <p className="text-sm text-muted-foreground">Загрузка сессии…</p>
    );
  }

  const showSkeleton = loading && !data;
  const tableRows = data?.table ?? [];
  const hasRows = tableRows.length > 0;

  const scatterMeta: ScatterChartMeta | null = data
    ? {
        axis_x_label: data.scatter_meta.axis_x_label,
        axis_y_label: data.scatter_meta.axis_y_label,
      }
    : null;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Лидерборд</h1>
          <p className="text-sm text-muted-foreground">
            Сравнение прогресса участников потока.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="flex rounded-lg border border-border p-0.5"
            role="tablist"
            aria-label="Режим отображения"
          >
            <Button
              type="button"
              role="tab"
              aria-selected={mode === "table"}
              variant={mode === "table" ? "default" : "ghost"}
              size="sm"
              className="rounded-md"
              onClick={() => setMode("table")}
            >
              Таблица
            </Button>
            <Button
              type="button"
              role="tab"
              aria-selected={mode === "chart"}
              variant={mode === "chart" ? "default" : "ghost"}
              size="sm"
              className="rounded-md"
              onClick={() => setMode("chart")}
            >
              Карта
            </Button>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => void load()}
            disabled={busy || !flowId}
          >
            <RefreshCw
              data-icon="inline-start"
              className={cn(busy && "animate-spin")}
              aria-hidden
            />
            Обновить
          </Button>
        </div>
      </div>

      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
          <AlertAction>
            <Button
              variant="outline"
              size="sm"
              onClick={() => void load()}
            >
              Повторить
            </Button>
          </AlertAction>
        </Alert>
      ) : null}

      {showSkeleton ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-40" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-48 w-full" />
          </CardContent>
        </Card>
      ) : null}

      {!loading && !error && data && !hasRows ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Нет студентов в потоке для рейтинга.
          </CardContent>
        </Card>
      ) : null}

      {data && hasRows ? (
        <>
          {mode === "table" ? (
            <Card className={cn(busy && "opacity-70")}>
              <CardHeader>
                <CardTitle>Таблица</CardTitle>
                <CardDescription>
                  Место, общий прогресс и статусы по урокам.
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-x-auto">
                <table className="w-full min-w-[640px] border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-muted-foreground">
                      <th className="pb-2 pr-3 font-medium">#</th>
                      <th className="pb-2 pr-3 font-medium">Участник</th>
                      <th className="pb-2 pr-3 font-medium">Прогресс</th>
                      <th className="pb-2 pr-3 font-medium">Уроки</th>
                      <th className="pb-2 font-medium">Медаль</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tableRows.map((row) => (
                      <tr
                        key={row.participant_id}
                        className="border-b border-border/60"
                      >
                        <td className="py-2 pr-3 tabular-nums">{row.rank}</td>
                        <td className="py-2 pr-3 font-medium">
                          {row.display_name}
                        </td>
                        <td className="py-2 pr-3">
                          <ProgressBar value={row.overall_progress} />
                        </td>
                        <td className="py-2 pr-3">
                          <LessonDots statuses={row.lesson_statuses} />
                        </td>
                        <td className="py-2 text-lg">
                          <MedalCell medal={row.medal} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          ) : (
            <Card className={cn(busy && "opacity-70")}>
              <CardHeader>
                <CardTitle>Карта</CardTitle>
                {scatterMeta ? (
                  <CardDescription>
                    {scatterMeta.axis_y_label} по вертикали,{" "}
                    {scatterMeta.axis_x_label} по горизонтали.
                  </CardDescription>
                ) : null}
              </CardHeader>
              <CardContent>
                <div
                  className="h-[420px] w-full"
                  role="img"
                  aria-label="Диаграмма рассеяния лидерборда"
                >
                  {scatterMeta ? (
                    <LeaderboardScatterChart
                      data={data.scatter as ScatterPoint[]}
                      meta={scatterMeta}
                    />
                  ) : null}
                </div>
                <p className="mt-2 text-xs text-muted-foreground">
                  Три лучших места выделены цветом и большим размером точки.
                </p>
              </CardContent>
            </Card>
          )}
        </>
      ) : null}
    </div>
  );
}
