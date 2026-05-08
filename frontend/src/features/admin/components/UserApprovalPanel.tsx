import { CheckCircle2, RefreshCw, ShieldCheck, UserRound } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import type { UserRole } from '../../../entities/user/model/user.types';
import { useApproveUser } from '../hooks/useApproveUser';
import { usePendingUsers } from '../hooks/usePendingUsers';

const roleLabels: Record<UserRole, string> = {
  ADMIN: '관리자',
  WORKER: '작업자',
  ENGINEER: '엔지니어',
};

export function UserApprovalPanel() {
  const { users, isLoading, errorMessage, refetch, removePendingUser } = usePendingUsers();
  const { approveUser, approvingUserId, errorMessage: approveErrorMessage } = useApproveUser();

  const handleApprove = async (userId: string) => {
    const isApproved = await approveUser(userId);

    if (isApproved) {
      removePendingUser(userId);
    }
  };

  return (
    <Panel className="p-6">
      <div className="flex flex-col gap-4 border-b border-slate-700/80 pb-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="flex items-center gap-3 text-[26px] font-black tracking-[-0.05em] text-white">
            <ShieldCheck className="h-7 w-7 text-blue-400" />
            사용자 승인
          </h2>
          <p className="mt-2 text-[15px] font-semibold text-slate-500">
            회원가입 후 승인 대기 중인 사용자를 확인하고 로그인 가능 상태로 변경합니다.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void refetch()}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-700 px-4 text-sm font-bold text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300"
        >
          <RefreshCw className="h-4 w-4" />
          새로고침
        </button>
      </div>

      {(errorMessage || approveErrorMessage) && (
        <p className="mt-5 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm font-bold text-red-300">
          {approveErrorMessage ?? errorMessage}
        </p>
      )}

      {isLoading ? (
        <div className="grid min-h-[260px] place-items-center text-[18px] font-bold text-slate-400">
          승인 대기 사용자를 불러오는 중...
        </div>
      ) : users.length === 0 ? (
        <div className="grid min-h-[260px] place-items-center rounded-2xl border border-dashed border-slate-700/80 bg-slate-950/20 text-center">
          <div>
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-400" />
            <p className="mt-4 text-[20px] font-black text-white">승인 대기 사용자가 없습니다</p>
            <p className="mt-2 text-sm font-semibold text-slate-500">신규 가입자가 생기면 이곳에 표시됩니다.</p>
          </div>
        </div>
      ) : (
        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-700/80">
          <div className="grid h-12 grid-cols-[1.3fr_1.5fr_1fr_1fr_120px] items-center bg-slate-950/40 px-5 text-sm font-black text-slate-500">
            <span>이름</span>
            <span>이메일</span>
            <span>소속</span>
            <span>역할</span>
            <span className="text-center">승인</span>
          </div>

          {users.map((user) => (
            <div
              key={user.id}
              className="grid min-h-[72px] grid-cols-[1.3fr_1.5fr_1fr_1fr_120px] items-center border-t border-slate-800/90 px-5 text-[15px] font-semibold text-slate-200"
            >
              <span className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-full bg-blue-500/10 text-blue-300">
                  <UserRound className="h-5 w-5" />
                </span>
                {user.name}
              </span>
              <span className="truncate text-slate-400">{user.email}</span>
              <span className="text-slate-300">{user.department}</span>
              <span className="text-slate-300">{roleLabels[user.role]}</span>
              <button
                type="button"
                onClick={() => void handleApprove(user.id)}
                disabled={approvingUserId === user.id}
                className="h-10 rounded-xl bg-blue-600 px-4 text-sm font-black text-white shadow-[0_0_18px_rgba(37,99,235,0.28)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
              >
                {approvingUserId === user.id ? '처리 중' : '승인'}
              </button>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}
