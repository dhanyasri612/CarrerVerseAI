import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

/**
 * CSS load order:
 * 1. reimagined.css  — new editorial design system (tokens, 6 themes, cv2-* layout)
 * 2. App.css         — kept for public pages: LandingPage, LoginPage, RegisterPage
 *                      (auth-page, auth-card, primary-button, landing-nav etc.)
 *                      Old sidebar classes inside it are dead code — they never render.
 * 3. ai8b.css        — Phase 8B AI page styles (cv-pill-*, cv-gap-*, cv-question-*)
 */
import './index.css';
import './reimagined.css';
import './App.css';
import './ai8b.css';

import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
