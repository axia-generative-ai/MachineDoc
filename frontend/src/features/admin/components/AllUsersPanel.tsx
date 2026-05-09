import { useEffect, useState } from 'react';
import { RefreshCw, Trash2, UserRound, Users } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import type { User, UserRole, UserState } from '../../../entities/user/model/user.types';
import { adminUserApi } from '../infra/adminUser.api';

const ROLE_LABELS: Record<UserRole, string> = { ADMIN: '관리자', ENGINEER: '엔지니어', WORKER: '작업자' };
const STATE_LABELS: Record<UserState, string> = { LOGIN: '로그인', LOGOUT: '로그아웃', PENDING: '승인 대기' };
const STATE_STYLE: Record<UserState, string> = {
  LOGIN: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-300',
  LOGOUT: 'border-slate-500/40 bg-slate-500/10 text-slate-300',
  PENDING: 'border-amber-400/40 bg-amber-500/10 text-amber-300',
};

export function AllUsersPanel() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await adminUserApi.getAllUsers();
      setUsers(data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '사용자 목록을 불러오지 못했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleRoleChange = async (userId: string, role: UserRole) => {
    setBusyUserId(userId);
    try {
      const updated = await adminUserApi.updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '역할 변경 실패');
    } finally {
      setBusyUserId(null);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!window.confirm('정말로 이 사용자를 삭제하시겠습니까? 복구할 수 없습니다.')) return;
    setBusyUserId(userId);
    try {
      await adminUserApi.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '삭제 실패');
    } finally {
      setBusyUserId(null);
    }
  };

  return (
    <Panel className="p-6">
      <div className="flex items-center justify-between border-b border-slate-700/80 pb-5">
        <div>
          <h2 className="flex items-center gap-3 text-[24px] font-black tracking-[-0.05em] text-white">
            <Users className="h-6 w-6 text-blue-400" />
            전체 사용자 ({users.length})
          </h2>
          <p className="mt-2 text-[13px] font-semibold text-slate-500">
            등록된 모든 사용자를 조회하고 역할 변경 또는 삭제할 수 있습니다.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={isLoading}
          className="grid h-10 w-10 place-items-center rounded-lg border border-slate-700 text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300 disabled:opacity-50"
          aria-label="새로고침"
        >
          <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {errorMessage && (
        <p className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      {isLoading ? (
        <p className="mt-10 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
      ) : users.length === 0 ? (
        <p className="mt-10 text-center text-[14px] font-bold text-slate-500">등록된 사용자가 없습니다.</p>
      ) : (
        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-700/80">
          <div className="grid h-12 grid-cols-[1.2fr_1.6fr_1.2fr_1.2fr_120px_120px] items-center bg-slate-950/40 px-5 text-[13px] font-black text-slate-500">
            <span>이름</span>
            <span>이메일</span>
            <span>소속</span>
            <span>역할</span>
            <span>상태</span>
            <span className="text-center">관리</span>
          </div>
          {users.map((user) => (
            <div
              key={user.id}
              className="grid min-h-[72px] grid-cols-[1.2fr_1.6fr_1.2fr_1.2fr_120px_120px] items-center border-t border-slate-800/90 px-5 text-[14px] font-semibold text-slate-200"
            >
              <span className="flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-blue-500/10 text-blue-300">
                  <UserRound className="h-4 w-4" />
                </span>
                {user.name}
              </span>
              <span className="truncate text-slate-400">{user.email}</span>
              <span className="text-slate-300">{user.department}</span>
              <select
                value={user.role}
                onChange={(event) => void handleRoleChange(user.id, event.target.value as UserRole)}
                disabled={busyUserId === user.id}
                className="h-9 rounded-lg border border-slate-700 bg-slate-950/50 px-2 text-[13px] font-bold text-white outline-none focus:border-blue-400/70 disabled:opacity-50"
              >
                {(Object.keys(ROLE_LABELS) as UserRole[]).map((role) => (
                  <option key={role} value={role} className="bg-slate-950 text-white">
                    {ROLE_LABELS[role]}
                  </option>
                ))}
              </select>
              <span className={`inline-flex h-7 w-fit items-center rounded-md border px-2 text-[12px] font-black ${STATE_STYLE[user.state]}`}>
                {STATE_LABELS[user.state]}
              </span>
              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={() => void handleDelete(user.id)}
                  disabled={busyUserId === user.id}
                  className="grid h-9 w-9 place-items-center rounded-lg border border-red-500/40 text-red-300 transition hover:bg-red-500/10 disabled:opacity-50"
                  aria-label="삭제"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}
