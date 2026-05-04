import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';

import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';

export function MainLayout() {
  // 사이드바 열림 상태는 TopBar와 본문 여백이 함께 사용하므로 레이아웃에서 관리합니다.
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') {
      return true;
    }

    return window.matchMedia('(min-width: 1024px)').matches;
  });

  useEffect(() => {
    const desktopQuery = window.matchMedia('(min-width: 1024px)');
    const handleViewportChange = (event: MediaQueryListEvent) => {
      setIsSidebarOpen(event.matches);
    };

    desktopQuery.addEventListener('change', handleViewportChange);

    return () => {
      desktopQuery.removeEventListener('change', handleViewportChange);
    };
  }, []);

  const handleSidebarToggle = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const handleSidebarClose = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-factory-radial text-slate-100">
      {/* 모바일에서는 사이드바가 본문 위를 덮기 때문에 배경 딤을 눌러 닫을 수 있게 합니다. */}
      {isSidebarOpen && <button type="button" aria-label="사이드바 닫기" onClick={handleSidebarClose} className="fixed inset-0 z-10 bg-black/55 backdrop-blur-[2px] lg:hidden" />}

      <Sidebar isOpen={isSidebarOpen} />
      <div className={`transition-[padding] duration-300 ease-out ${isSidebarOpen ? 'lg:pl-[252px]' : 'lg:pl-0'}`}>
        <TopBar isSidebarOpen={isSidebarOpen} onMenuClick={handleSidebarToggle} />
        <main className="px-5 pb-7 pt-[106px] lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
