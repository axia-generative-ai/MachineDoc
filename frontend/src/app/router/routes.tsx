import { createBrowserRouter } from 'react-router-dom';

import { MainLayout } from '../layouts/MainLayout';
import { AdminPage } from '../../pages/AdminPage/AdminPage';
import { AlertLogPage } from '../../pages/AlertLogPage/AlertLogPage';
import { DashboardPage } from '../../pages/DashboardPage/DashboardPage';
import { DetectionPage } from '../../pages/DetectionPage/DetectionPage';
import { ErrorSearchPage } from '../../pages/ErrorSearchPage/ErrorSearchPage';
import { ErrorSearchResultPage } from '../../pages/ErrorSearchResultPage/ErrorSearchResultPage';
import { NewPage } from '../../pages/NewPage/NewPage';

export const routes = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'error-search', element: <ErrorSearchPage /> },
      { path: 'error-search/result', element: <ErrorSearchResultPage /> },
      { path: 'detection', element: <DetectionPage /> },
      { path: 'alert-log', element: <AlertLogPage /> },
      { path: 'admin', element: <AdminPage /> },
      { path: 'new', element: <NewPage /> },
    ],
  },
]);
