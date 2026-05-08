import type { AdminUserRepository } from '../domain/adminUser.repository';

export function getPendingUsersUseCase(repository: AdminUserRepository) {
  return repository.getPendingUsers();
}
