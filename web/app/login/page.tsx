import { Suspense } from "react";

import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-1 flex-col items-center justify-center bg-background p-6">
      <Suspense
        fallback={
          <p className="text-sm text-muted-foreground">Загрузка формы…</p>
        }
      >
        <LoginForm />
      </Suspense>
    </div>
  );
}
