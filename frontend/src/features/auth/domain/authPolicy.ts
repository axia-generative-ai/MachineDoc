import type { LoginCommand, SignupCommand } from '../model/auth.types';

export class AuthPolicyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthPolicyError';
  }
}

export function validateLoginCommand(command: LoginCommand) {
  if (!command.email.trim() || !command.password.trim()) {
    throw new AuthPolicyError('이메일과 비밀번호를 입력해주세요.');
  }
}

export function validateSignupCommand(command: SignupCommand) {
  if (!command.name.trim()) {
    throw new AuthPolicyError('이름을 입력해주세요.');
  }

  if (!command.email.trim()) {
    throw new AuthPolicyError('이메일을 입력해주세요.');
  }

  if (!command.password.trim()) {
    throw new AuthPolicyError('비밀번호를 입력해주세요.');
  }

  if (command.password.length < 8) {
    throw new AuthPolicyError('비밀번호는 8자 이상 입력해주세요.');
  }

  if (!command.department.trim()) {
    throw new AuthPolicyError('소속을 선택해주세요.');
  }

  if (!['WORKER', 'ENGINEER'].includes(command.role)) {
    throw new AuthPolicyError('관리자는 웹에서 가입할 수 없습니다.');
  }
}
