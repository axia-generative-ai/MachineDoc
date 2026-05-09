export type ErrorSearchCommand = {
  errorCode: string;
};

export type ErrorSearchResult = {
  keyword: string;
  status: string;
  analysis: string;
  solution: string;
  raw: Record<string, unknown>;
};
