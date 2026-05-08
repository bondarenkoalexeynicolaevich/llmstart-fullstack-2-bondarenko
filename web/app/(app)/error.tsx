"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-6">
      <h2 className="text-lg font-semibold">Что-то пошло не так</h2>
      <p className="text-sm text-muted-foreground">
        {error.message || "Произошла непредвиденная ошибка."}
      </p>
      <Button type="button" variant="outline" onClick={reset}>
        Попробовать снова
      </Button>
    </div>
  );
}
