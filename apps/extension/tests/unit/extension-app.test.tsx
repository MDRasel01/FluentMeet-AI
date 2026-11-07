import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExtensionApp } from '../../ExtensionApp';
import { useExtensionStore } from '../../src/sidepanel/store/extension-store';

describe('ExtensionApp UI Component Tests', () => {
  beforeEach(() => {
    // Reset store state
    useExtensionStore.setState({
      screen: 'detected',
      sessionState: 'MEETING_DETECTED',
      consentChecked: false,
      micVolume: 45,
      tabVolume: 70,
    });
  });

  it('should render header with SidePanel branding and version', () => {
    render(<ExtensionApp initialScreen="detected" />);
    expect(screen.getByText('Meeting Coach SidePanel')).toBeDefined();
    expect(screen.getByText('v1.0.2')).toBeDefined();
  });

  it('should disable Start Analysis button until consent checkbox is confirmed (Section 8 mandate)', () => {
    render(<ExtensionApp initialScreen="detected" />);

    const startButton = screen.getByRole('button', { name: /Start Analysis Session/i });
    expect(startButton.hasAttribute('disabled')).toBe(true);

    const consentCheckbox = screen.getByRole('checkbox');
    fireEvent.click(consentCheckbox);

    // After ticking consent checkbox, button must be enabled
    expect(startButton.hasAttribute('disabled')).toBe(false);
  });

  it('should render live session with dual VU signal meters and timer', () => {
    render(<ExtensionApp initialScreen="live" />);

    expect(screen.getByText(/Live Recording Active/i)).toBeDefined();
    expect(screen.getByText(/Your Microphone/i)).toBeDefined();
    expect(screen.getByText(/Meeting Tab Audio/i)).toBeDefined();
    expect(screen.getByText(/Pause Session/i)).toBeDefined();
    expect(screen.getByText(/Stop & Analyze/i)).toBeDefined();
  });
});

