import { EmptyState, ErrorState, LoadingState } from "@/shared/ui";
import { PlanReview } from "@/features/interview/components/PlanReview";
import { QuestionPrompt } from "@/features/interview/components/QuestionPrompt";
import { useApprovePlan, usePlan } from "@/features/interview/queries";
import { INTERVIEW_TEXTS } from "@/features/interview/texts";

interface InterviewPaneProps {
  projectId: string;
  /** True while the assistant works. Answers wait until it is done. */
  busy: boolean;
  /** Send a message to the chat. The interview never talks to the chat feature itself. */
  onSend: (message: string) => void;
  onApproved: () => void;
}

/** The right pane before the deck exists: one question, the plan to review, or a first hint. */
export function InterviewPane({ projectId, busy, onSend, onApproved }: InterviewPaneProps): React.JSX.Element {
  const plan = usePlan(projectId);
  const approve = useApprovePlan(projectId);

  if (plan.isPending) return <LoadingState />;
  if (plan.isError) return <ErrorState error={plan.error} onRetry={() => void plan.refetch()} />;
  const { data } = plan;
  if (data.pending_question) {
    return <QuestionPrompt key={data.pending_question.question} question={data.pending_question} disabled={busy} onAnswer={onSend} />;
  }
  if (data.slides.length === 0) {
    return <EmptyState title={INTERVIEW_TEXTS.start.title} hint={INTERVIEW_TEXTS.start.hint} />;
  }
  return (
    <PlanReview
      plan={data}
      disabled={busy}
      approving={approve.isPending}
      approveError={approve.error}
      onApprove={() => approve.mutate(undefined, { onSuccess: onApproved })}
      onRequestChanges={onSend}
    />
  );
}
