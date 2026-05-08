import type { AuthRepository } from '../domain/auth.repository';
import { validateSignupCommand } from '../domain/authPolicy';
import type { SignupCommand } from '../model/auth.types';

export function signupUseCase(repository: AuthRepository, command: SignupCommand) {
  validateSignupCommand(command);
  return repository.signup(command);
}
