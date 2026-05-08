"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { LayoutDashboard, LogOut, MessageSquare, Trophy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { clearSession, getSession } from "@/lib/session";
import type { WebClientSession } from "@/lib/types";

const nav = [
  { href: "/dashboard", label: "Панель", icon: LayoutDashboard },
  { href: "/leaderboard", label: "Лидерборд", icon: Trophy },
  { href: "/chat", label: "Чат", icon: MessageSquare },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session] = useState<WebClientSession | null>(() => getSession());

  function logout() {
    clearSession();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen flex-1">
      <aside className="flex w-56 flex-col border-r border-border bg-sidebar text-sidebar-foreground">
        <div className="border-b border-sidebar-border px-4 py-4 text-sm font-semibold">
          Поток
        </div>
        <nav className="flex flex-col gap-1 p-2">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
                )}
              >
                <Icon className="size-4 shrink-0" aria-hidden />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col bg-background">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-3">
          <div className="min-w-0 text-sm">
            {session ? (
              <>
                <span className="font-medium text-foreground">
                  {session.display_name}
                </span>
                <span className="text-muted-foreground">
                  {" "}
                  · {session.role === "teacher" ? "преподаватель" : "студент"}
                </span>
                <div className="truncate text-xs text-muted-foreground">
                  flow: {session.flow_id}
                </div>
              </>
            ) : (
              <span className="text-muted-foreground">…</span>
            )}
          </div>
          <Button type="button" variant="outline" size="sm" onClick={logout}>
            <LogOut data-icon="inline-start" />
            Выход
          </Button>
        </header>
        <main className="flex min-h-0 flex-1 flex-col p-6">{children}</main>
      </div>
    </div>
  );
}
