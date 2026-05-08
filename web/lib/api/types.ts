/** Типы ответов teacher-flow API (см. OpenAPI). */

export type DashboardPeriod = {
  start_date: string;
  end_date: string;
  label: string;
};

export type DashboardKpiId =
  | "active_students"
  | "submissions_count"
  | "questions_count"
  | "completion_rate";

export type DashboardKpi = {
  id: DashboardKpiId;
  value: number;
  delta: number;
  delta_direction: "up" | "down" | "unchanged";
  unit: "count" | "percent";
};

export type ActivityDay = {
  date: string;
  count: number;
};

export type TeacherDashboardResponse = {
  period: DashboardPeriod;
  kpis: DashboardKpi[];
  activity: ActivityDay[];
};

export type CursorPageMeta = {
  next_cursor: string | null;
};

export type QuestionFeedItem = {
  participant_id: string;
  participant_name: string;
  asked_at: string;
  question_text: string;
  answer_summary: string | null;
};

export type QuestionFeedPage = CursorPageMeta & {
  items: QuestionFeedItem[];
};

export type MaterialRef = {
  id: string;
  title: string;
  type: "link" | "file" | "text";
  url: string | null;
  content: string | null;
};

export type SubmissionFeedItem = {
  submission_id: string;
  participant_id: string;
  participant_name: string;
  lesson_id: string;
  lesson_title: string;
  assignment_id: string;
  assignment_title: string;
  status: "submitted" | "reviewed" | "approved";
  submitted_at: string;
  comment: string | null;
  materials: MaterialRef[];
};

export type SubmissionFeedPage = CursorPageMeta & {
  items: SubmissionFeedItem[];
};

export type MatrixLessonColumn = {
  id: string;
  title: string;
  module_title: string;
  module_order: number;
  lesson_order: number;
};

export type MatrixCell = {
  status: "submitted" | "reviewed" | "approved" | null;
  submitted_at: string | null;
};

export type MatrixParticipantRow = {
  participant_id: string;
  display_name: string;
  cells: MatrixCell[];
};

export type ProgressMatrixResponse = {
  lessons: MatrixLessonColumn[];
  rows: MatrixParticipantRow[];
};

/** Лидерборд (OpenAPI LeaderboardResponse). */

export type ScatterMeta = {
  axis_x_label: string;
  axis_y_label: string;
};

export type LessonStatusIcon = {
  lesson_id: string;
  state: "done" | "partial" | "none";
};

export type LeaderboardMedal = "gold" | "silver" | "bronze";

export type LeaderboardRow = {
  rank: number;
  participant_id: string;
  display_name: string;
  overall_progress: number;
  lesson_statuses: LessonStatusIcon[];
  medal: LeaderboardMedal | null;
};

export type ScatterPoint = {
  participant_id: string;
  display_name: string;
  x: number;
  y: number;
  rank: number;
};

export type LeaderboardResponse = {
  scatter_meta: ScatterMeta;
  table: LeaderboardRow[];
  scatter: ScatterPoint[];
};

/** Диалог участника (веб), см. OpenAPI DialogMessageReadOut / DialogMessageListPageOut. */

export type DialogMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
};

export type DialogMessageListPage = CursorPageMeta & {
  items: DialogMessage[];
};

export type DialogMessageCreateResponse = {
  reply_text: string;
  user_message_id: string;
  assistant_message_id: string;
  transcription?: string | null;
};
