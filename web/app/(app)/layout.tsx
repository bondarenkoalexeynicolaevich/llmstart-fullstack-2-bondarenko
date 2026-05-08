import { AppShell } from "@/components/app-shell";
import { ChatWidgetShell } from "@/components/chat-widget-shell";
import { SessionGate } from "@/components/session-gate";
import { ChatProvider } from "@/lib/chat-context";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionGate>
      <ChatProvider>
        <AppShell>{children}</AppShell>
        <ChatWidgetShell />
      </ChatProvider>
    </SessionGate>
  );
}
