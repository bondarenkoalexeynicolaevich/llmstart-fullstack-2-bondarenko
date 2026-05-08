import { apiFetch } from "@/lib/api/client";
import type {
  LeaderboardResponse,
  ProgressMatrixResponse,
  QuestionFeedPage,
  SubmissionFeedPage,
  TeacherDashboardResponse,
} from "@/lib/api/types";

function q(flowId: string) {
  return encodeURIComponent(flowId);
}

export function fetchTeacherDashboard(flowId: string) {
  return apiFetch<TeacherDashboardResponse>(
    `/v1/flows/${q(flowId)}/dashboard`,
  );
}

export function fetchQuestionFeed(
  flowId: string,
  opts: { limit?: number; cursor?: string | null } = {},
) {
  const sp = new URLSearchParams();
  if (opts.limit != null) sp.set("limit", String(opts.limit));
  if (opts.cursor) sp.set("cursor", opts.cursor);
  const qs = sp.toString();
  return apiFetch<QuestionFeedPage>(
    `/v1/flows/${q(flowId)}/questions${qs ? `?${qs}` : ""}`,
  );
}

export function fetchSubmissionFeed(
  flowId: string,
  opts: { limit?: number; cursor?: string | null } = {},
) {
  const sp = new URLSearchParams();
  if (opts.limit != null) sp.set("limit", String(opts.limit));
  if (opts.cursor) sp.set("cursor", opts.cursor);
  const qs = sp.toString();
  return apiFetch<SubmissionFeedPage>(
    `/v1/flows/${q(flowId)}/submissions${qs ? `?${qs}` : ""}`,
  );
}

export function fetchProgressMatrix(flowId: string) {
  return apiFetch<ProgressMatrixResponse>(
    `/v1/flows/${q(flowId)}/progress-matrix`,
  );
}

export function fetchFlowLeaderboard(flowId: string) {
  return apiFetch<LeaderboardResponse>(`/v1/flows/${q(flowId)}/leaderboard`);
}
