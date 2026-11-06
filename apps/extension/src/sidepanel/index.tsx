import React from 'react';
import ReactDOM from 'react-dom/client';
import { ExtensionApp } from '../../ExtensionApp';
import './sidepanel.css';

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <div className="dark min-h-screen bg-[#0B0F19] text-white">
        <ExtensionApp isDark={true} />
      </div>
    </React.StrictMode>
  );
}

