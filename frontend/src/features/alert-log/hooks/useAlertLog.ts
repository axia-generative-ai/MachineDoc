import { useEffect, useMemo, useState } from 'react';

import { alertLogApi, type AlertLogItem, type NotificationLevel, type ReadStatus } from '../infra/alertLog.api';
import type { alertFilters } from '../model/alertLogData';

export function useAlertLog(filter: (typeof alertFilters)[number]) {
  const [items, setItems] = useState<AlertLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setItems(await alertLogApi.list(200));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '알림 이력을 불러오지 못했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const filtered = useMemo(() => {
    if (filter === '전체') return items;
    return items.filter((item) => item.level === (filter as NotificationLevel));
  }, [items, filter]);

  const updateStatus = async (notificationId: number, isRead: ReadStatus) => {
    setBusyId(notificationId);
    try {
      const updated = await alertLogApi.updateReadStatus(notificationId, isRead);
      setItems((prev) => prev.map((item) => (item.notificationId === notificationId ? updated : item)));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '상태 변경 실패');
    } finally {
      setBusyId(null);
    }
  };

  return { items, filtered, isLoading, errorMessage, busyId, load, updateStatus };
}
