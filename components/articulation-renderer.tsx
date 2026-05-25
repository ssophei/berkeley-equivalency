import type {
  ArticulationNode,
  CourseGroupNode,
  CourseNode,
  NoteNode,
  SendingArticulation,
} from "@/lib/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

function noteText(note: NoteNode): string {
  if (typeof note === "string") {
    return note;
  }
  return note.content ?? note.text ?? note.label ?? "";
}

function Notes({ notes }: { notes?: NoteNode[] }) {
  const visibleNotes = (notes ?? []).map(noteText).filter(Boolean);

  if (visibleNotes.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 space-y-1">
      {visibleNotes.map((note, index) => (
        <div
          key={`${note}-${index}`}
          className="border-l-2 border-slate-400 bg-slate-100 px-3 py-2 text-sm text-slate-700"
        >
          {note}
        </div>
      ))}
    </div>
  );
}

function CourseLine({ course }: { course: CourseNode }) {
  return (
    <div className="grid grid-cols-[minmax(7rem,auto)_1fr_auto] items-start gap-3">
      <div className="font-semibold text-primary">{course.course_key}</div>
      <div className="text-sm text-slate-700">{course.title}</div>
      {course.max_units || course.min_units ? (
        <Badge variant="secondary" className="tabular-nums">
          {(course.max_units ?? course.min_units)?.toFixed(2)}
        </Badge>
      ) : null}
    </div>
  );
}

function isCourseNode(node: ArticulationNode): node is CourseNode {
  return node.type === "Course";
}

function isCourseGroupNode(node: ArticulationNode): node is CourseGroupNode {
  return node.type === "CourseGroup";
}

function isSpecialNode(node: ArticulationNode): node is Exclude<ArticulationNode, CourseNode | CourseGroupNode> {
  return !isCourseNode(node) && !isCourseGroupNode(node);
}

function ConjunctionDivider({ value }: { value: string }) {
  return (
    <div className="flex items-center gap-2 py-2">
      <Badge variant={value === "Or" ? "default" : "outline"}>{value.toUpperCase()}</Badge>
      <div className="h-px flex-1 bg-border" />
    </div>
  );
}

function CourseGroup({ group, depth = 0 }: { group: CourseGroupNode; depth?: number }) {
  const items = group.items ?? [];
  const conjunction = group.course_conjunction ?? "And";

  return (
    <div
      className={cn(
        "space-y-2",
        depth > 0 && "border-l-2 border-border pl-3",
        conjunction === "Or" && "rounded-md border border-blue-200 bg-blue-50/40 p-3",
      )}
    >
      {items.map((item, index) => (
        <div key={index}>
          {index > 0 ? <ConjunctionDivider value={conjunction} /> : null}
          <ArticulationNodeView node={item} depth={depth + 1} />
        </div>
      ))}
      <Notes notes={group.attributes} />
    </div>
  );
}

function ArticulationNodeView({
  node,
  depth = 0,
}: {
  node: ArticulationNode;
  depth?: number;
}) {
  if (isCourseNode(node)) {
    return (
      <div>
        <CourseLine course={node} />
        <Notes notes={[...(node.attributes ?? []), ...(node.requisites ?? [])]} />
      </div>
    );
  }

  if (isCourseGroupNode(node)) {
    return <CourseGroup group={node} depth={depth} />;
  }

  return (
    <div className="rounded-md border border-dashed px-3 py-2 text-sm text-muted-foreground">
      {node.reason ?? node.type}
      <Notes notes={node.attributes} />
    </div>
  );
}

function topLevelConjunctionFor(
  index: number,
  sending: SendingArticulation,
): string | null {
  const match = sending.group_conjunctions?.find(
    (conjunction) =>
      conjunction.begin_position !== undefined &&
      conjunction.end_position !== undefined &&
      index > conjunction.begin_position &&
      index <= conjunction.end_position,
  );

  return match?.conjunction ?? null;
}

export function ArticulationRenderer({ sending }: { sending: SendingArticulation }) {
  if (sending.type === "NotArticulated") {
    return (
      <div className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
        {sending.reason ?? "No articulated sending course"}
      </div>
    );
  }

  const items = sending.items ?? [];

  if (items.length === 0) {
    return (
      <div className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
        No sending courses listed.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item, index) => {
        const divider = index > 0 ? topLevelConjunctionFor(index, sending) : null;
        return (
          <div key={index}>
            {divider ? <ConjunctionDivider value={divider} /> : null}
            <ArticulationNodeView node={item} />
          </div>
        );
      })}
      <Notes notes={sending.attributes} />
    </div>
  );
}
