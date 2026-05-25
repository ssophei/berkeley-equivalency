"use client";

import { Check, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { BerkeleyCourse } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

type CourseComboboxProps = {
  courses: BerkeleyCourse[];
  selectedId: string;
  onSelect: (courseId: string) => void;
};

export function CourseCombobox({
  courses,
  selectedId,
  onSelect,
}: CourseComboboxProps) {
  const [query, setQuery] = useState("");
  const selected = courses.find((course) => course.id === selectedId);
  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return courses.slice(0, 40);
    }

    return courses
      .filter((course) =>
        `${course.displayKey} ${course.title ?? ""}`
          .toLowerCase()
          .includes(normalizedQuery),
      )
      .slice(0, 40);
  }, [courses, query]);

  return (
    <div className="space-y-2">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={selected ? selected.displayKey : "Search Berkeley courses"}
        />
      </div>
      <div className="max-h-72 overflow-auto rounded-md border bg-card">
        {filtered.map((course) => (
          <button
            key={course.id}
            type="button"
            onClick={() => {
              onSelect(course.id);
              setQuery("");
            }}
            className={cn(
              "grid w-full grid-cols-[1fr_auto] gap-3 border-b px-3 py-2 text-left text-sm last:border-b-0 hover:bg-secondary",
              course.id === selectedId && "bg-secondary",
            )}
          >
            <span className="min-w-0">
              <span className="font-semibold text-primary">{course.displayKey}</span>
              {course.title ? (
                <span className="ml-2 text-muted-foreground">{course.title}</span>
              ) : null}
            </span>
            {course.id === selectedId ? (
              <Check className="mt-0.5 h-4 w-4 text-primary" />
            ) : null}
          </button>
        ))}
        {filtered.length === 0 ? (
          <div className="px-3 py-6 text-sm text-muted-foreground">
            No Berkeley courses found.
          </div>
        ) : null}
      </div>
    </div>
  );
}
