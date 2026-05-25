import { NextResponse } from "next/server";
import { getSupabaseServerClient } from "@/lib/supabase";
import type { BerkeleyCourse } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const supabase = getSupabaseServerClient();
    const { data, error } = await supabase
      .from("receiving_requirements")
      .select("id, display_key, title, requirement_type")
      .eq("receiving_institution_id", 79)
      .order("display_key", { ascending: true });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const courses: BerkeleyCourse[] = (data ?? [])
      .filter((row) => row.display_key)
      .map((row) => ({
        id: row.id,
        displayKey: row.display_key,
        title: row.title,
        type: row.requirement_type,
      }));

    return NextResponse.json({ courses });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 },
    );
  }
}
