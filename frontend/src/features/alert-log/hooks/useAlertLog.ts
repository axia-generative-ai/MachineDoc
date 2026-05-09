import { useEffect, useMemo, useState } from 'react';

import { alertLogApi, type AlertLogItem, type NotificationLevel, type ReadStatus } from '../infra/alertLog.api';
import { alertFilters } from '../model/alertLogData';

export const ALERT_LOG_PAGE_SIZE = 10;

export function useAlertLog(filter: (typeof alertFilters)[number], page: number) {
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
    if (filter === alertFilters[0]) return items;
    return items.filter((item) => item.level === (filter as NotificationLevel));
  }, [items, filter]);

  const pagedItems = useMemo(() => {
    const start = (page - 1) * ALERT_LOG_PAGE_SIZE;
    return filtered.slice(start, start + ALERT_LOG_PAGE_SIZE);
  }, [filtered, page]);

  const updateStatus = async (notificationId: number, isRead: ReadStatus) => {
    setBusyId(notificationId);

    try {
      const updated = await alertLogApi.updateReadStatus(notificationId, isRead);
      setItems((prev) => prev.map((item) => (item.notificationId === notificationId ? updated : item)));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '상태 변경에 실패했습니다.');
    } finally {
      setBusyId(null);
    }
  };

  return { items, filtered, pagedItems, isLoading, errorMessage, busyId, load, updateStatus };
}
