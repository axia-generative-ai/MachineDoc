export type ErrorSearchCommand = {
  errorCode: string;
};

export type ManualCitation = {
  filename: string;
  page: number;
  manualId: number | null;
};

export type ErrorSearchResult = {
  keyword: string;
  status: string;
  analysis: string;
  solution: string;
  historyId: number | null;
  citations: ManualCitation[];
  raw: Record<string, unknown>;
};
