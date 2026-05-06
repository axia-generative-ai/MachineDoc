import { AdminHeader } from '../../features/admin/components/AdminHeader';
import { AdminManualRegistration } from '../../features/admin/components/AdminManualRegistration';
import { AdminTabs } from '../../features/admin/components/AdminTabs';

export function AdminPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <AdminHeader />
      <AdminTabs />
      <AdminManualRegistration />
    </div>
  );
}
