"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getSession } from "@/lib/session";

/**
 * Доступ только при валидной сессии в localStorage.
 */
export function SessionGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getSession()) {
      router.replace("/login");
      return;
    }
    queueMicrotask(() => setReady(true));
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen flex-1 items-center justify-center bg-background text-muted-foreground">
        Загрузка…
      </div>
    );
  }

  return <>{children}</>;
}
