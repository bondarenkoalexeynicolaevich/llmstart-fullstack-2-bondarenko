import type { Metadata } from "next";

import { TeacherDashboardClient } from "@/components/teacher-dashboard-client";

export const metadata: Metadata = {
  title: "Панель преподавателя | LMStart",
};

export default function DashboardPage() {
  return <TeacherDashboardClient />;
}
