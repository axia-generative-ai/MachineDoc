import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

import { QueryProvider } from './app/providers/QueryProvider';
import { routes } from './app/router/routes';
import { initializeThemePreference } from './shared/theme/themePreference';
import './styles/index.css';

initializeThemePreference();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryProvider>
      <RouterProvider router={routes} />
    </QueryProvider>
  </React.StrictMode>,
);
