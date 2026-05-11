import type { AdminUserRepository } from '../domain/adminUser.repository';
import { adminUserApi } from './adminUser.api';

export const adminUserRepositoryImpl: AdminUserRepository = {
  getPendingUsers: adminUserApi.getPendingUsers,
  approveUser: adminUserApi.approveUser,
};
