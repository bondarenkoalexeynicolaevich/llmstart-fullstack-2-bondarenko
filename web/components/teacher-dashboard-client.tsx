"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ChevronRight, RefreshCw } from "lucide-react";

import { Alert, AlertAction, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  fetchProgressMatrix,
  fetchQuestionFeed,
  fetchSubmissionFeed,
  fetchTeacherDashboard,
} from "@/lib/api/flow-teacher";
import type {
  DashboardKpi,
  MatrixCell,
  ProgressMatrixResponse,
  QuestionFeedItem,
  SubmissionFeedItem,
  TeacherDashboardResponse,
} from "@/lib/api/types";
import { getSession } from "@/lib/session";
import type { WebClientSession } from "@/lib/types";
import type { ActivityChartPoint } from "@/components/charts/activity-line-chart";

const ActivityLineChart = dynamic(
  () =>
    import("@/components/charts/activity-line-chart").then(
      (m) => m.ActivityLineChart,
    ),
  {
    ssr: false,
    loading: () => <Skeleton className="h-full w-full" />,
  },
);

const FEED_PAGE = 20;

const KPI_TITLE: Record<DashboardKpi["id"], string> = {
  active_students: "Активные студенты",
  submissions_count: "Сдачи",
  questions_count: "Вопросы к ассистенту",
  completion_rate: "Завершённость (approved)",
};

const STATUS_LABEL: Record<SubmissionFeedItem["status"], string> = {
  submitted: "Отправлено",
  reviewed: "Проверено",
  approved: "Принято",
};

const DATE_FMT = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const DATETIME_FMT = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

const DAY_FMT = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
});

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return DATE_FMT.format(d);
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return DATETIME_FMT.format(d);
}

function formatDayLabel(isoDate: string): string {
  const d = new Date(isoDate + "T12:00:00Z");
  if (Number.isNaN(d.getTime())) return isoDate.slice(5);
  return DAY_FMT.format(d);
}

function formatKpiValue(k: DashboardKpi): string {
  if (k.unit === "percent") {
    return `${k.value.toFixed(1)}%`;
  }
  return String(Math.round(k.value));
}

function formatDelta(k: DashboardKpi): string {
  const sign = k.delta > 0 ? "+" : "";
  if (k.unit === "percent") {
    return `${sign}${k.delta.toFixed(1)} п.п.`;
  }
  return `${sign}${Math.round(k.delta)}`;
}

import { ArrowDown, ArrowUp, Minus } from "lucide-react";

function DeltaIcon({ dir }: { dir: DashboardKpi["delta_direction"] }) {
  if (dir === "up") {
    return <ArrowUp className="size-3.5 text-emerald-400" aria-hidden />;
  }
  if (dir === "down") {
    return <ArrowDown className="size-3.5 text-rose-400" aria-hidden />;
  }
  return <Minus className="size-3.5 text-muted-foreground" aria-hidden />;
}

function cellBg(c: MatrixCell): string {
  if (!c.status) return "bg-muted/50";
  if (c.status === "approved") return "bg-emerald-500/25";
  if (c.status === "reviewed") return "bg-amber-500/25";
  return "bg-sky-500/20";
}

function cellTooltip(c: MatrixCell): string {
  if (!c.status) return "Нет сдачи";
  const st = STATUS_LABEL[c.status];
  const at = c.submitted_at ? formatDateTime(c.submitted_at) : "";
  return at ? `${st} · ${at}` : st;
}

function MaterialsList({ items }: { items: SubmissionFeedItem["materials"] }) {
  if (!items.length) {
    return <p className="text-muted-foreground">Материалы не приложены.</p>;
  }
  return (
    <ul className="space-y-2">
      {items.map((m) => (
        <li key={m.id} className="rounded-md border border-border p-2 text-xs">
          <div className="font-medium">{m.title}</div>
          <div className="text-muted-foreground">{m.type}</div>
          {m.type === "link" && m.url ? (
            <a
              href={m.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-flex items-center gap-1 text-primary underline-offset-2 hover:underline"
            >
              Открыть <ChevronRight className="size-3" />
            </a>
          ) : null}
          {m.type === "text" && m.content ? (
            <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded bg-muted/50 p-2">
              {m.content}
            </pre>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function ErrorAlert({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <Alert variant="destructive">
      <AlertDescription>{message}</AlertDescription>
      <AlertAction>
        <Button type="button" size="sm" variant="outline" onClick={onRetry}>
          <RefreshCw data-icon="inline-start" />
          Повторить
        </Button>
      </AlertAction>
    </Alert>
  );
}

export function TeacherDashboardClient() {
  const [session, setSession] = useState<WebClientSession | null>(() =>
    getSession(),
  );

  useEffect(() => {
    queueMicrotask(() => {
      setSession(getSession());
    });
  }, []);

  const [dash, setDash] = useState<TeacherDashboardResponse | null>(null);
  const [dashLoading, setDashLoading] = useState(true);
  const [dashError, setDashError] = useState<string | null>(null);

  const [matrix, setMatrix] = useState<ProgressMatrixResponse | null>(null);
  const [matrixLoading, setMatrixLoading] = useState(true);
  const [matrixError, setMatrixError] = useState<string | null>(null);

  const [qItems, setQItems] = useState<QuestionFeedItem[]>([]);
  const [qCursor, setQCursor] = useState<string | null>(null);
  const [qLoading, setQLoading] = useState(true);
  const [qLoadingMore, setQLoadingMore] = useState(false);
  const [qError, setQError] = useState<string | null>(null);

  const [sItems, setSItems] = useState<SubmissionFeedItem[]>([]);
  const [sCursor, setSCursor] = useState<string | null>(null);
  const [sLoading, setSLoading] = useState(true);
  const [sLoadingMore, setSLoadingMore] = useState(false);
  const [sError, setSError] = useState<string | null>(null);

  const [selectedSubmission, setSelectedSubmission] =
    useState<SubmissionFeedItem | null>(null);

  const flowId = session?.flow_id ?? "";
  const isTeacher = session?.role === "teacher";

  const loadDashboard = useCallback(async () => {
    if (!flowId || !isTeacher) return;
    setDashLoading(true);
    setDashError(null);
    try {
      setDash(await fetchTeacherDashboard(flowId));
    } catch (e) {
      setDashError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setDashLoading(false);
    }
  }, [flowId, isTeacher]);

  const loadMatrix = useCallback(async () => {
    if (!flowId || !isTeacher) return;
    setMatrixLoading(true);
    setMatrixError(null);
    try {
      setMatrix(await fetchProgressMatrix(flowId));
    } catch (e) {
      setMatrixError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setMatrixLoading(false);
    }
  }, [flowId, isTeacher]);

  const loadQuestions = useCallback(
    async (cursor: string | null, append: boolean) => {
      if (!flowId || !isTeacher) return;
      if (append) setQLoadingMore(true);
      else setQLoading(true);
      setQError(null);
      try {
        const page = await fetchQuestionFeed(flowId, {
          limit: FEED_PAGE,
          cursor,
        });
        setQItems((prev) => (append ? [...prev, ...page.items] : page.items));
        setQCursor(page.next_cursor);
      } catch (e) {
        setQError(e instanceof Error ? e.message : "Ошибка загрузки");
      } finally {
        setQLoading(false);
        setQLoadingMore(false);
      }
    },
    [flowId, isTeacher],
  );

  const loadSubmissions = useCallback(
    async (cursor: string | null, append: boolean) => {
      if (!flowId || !isTeacher) return;
      if (append) setSLoadingMore(true);
      else setSLoading(true);
      setSError(null);
      try {
        const page = await fetchSubmissionFeed(flowId, {
          limit: FEED_PAGE,
          cursor,
        });
        setSItems((prev) => (append ? [...prev, ...page.items] : page.items));
        setSCursor(page.next_cursor);
      } catch (e) {
        setSError(e instanceof Error ? e.message : "Ошибка загрузки");
      } finally {
        setSLoading(false);
        setSLoadingMore(false);
      }
    },
    [flowId, isTeacher],
  );

  useEffect(() => {
    if (!flowId || !isTeacher) return;
    queueMicrotask(() => {
      void loadDashboard();
    });
  }, [flowId, isTeacher, loadDashboard]);

  useEffect(() => {
    if (!flowId || !isTeacher) return;
    queueMicrotask(() => {
      void loadMatrix();
    });
  }, [flowId, isTeacher, loadMatrix]);

  useEffect(() => {
    if (!flowId || !isTeacher) return;
    queueMicrotask(() => {
      void loadQuestions(null, false);
    });
  }, [flowId, isTeacher, loadQuestions]);

  useEffect(() => {
    if (!flowId || !isTeacher) return;
    queueMicrotask(() => {
      void loadSubmissions(null, false);
    });
  }, [flowId, isTeacher, loadSubmissions]);

  const chartData = useMemo<ActivityChartPoint[]>(() => {
    if (!dash?.activity.length) return [];
    return dash.activity.map((a) => ({
      day: formatDayLabel(a.date),
      count: a.count,
    }));
  }, [dash]);

  if (!session) {
    return (
      <div className="flex flex-col gap-2 text-muted-foreground">
        <Skeleton className="h-8 w-64" />
      </div>
    );
  }

  if (!isTeacher) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-xl font-semibold tracking-tight">
          Панель преподавателя
        </h1>
        <Card>
          <CardHeader>
            <CardTitle>Недостаточно прав</CardTitle>
            <CardDescription>
              Сводка потока, вопросы и матрица доступны только участникам с ролью
              преподавателя в этом потоке.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Link
              href="/leaderboard"
              className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
            >
              Лидерборд
            </Link>
            <Link
              href="/chat"
              className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
            >
              Чат
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">
          Панель преподавателя
        </h1>
        {dash?.period ? (
          <p className="mt-1 text-sm text-muted-foreground">
            Период: {formatDate(dash.period.start_date)} —{" "}
            {formatDate(dash.period.end_date)}
            {dash.period.label ? ` · ${dash.period.label}` : ""}
          </p>
        ) : (
          <p className="mt-1 text-sm text-muted-foreground">
            KPI и активность за последние 14 дней
          </p>
        )}
      </div>

      {/* KPI + chart */}
      <section className="flex flex-col gap-4">
        {dashError ? (
          <ErrorAlert message={dashError} onRetry={loadDashboard} />
        ) : null}
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {dashLoading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} size="sm">
                  <CardHeader className="pb-0">
                    <Skeleton className="h-4 w-32" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-8 w-20" />
                  </CardContent>
                </Card>
              ))
            : dash?.kpis.map((k) => (
                <Card key={k.id} size="sm">
                  <CardHeader className="pb-0">
                    <CardDescription>{KPI_TITLE[k.id]}</CardDescription>
                    <CardTitle className="text-2xl tabular-nums">
                      {formatKpiValue(k)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex items-center gap-2 text-xs text-muted-foreground">
                    <DeltaIcon dir={k.delta_direction} />
                    <span>к прошлому периоду: {formatDelta(k)}</span>
                  </CardContent>
                </Card>
              ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Активность</CardTitle>
            <CardDescription>
              Сообщения студентов ассистенту по дням (текущее окно)
            </CardDescription>
          </CardHeader>
          <CardContent className="h-64 w-full min-w-0 pl-0">
            {dashLoading ? (
              <Skeleton className="h-full w-full" />
            ) : chartData.length ? (
              <ActivityLineChart data={chartData} />
            ) : (
              <p className="text-sm text-muted-foreground">
                Нет данных для графика.
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Questions */}
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Вопросы к ассистенту</h2>
        {qError ? (
          <ErrorAlert
            message={qError}
            onRetry={() => void loadQuestions(null, false)}
          />
        ) : null}
        <div className="overflow-x-auto rounded-xl ring-1 ring-foreground/10">
          <table className="w-full min-w-[640px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/40 text-left text-xs text-muted-foreground">
                <th className="px-3 py-2 font-medium">Студент</th>
                <th className="px-3 py-2 font-medium">Когда</th>
                <th className="px-3 py-2 font-medium">Вопрос</th>
                <th className="px-3 py-2 font-medium">Резюме ответа</th>
              </tr>
            </thead>
            <tbody>
              {qLoading ? (
                <tr>
                  <td colSpan={4} className="px-3 py-8">
                    <Skeleton className="h-24 w-full" />
                  </td>
                </tr>
              ) : qItems.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Пока нет вопросов в этом потоке.
                  </td>
                </tr>
              ) : (
                qItems.map((row, idx) => (
                  <tr
                    key={`${row.participant_id}-${row.asked_at}-${idx}`}
                    className="border-b border-border/80 last:border-0"
                  >
                    <td className="px-3 py-2 align-top font-medium">
                      {row.participant_name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 align-top text-muted-foreground">
                      {formatDateTime(row.asked_at)}
                    </td>
                    <td className="max-w-md px-3 py-2 align-top text-muted-foreground">
                      <span className="line-clamp-3">{row.question_text}</span>
                    </td>
                    <td className="max-w-xs px-3 py-2 align-top text-muted-foreground">
                      {row.answer_summary ?? "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {qCursor ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={qLoadingMore}
            onClick={() => void loadQuestions(qCursor, true)}
          >
            {qLoadingMore ? "Загрузка…" : "Загрузить ещё"}
          </Button>
        ) : null}
      </section>

      {/* Submissions */}
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Сдачи</h2>
        {sError ? (
          <ErrorAlert
            message={sError}
            onRetry={() => void loadSubmissions(null, false)}
          />
        ) : null}
        <div className="overflow-x-auto rounded-xl ring-1 ring-foreground/10">
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/40 text-left text-xs text-muted-foreground">
                <th className="px-3 py-2 font-medium">Студент</th>
                <th className="px-3 py-2 font-medium">Урок</th>
                <th className="px-3 py-2 font-medium">Задание</th>
                <th className="px-3 py-2 font-medium">Статус</th>
                <th className="px-3 py-2 font-medium">Сдано</th>
              </tr>
            </thead>
            <tbody>
              {sLoading ? (
                <tr>
                  <td colSpan={5} className="px-3 py-8">
                    <Skeleton className="h-24 w-full" />
                  </td>
                </tr>
              ) : sItems.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Нет сдач по потоку.
                  </td>
                </tr>
              ) : (
                sItems.map((row) => (
                  <tr
                    key={row.submission_id}
                    className="cursor-pointer border-b border-border/80 last:border-0 hover:bg-muted/40"
                    onClick={() => setSelectedSubmission(row)}
                  >
                    <td className="px-3 py-2 font-medium">
                      {row.participant_name}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {row.lesson_title}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {row.assignment_title}
                    </td>
                    <td className="px-3 py-2">
                      <Badge variant="outline">
                        {STATUS_LABEL[row.status]}
                      </Badge>
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 text-muted-foreground">
                      {formatDateTime(row.submitted_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {sCursor ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={sLoadingMore}
            onClick={() => void loadSubmissions(sCursor, true)}
          >
            {sLoadingMore ? "Загрузка…" : "Загрузить ещё"}
          </Button>
        ) : null}
      </section>

      <Sheet
        open={selectedSubmission != null}
        onOpenChange={(open) => {
          if (!open) setSelectedSubmission(null);
        }}
      >
        <SheetContent side="right" className="sm:max-w-md">
          {selectedSubmission ? (
            <>
              <SheetHeader>
                <SheetTitle>Сдача</SheetTitle>
                <SheetDescription>
                  {selectedSubmission.participant_name} ·{" "}
                  {selectedSubmission.assignment_title}
                </SheetDescription>
              </SheetHeader>
              <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 pb-6 text-sm">
                <div>
                  <div className="text-xs text-muted-foreground">Урок</div>
                  <div>{selectedSubmission.lesson_title}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Статус</div>
                  <div>{STATUS_LABEL[selectedSubmission.status]}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Сдано</div>
                  <div>{formatDateTime(selectedSubmission.submitted_at)}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">
                    Комментарий
                  </div>
                  <div className="mt-1 whitespace-pre-wrap rounded-md bg-muted/50 p-2">
                    {selectedSubmission.comment ?? "—"}
                  </div>
                </div>
                <div>
                  <div className="mb-2 text-xs font-medium text-muted-foreground">
                    Материалы
                  </div>
                  <MaterialsList items={selectedSubmission.materials} />
                </div>
              </div>
            </>
          ) : null}
        </SheetContent>
      </Sheet>

      {/* Matrix */}
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Матрица прогресса</h2>
        {matrixError ? (
          <ErrorAlert message={matrixError} onRetry={loadMatrix} />
        ) : null}
        {matrixLoading ? (
          <Skeleton className="h-48 w-full" />
        ) : matrix && matrix.lessons.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            В потоке нет уроков с заданиями.
          </p>
        ) : matrix && matrix.rows.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Нет студентов в потоке.
          </p>
        ) : matrix ? (
          <div className="overflow-x-auto rounded-xl ring-1 ring-foreground/10">
            <table className="border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  <th className="sticky left-0 z-20 min-w-[140px] bg-card px-2 py-2 text-left text-xs font-medium text-muted-foreground shadow-[2px_0_4px_-2px_rgba(0,0,0,0.15)]">
                    Студент
                  </th>
                  {matrix.lessons.map((le) => (
                    <th
                      key={le.id}
                      className="min-w-[72px] max-w-[100px] px-1 py-2 text-center text-[10px] font-normal leading-tight text-muted-foreground"
                      title={`${le.module_title} · ${le.title}`}
                    >
                      <div className="line-clamp-2">{le.module_title}</div>
                      <div className="mt-0.5 line-clamp-2 font-medium text-foreground">
                        {le.title}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.rows.map((r) => (
                  <tr
                    key={r.participant_id}
                    className="border-b border-border/80 last:border-0"
                  >
                    <td className="sticky left-0 z-10 bg-card px-2 py-1.5 text-xs font-medium shadow-[2px_0_4px_-2px_rgba(0,0,0,0.12)]">
                      {r.display_name}
                    </td>
                    {r.cells.map((c, i) => (
                      <td key={i} className="p-0.5">
                        <div
                          className={cn(
                            "mx-auto h-7 w-full max-w-[2.5rem] rounded-sm ring-1 ring-inset ring-border/60",
                            cellBg(c),
                          )}
                          title={cellTooltip(c)}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}
