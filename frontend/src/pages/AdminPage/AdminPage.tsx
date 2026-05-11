import { useState } from 'react';

import { AdminHeader } from '../../features/admin/components/AdminHeader';
import { AdminManualRegistration } from '../../features/admin/components/AdminManualRegistration';
import { AdminPromptPanel } from '../../features/admin/components/AdminPromptPanel';
import { AdminTabs } from '../../features/admin/components/AdminTabs';
import { AllUsersPanel } from '../../features/admin/components/AllUsersPanel';
import { ErrorCodeMappingPanel } from '../../features/admin/components/ErrorCodeMappingPanel';
import { UserApprovalPanel } from '../../features/admin/components/UserApprovalPanel';
import { adminTabs, type AdminTab } from '../../features/admin/model/adminData';

export function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>(adminTabs[0]);
  const [mappingRefreshKey, setMappingRefreshKey] = useState(0);

  const handleManualUploaded = () => {
    setMappingRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="mx-auto max-w-[1640px]">
      <AdminHeader />
      <AdminTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === '매뉴얼 등록' && <AdminManualRegistration onUploadSuccess={handleManualUploaded} />}
      {activeTab === '오류코드 매핑' && <ErrorCodeMappingPanel refreshKey={mappingRefreshKey} />}
      {activeTab === '프롬프트 관리' && <AdminPromptPanel />}
      {activeTab === '사용자 승인' && (
        <div className="space-y-6">
          <UserApprovalPanel />
          <AllUsersPanel />
        </div>
      )}
    </div>
  );
}
