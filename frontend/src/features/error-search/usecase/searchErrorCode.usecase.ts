import type { ErrorSearchRepository } from '../domain/errorSearch.repository';
import type { ErrorSearchCommand } from '../model/errorSearch.types';

export class ErrorSearchPolicyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ErrorSearchPolicyError';
  }
}

export function searchErrorCodeUseCase(repository: ErrorSearchRepository, command: ErrorSearchCommand) {
  const errorCode = command.errorCode.trim().toUpperCase();

  if (!errorCode) {
    throw new ErrorSearchPolicyError('검색어를 입력해주세요.');
  }

  return repository.searchByCode({ errorCode });
}
