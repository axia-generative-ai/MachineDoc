import type { AuthRepository } from '../domain/auth.repository';
import type { LoginCommand } from '../model/auth.types';

export function loginUseCase(repository: AuthRepository, command: LoginCommand) {
  return repository.login(command);
}
