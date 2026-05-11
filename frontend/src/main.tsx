import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

import { routes } from './app/router/routes';
import { initializeThemePreference } from './shared/theme/themePreference';
import './styles/index.css';

initializeThemePreference();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={routes} />
  </React.StrictMode>,
);
