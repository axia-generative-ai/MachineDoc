import { createBrowserRouter } from 'react-router-dom';

import { MainLayout } from '../layouts/MainLayout';
import { AdminPage } from '../../pages/AdminPage/AdminPage';
import { AlertLogPage } from '../../pages/AlertLogPage/AlertLogPage';
import { DashboardPage } from '../../pages/DashboardPage/DashboardPage';
import { DetectionPage } from '../../pages/DetectionPage/DetectionPage';
import { ErrorSearchPage } from '../../pages/ErrorSearchPage/ErrorSearchPage';
import { ErrorSearchResultPage } from '../../pages/ErrorSearchResultPage/ErrorSearchResultPage';
import { LoginPage } from '../../pages/LoginPage/LoginPage';
import { SearchHistoryPage } from '../../pages/SearchHistoryPage/SearchHistoryPage';
import { SettingsPage } from '../../pages/SettingsPage/SettingsPage';
import { SignupPage } from '../../pages/SignupPage/SignupPage';

export const routes = createBrowserRouter([
  { path: '/', element: <LoginPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/signup', element: <SignupPage /> },
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'error-search', element: <ErrorSearchPage /> },
      { path: 'error-search/result', element: <ErrorSearchResultPage /> },
      { path: 'detection', element: <DetectionPage /> },
      { path: 'alert-log', element: <AlertLogPage /> },
      { path: 'search-history', element: <SearchHistoryPage /> },
      { path: 'action-history', element: <SearchHistoryPage /> },
      { path: 'saved-documents', element: <SearchHistoryPage /> },
      { path: 'admin', element: <AdminPage /> },
      { path: 'settings', element: <SettingsPage /> },
    ],
  },
]);
