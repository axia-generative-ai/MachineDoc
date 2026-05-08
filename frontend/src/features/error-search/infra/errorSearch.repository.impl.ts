import type { ErrorSearchRepository } from '../domain/errorSearch.repository';
import { errorSearchApi } from './errorSearch.api';

export const errorSearchRepositoryImpl: ErrorSearchRepository = {
  searchByCode: errorSearchApi.searchByCode,
};
