import type { NotificationRepository } from '../domain/notification.repository';
import { notificationSocketApi } from './notificationSocket.api';

export const notificationRepositoryImpl: NotificationRepository = {
  subscribe: notificationSocketApi.subscribe,
};
