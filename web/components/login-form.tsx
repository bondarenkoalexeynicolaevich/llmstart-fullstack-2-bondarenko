"use client";

import type { FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { createWebSession } from "@/lib/api";
import { getPublicBackendBaseUrl } from "@/lib/env";
import { saveSession, getSession } from "@/lib/session";

const DEMO_FLOW =
  process.env.NEXT_PUBLIC_DEMO_FLOW ?? "00000000-0000-0000-0000-000000000001";
const DEMO_USER =
  process.env.NEXT_PUBLIC_DEMO_USER ?? "bondarenko_alexey_nikolaevich";

function normalizeTelegramUsername(raw: string): string {
  let s = raw.trim().replace(/^@+/, "");
  s = s.replace(/^\++/, "");
  s = s.replace(/\s+/g, "");
  return s;
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState("");
  const [flowId, setFlowId] = useState(DEMO_FLOW);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (getSession()) {
      router.replace("/dashboard");
    }
  }, [router]);

  const queryKey = searchParams.toString();

  /** Подсказка: в ссылке есть username=, но значение пустое (частая опечатка в URL). */
  const emptyUsernameInQueryHint = useMemo(() => {
    const sp = new URLSearchParams(queryKey);
    const fromUser =
      sp.get("username") ?? sp.get("telegram_username") ?? sp.get("user");
    const hasUserKey =
      sp.has("username") || sp.has("telegram_username") || sp.has("user");
    if (!hasUserKey || fromUser?.trim()) return null;
    return "В адресе после username= ничего нет — допишите юзернейм или введите его в поле ниже.";
  }, [queryKey]);

  /** Подставить username / flow_id из query (?username=&flow_id= или ?telegram_username=). */
  useEffect(() => {
    const sp = new URLSearchParams(queryKey);
    const rawUser =
      sp.get("username") ?? sp.get("telegram_username") ?? sp.get("user");
    const rawFlow = sp.get("flow_id") ?? sp.get("flow");
    queueMicrotask(() => {
      if (rawUser?.trim()) {
        setUsername(normalizeTelegramUsername(rawUser));
      }
      if (rawFlow?.trim()) {
        setFlowId(rawFlow.trim());
      }
    });
  }, [queryKey]);

  const submitCredentials = useCallback(
    async (rawUser: string, rawFlow: string) => {
      setError(null);
      setPending(true);
      try {
        const u = normalizeTelegramUsername(rawUser);
        const fid = rawFlow.trim();
        if (!u || !fid) {
          setError("Заполните поля.");
          return;
        }
        const res = await createWebSession({
          telegram_username: u,
          flow_id: fid,
        });
        saveSession(res, fid);
        router.replace("/dashboard");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось войти");
      } finally {
        setPending(false);
      }
    },
    [router],
  );

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await submitCredentials(username, flowId);
  }

  return (
    <Card className="w-full max-w-md border-border shadow-md">
      <CardHeader>
        <CardTitle>Вход</CardTitle>
        <CardDescription>
          Telegram username (без @; регистр не важен) и UUID потока. Можно передать в
          URL:{" "}
          <span className="font-mono text-[0.65rem] break-all">
            ?username={DEMO_USER}&flow_id=…
          </span>{" "}
          (без <span className="font-mono">+</span> перед ником; символ «+» в query
          даёт пробел и ломает ник.)
          . Backend:{" "}
          <span className="font-mono text-xs">{getPublicBackendBaseUrl()}</span>
        </CardDescription>
      </CardHeader>
      <form onSubmit={onSubmit}>
        <CardContent className="flex flex-col gap-4">
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="username">Telegram username</FieldLabel>
              <Input
                id="username"
                name="username"
                autoComplete="username"
                placeholder={DEMO_USER}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={pending}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="flow_id">Flow ID (UUID)</FieldLabel>
              <Input
                id="flow_id"
                name="flow_id"
                placeholder={DEMO_FLOW}
                value={flowId}
                onChange={(e) => setFlowId(e.target.value)}
                disabled={pending}
                className="font-mono text-sm"
              />
            </Field>
          </FieldGroup>
          <p className="text-xs text-muted-foreground">
            Локальный demo: пользователь{" "}
            <span className="font-mono">{DEMO_USER}</span>, поток{" "}
            <span className="font-mono">{DEMO_FLOW}</span> после{" "}
            <code className="font-mono">make db-seed</code>.
          </p>
          <p className="text-xs text-muted-foreground">
            Запрос к API в «Сеть»: тип <strong>Fetch</strong> или группа{" "}
            <strong>Все</strong> (не только документ). Имя:{" "}
            <span className="font-mono">web-session</span>, хост как у бэкенда (
            <span className="font-mono">:8000</span> по умолчанию).
          </p>
          {emptyUsernameInQueryHint ? (
            <p className="text-sm text-amber-600 dark:text-amber-500" role="status">
              {emptyUsernameInQueryHint}
            </p>
          ) : null}
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
        </CardContent>
        <CardFooter>
          <Button
            type="submit"
            className="w-full"
            disabled={pending}
          >
            {pending ? "Вход…" : "Войти"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
