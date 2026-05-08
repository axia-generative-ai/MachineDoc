import type { AuthRepository } from '../domain/auth.repository';
import { validateLoginCommand } from '../domain/authPolicy';
import type { LoginCommand } from '../model/auth.types';

export function loginUseCase(repository: AuthRepository, command: LoginCommand) {
  validateLoginCommand(command);
  return repository.login(command);
}
