import type { Metadata } from "next";

import { LeaderboardClient } from "@/components/leaderboard-client";

export const metadata: Metadata = {
  title: "Лидерборд | LMStart",
};

export default function LeaderboardPage() {
  return <LeaderboardClient />;
}
