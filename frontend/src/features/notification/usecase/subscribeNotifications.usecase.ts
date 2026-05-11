import type { NotificationRepository, NotificationSubscriptionHandlers } from '../domain/notification.repository';

export function subscribeNotificationsUseCase(repository: NotificationRepository, handlers: NotificationSubscriptionHandlers) {
  return repository.subscribe(handlers);
}
