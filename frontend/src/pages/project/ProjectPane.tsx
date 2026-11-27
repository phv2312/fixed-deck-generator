import { InterviewPane } from "@/features/interview";
import type { ChatTurn } from "@/features/chat";
import type { Project } from "@/features/projects";
import { DeckPane } from "@/pages/project/DeckPane";
import { PAGE_TEXTS } from "@/pages/texts";

const INTERVIEW_PHASES: ReadonlySet<Project["phase"]> = new Set(["draft", "interviewing", "review"]);

interface ProjectPaneProps {
  project: Project;
  turn: ChatTurn;
  onAskAi: () => void;
}

/** The right pane: the interview before the plan is approved, the deck state after it. */
export function ProjectPane({ project, turn, onAskAi }: ProjectPaneProps): React.JSX.Element {
  if (INTERVIEW_PHASES.has(project.phase)) {
    return (
      <InterviewPane
        projectId={project.id}
        busy={turn.busy}
        onSend={(message) => void turn.send(message)}
        onApproved={() => void turn.send(PAGE_TEXTS.buildDeckMessage)}
      />
    );
  }
  return <DeckPane projectId={project.id} phase={project.phase} progress={turn.live?.progress ?? null} locked={turn.busy} onAskAi={onAskAi} />;
}
