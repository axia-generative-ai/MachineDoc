import type { AuthRepository } from '../domain/auth.repository';

export function logoutUseCase(repository: AuthRepository) {
  return repository.logout();
}
