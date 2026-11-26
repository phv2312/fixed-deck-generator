import { EditorBar } from "@/features/deck-editor/components/EditorBar";
import { SlideList } from "@/features/deck-editor/components/SlideList";
import { SlideStage } from "@/features/deck-editor/components/SlideStage";
import { useDeckEditor } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import { EmptyState, ErrorState, LoadingState } from "@/shared/ui";

/** Edit the built deck: slide list, the slide with its element boxes, and a floating toolbar. */
interface DeckEditorProps {
  projectId: string;
  /** True while the assistant works on the deck. The editor shows it and takes no edit. */
  locked: boolean;
}

export function DeckEditor({ projectId, locked }: DeckEditorProps): React.JSX.Element {
  const editor = useDeckEditor(projectId, locked);
  const { deck, slide, query } = editor;
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => void query.refetch()} />;
  if (!deck || !slide) return <EmptyState title={EDITOR_TEXTS.empty.title} hint={EDITOR_TEXTS.empty.body} />;
  return (
    <div className="flex flex-col gap-4 md:flex-row">
      <SlideList projectId={projectId} deck={deck} current={editor.slideIndex} onPick={editor.selectSlide} />
      <div className="flex min-w-0 flex-1 flex-col gap-4">
        <EditorBar editor={editor} />
        <div className="lg:pt-12">
          <SlideStage projectId={projectId} deck={deck} slide={slide} editor={editor} />
        </div>
      </div>
    </div>
  );
}
