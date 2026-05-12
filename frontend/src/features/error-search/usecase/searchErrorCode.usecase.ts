import type { ErrorSearchRepository } from '../domain/errorSearch.repository';
import type { ErrorSearchCommand } from '../model/errorSearch.types';

export class ErrorSearchPolicyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ErrorSearchPolicyError';
  }
}

export function searchErrorCodeUseCase(repository: ErrorSearchRepository, command: ErrorSearchCommand) {
  // 대소문자는 BE에서 case-insensitive로 비교한다 (벤더 코드가 mixed case: oH, COM.E 등).
  // 원본 그대로 보내야 알림 카드의 `oC` 같은 코드 검색이 깨지지 않음.
  const errorCode = command.errorCode.trim();

  if (!errorCode) {
    throw new ErrorSearchPolicyError('검색어를 입력해주세요.');
  }

  return repository.searchByCode({ errorCode });
}
