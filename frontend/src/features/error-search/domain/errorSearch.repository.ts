import type { ErrorSearchCommand, ErrorSearchResult } from '../model/errorSearch.types';

export type ErrorSearchRepository = {
  searchByCode(command: ErrorSearchCommand): Promise<ErrorSearchResult>;
};
