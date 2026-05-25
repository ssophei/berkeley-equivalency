"use client";

import { Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ArticulationRenderer } from "@/components/articulation-renderer";
import { CourseCombobox } from "@/components/course-combobox";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { ArticulationResult, BerkeleyCourse } from "@/lib/types";

type CoursesResponse = {
  courses: BerkeleyCourse[];
  error?: string;
};

type ArticulationsResponse = {
  articulations: ArticulationResult[];
  error?: string;
};

export default function Home() {
  const [courses, setCourses] = useState<BerkeleyCourse[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [articulations, setArticulations] = useState<ArticulationResult[]>([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCourses() {
      setCoursesLoading(true);
      const response = await fetch("/api/courses");
      const payload = (await response.json()) as CoursesResponse;

      if (!response.ok) {
        setError(payload.error ?? "Failed to load Berkeley courses");
        setCoursesLoading(false);
        return;
      }

      setCourses(payload.courses);
      setSelectedCourseId(payload.courses[0]?.id ?? "");
      setCoursesLoading(false);
    }

    void loadCourses();
  }, []);

  useEffect(() => {
    if (!selectedCourseId) {
      return;
    }

    async function loadArticulations() {
      setResultsLoading(true);
      setError(null);
      const response = await fetch(
        `/api/articulations?courseId=${encodeURIComponent(selectedCourseId)}`,
      );
      const payload = (await response.json()) as ArticulationsResponse;

      if (!response.ok) {
        setError(payload.error ?? "Failed to load articulations");
        setArticulations([]);
        setResultsLoading(false);
        return;
      }

      setArticulations(payload.articulations);
      setResultsLoading(false);
    }

    void loadArticulations();
  }, [selectedCourseId]);

  const selectedCourse = courses.find((course) => course.id === selectedCourseId);
  const grouped = useMemo(() => {
    return articulations.reduce<Record<string, ArticulationResult[]>>(
      (accumulator, articulation) => {
        const key = articulation.sendingInstitution.name;
        accumulator[key] = [...(accumulator[key] ?? []), articulation];
        return accumulator;
      },
      {},
    );
  }, [articulations]);

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex max-w-6xl flex-col gap-5 px-4 py-6 md:px-6">
        <section className="grid gap-4 md:grid-cols-[22rem_1fr]">
          <div>
            <h1 className="text-xl font-semibold">Berkeley Transfer Search</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Select a Berkeley course to see matching community college articulations.
            </p>
          </div>
          <Card>
            <CardContent className="p-3">
              {coursesLoading ? (
                <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading courses
                </div>
              ) : (
                <CourseCombobox
                  courses={courses}
                  selectedId={selectedCourseId}
                  onSelect={setSelectedCourseId}
                />
              )}
            </CardContent>
          </Card>
        </section>

        {error ? (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        <section className="space-y-3">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <div className="text-sm text-muted-foreground">Selected course</div>
              <div className="text-lg font-semibold">
                {selectedCourse?.displayKey ?? "No course selected"}
                {selectedCourse?.title ? (
                  <span className="ml-2 font-normal text-muted-foreground">
                    {selectedCourse.title}
                  </span>
                ) : null}
              </div>
            </div>
            <Badge variant="secondary">
              {resultsLoading ? "Loading" : `${articulations.length} results`}
            </Badge>
          </div>

          {resultsLoading ? (
            <Card>
              <CardContent className="flex h-40 items-center justify-center text-sm text-muted-foreground">
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading articulations
              </CardContent>
            </Card>
          ) : null}

          {!resultsLoading && articulations.length === 0 && selectedCourseId ? (
            <Card>
              <CardContent className="py-10 text-center text-sm text-muted-foreground">
                No articulations found for this course.
              </CardContent>
            </Card>
          ) : null}

          {!resultsLoading
            ? Object.entries(grouped).map(([institution, rows]) => (
                <Card key={institution}>
                  <CardHeader className="flex flex-row items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold">{institution}</div>
                      <div className="text-xs text-muted-foreground">
                        {rows[0]?.academicYear.code}
                      </div>
                    </div>
                    <Badge variant="outline">
                      {rows.length} {rows.length === 1 ? "match" : "matches"}
                    </Badge>
                  </CardHeader>
                  <CardContent className="space-y-5">
                    {rows.map((row) => (
                      <div
                        key={`${row.sourceFile}-${row.groupName}`}
                        className="space-y-3 border-b pb-5 last:border-b-0 last:pb-0"
                      >
                        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                          {row.groupName ? <Badge variant="secondary">{row.groupName}</Badge> : null}
                          <span>{row.sourceFile}</span>
                        </div>
                        <ArticulationRenderer sending={row.sending} />
                      </div>
                    ))}
                  </CardContent>
                </Card>
              ))
            : null}
        </section>
      </div>
    </main>
  );
}
