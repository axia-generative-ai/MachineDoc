import type { AuthRepository } from '../domain/auth.repository';
import type { SignupCommand } from '../model/auth.types';

export function signupUseCase(repository: AuthRepository, command: SignupCommand) {
  return repository.signup(command);
}
