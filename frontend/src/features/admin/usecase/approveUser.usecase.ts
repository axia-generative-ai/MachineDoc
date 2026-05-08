import type { AdminUserRepository } from '../domain/adminUser.repository';

export function approveUserUseCase(repository: AdminUserRepository, userId: string) {
  return repository.approveUser(userId);
}
