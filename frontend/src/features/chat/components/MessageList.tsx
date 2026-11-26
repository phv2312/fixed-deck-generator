import Alert from "@mui/material/Alert";
import { useEffect, useRef } from "react";

import { AssistantMessage, LiveMessage, UserMessage } from "@/features/chat/components/Messages";
import { useChat } from "@/features/chat/queries";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ChatMessage, ToolCall, ToolField } from "@/features/chat/types";
import type { ChatTurn } from "@/features/chat/useChatTurn";
import { ApiError, errorText } from "@/shared/api";
import { EmptyState, ErrorState, LoadingState } from "@/shared/ui";

type ShowAll = (call: ToolCall, field: ToolField) => void;

interface MessageListProps {
  projectId: string;
  turn: ChatTurn;
  onShowAll: ShowAll;
}

function HistoryMessages({ messages, onShowAll }: { messages: ChatMessage[]; onShowAll: ShowAll }): React.JSX.Element[] {
  return messages.map((message) =>
    message.role === "user" ? (
      <UserMessage key={message.id} text={message.text} />
    ) : (
      <AssistantMessage key={message.id} message={message} onShowAll={onShowAll} />
    ),
  );
}

/** The user message that is on its way, until the history has it. */
function pendingText(messages: ChatMessage[], pending: string | null): string | null {
  const last = messages.at(-1);
  return last?.role === "user" && last.text === pending ? null : pending;
}

function TurnTail({ turn, pending, onShowAll }: { turn: ChatTurn; pending: string | null; onShowAll: ShowAll }): React.JSX.Element {
  return (
    <>
      {pending ? <UserMessage text={pending} /> : null}
      {turn.live ? <LiveMessage live={turn.live} onShowAll={onShowAll} /> : null}
      {turn.errorCode ? <Alert severity="error">{errorText(new ApiError(turn.errorCode, "", 0, null))}</Alert> : null}
    </>
  );
}

/** The messages of the history, then the message that is on its way, then the turn that runs. */
export function MessageList({ projectId, turn, onShowAll }: MessageListProps): React.JSX.Element {
  const history = useChat(projectId);
  const endRef = useRef<HTMLDivElement>(null);
  const messages = history.data?.messages ?? [];
  const pending = pendingText(messages, turn.pending);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages.length, turn.live?.text, turn.live?.tools.length, turn.pending]);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-4">
      {history.isPending ? <LoadingState /> : null}
      {history.isError ? <ErrorState error={history.error} onRetry={() => void history.refetch()} /> : null}
      {history.data && messages.length === 0 && !pending ? (
        <EmptyState title={CHAT_TEXTS.empty.title} hint={CHAT_TEXTS.empty.hint} />
      ) : null}
      <HistoryMessages messages={messages} onShowAll={onShowAll} />
      <TurnTail turn={turn} pending={pending} onShowAll={onShowAll} />
      <div ref={endRef} />
    </div>
  );
}
