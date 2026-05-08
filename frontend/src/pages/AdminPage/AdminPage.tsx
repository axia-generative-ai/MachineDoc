import { useState } from 'react';

import { AdminHeader } from '../../features/admin/components/AdminHeader';
import { AdminManualRegistration } from '../../features/admin/components/AdminManualRegistration';
import { AdminTabs } from '../../features/admin/components/AdminTabs';
import { UserApprovalPanel } from '../../features/admin/components/UserApprovalPanel';
import { adminTabs, type AdminTab } from '../../features/admin/model/adminData';

export function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>(adminTabs[0]);

  return (
    <div className="mx-auto max-w-[1640px]">
      <AdminHeader />
      <AdminTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === '사용자 승인' ? <UserApprovalPanel /> : <AdminManualRegistration />}
    </div>
  );
}
