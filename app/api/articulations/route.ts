import { NextRequest, NextResponse } from "next/server";
import { getSupabaseServerClient } from "@/lib/supabase";
import type { ArticulationResult, SendingArticulation } from "@/lib/types";

export const dynamic = "force-dynamic";

type ArticulationRow = {
  academic_year_id: number;
  group_name: string | null;
  source_file: string;
  sending_institution_id: number;
  receiving_json: unknown;
  sending_json: SendingArticulation;
};

type RequirementRow = {
  display_key: string;
  title: string | null;
};

type InstitutionRow = {
  id: number;
  name: string;
};

type AcademicYearRow = {
  id: number;
  code: string;
};

export async function GET(request: NextRequest) {
  const courseId = request.nextUrl.searchParams.get("courseId");

  if (!courseId) {
    return NextResponse.json({ error: "Missing courseId" }, { status: 400 });
  }

  try {
    const supabase = getSupabaseServerClient();

    const [requirementResult, articulationResult] = await Promise.all([
      supabase
        .from("receiving_requirements")
        .select("display_key, title")
        .eq("id", courseId)
        .single(),
      supabase
        .from("articulations")
        .select(
          "academic_year_id, group_name, source_file, sending_institution_id, receiving_json, sending_json",
        )
        .eq("receiving_requirement_id", courseId)
        .order("sending_institution_id", { ascending: true }),
    ]);

    if (requirementResult.error) {
      return NextResponse.json(
        { error: requirementResult.error.message },
        { status: 500 },
      );
    }

    if (articulationResult.error) {
      return NextResponse.json(
        { error: articulationResult.error.message },
        { status: 500 },
      );
    }

    const requirement = requirementResult.data as RequirementRow;
    const rows = (articulationResult.data ?? []) as ArticulationRow[];
    const sendingIds = [...new Set(rows.map((row) => row.sending_institution_id))];
    const yearIds = [...new Set(rows.map((row) => row.academic_year_id))];

    const [institutionResult, yearResult] = await Promise.all([
      supabase.from("institutions").select("id, name").in("id", sendingIds),
      supabase.from("academic_years").select("id, code").in("id", yearIds),
    ]);

    if (institutionResult.error) {
      return NextResponse.json(
        { error: institutionResult.error.message },
        { status: 500 },
      );
    }

    if (yearResult.error) {
      return NextResponse.json({ error: yearResult.error.message }, { status: 500 });
    }

    const institutions = new Map(
      ((institutionResult.data ?? []) as InstitutionRow[]).map((institution) => [
        institution.id,
        institution,
      ]),
    );
    const years = new Map(
      ((yearResult.data ?? []) as AcademicYearRow[]).map((year) => [year.id, year]),
    );

    const articulations: ArticulationResult[] = rows
      .map((row) => {
        const institution = institutions.get(row.sending_institution_id);
        const year = years.get(row.academic_year_id);

        if (!institution || !year) {
          return null;
        }

        return {
          academicYear: year,
          groupName: row.group_name,
          sourceFile: row.source_file,
          sendingInstitution: institution,
          berkeleyCourse: requirement.display_key,
          berkeleyTitle: requirement.title,
          receiving: row.receiving_json,
          sending: row.sending_json,
        };
      })
      .filter((row): row is ArticulationResult => row !== null)
      .sort((a, b) =>
        a.sendingInstitution.name.localeCompare(b.sendingInstitution.name),
      );

    return NextResponse.json({ articulations });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 },
    );
  }
}
