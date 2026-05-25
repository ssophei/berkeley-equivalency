export type BerkeleyCourse = {
  id: string;
  displayKey: string;
  title: string | null;
  type: "Course" | "Series" | string;
};

export type CourseNode = {
  type: "Course";
  id?: number;
  prefix?: string;
  course_number?: string | number;
  course_key?: string;
  title?: string;
  department?: string;
  min_units?: number;
  max_units?: number;
  attributes?: NoteNode[];
  requisites?: NoteNode[];
};

export type CourseGroupNode = {
  type: "CourseGroup";
  course_conjunction?: "And" | "Or" | string;
  items?: ArticulationNode[];
  attributes?: NoteNode[];
};

export type SpecialNode = {
  type: "NotArticulated" | "MustBeTakenAtReceivingUniversity" | string;
  reason?: string;
  attributes?: NoteNode[];
};

export type NoteNode =
  | string
  | {
      content?: string;
      text?: string;
      label?: string;
      [key: string]: unknown;
    };

export type ArticulationNode = CourseNode | CourseGroupNode | SpecialNode;

export type SendingArticulation = {
  type: "SendingArticulation" | "NotArticulated" | string;
  items?: ArticulationNode[];
  group_conjunctions?: {
    conjunction?: "And" | "Or" | string;
    begin_position?: number;
    end_position?: number;
  }[];
  reason?: string;
  attributes?: NoteNode[];
};

export type ArticulationResult = {
  academicYear: {
    id: number;
    code: string;
  };
  groupName: string | null;
  sourceFile: string;
  sendingInstitution: {
    id: number;
    name: string;
  };
  berkeleyCourse: string;
  berkeleyTitle: string | null;
  receiving: unknown;
  sending: SendingArticulation;
};
