"use client";

import { MessageCircle } from "lucide-react";
import { useState } from "react";

import { ChatPanel } from "@/components/chat-panel";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export function ChatWidgetShell() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        type="button"
        size="icon-lg"
        className="fixed bottom-6 right-6 z-50 size-14 rounded-full shadow-lg"
        onClick={() => {
          setOpen(true);
        }}
        aria-label="Открыть чат с ассистентом"
      >
        <MessageCircle className="size-7" />
      </Button>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="right" className="flex w-full flex-col sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Ассистент</SheetTitle>
          </SheetHeader>
          <div className="mt-4 flex min-h-0 flex-1 flex-col text-sm">
            {open ? <ChatPanel /> : null}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
