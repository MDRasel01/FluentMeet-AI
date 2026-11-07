import { describe, it, expect, beforeEach } from 'vitest';
import { SessionController } from '../../src/background/session-controller';

describe('SessionController (State Machine FSM)', () => {
  let controller: SessionController;

  beforeEach(() => {
    // Mock chrome storage
    const store: Record<string, unknown> = {};
    (globalThis as unknown as { chrome: unknown }).chrome = {
      storage: {
        session: {
          get: async (key: string) => ({ [key]: store[key] }),
          set: async (obj: Record<string, unknown>) => Object.assign(store, obj),
        },
      },
      runtime: {
        sendMessage: async () => {},
      },
    };

    controller = new SessionController();
  });

  it('should initialize with IDLE state', () => {
    expect(controller.getState()).toBe('IDLE');
  });

  it('should allow valid transitions: IDLE -> PLATFORM_DETECTED -> MEETING_DETECTED', () => {
    const t1 = controller.transition('PLATFORM_DETECTED', { platform: 'google-meet' });
    expect(t1).toBe(true);
    expect(controller.getState()).toBe('PLATFORM_DETECTED');

    const t2 = controller.transition('MEETING_DETECTED');
    expect(t2).toBe(true);
    expect(controller.getState()).toBe('MEETING_DETECTED');
  });

  it('should reject invalid transitions (e.g. IDLE directly to CAPTURING)', () => {
    const invalidTransition = controller.transition('CAPTURING');
    expect(invalidTransition).toBe(false);
    expect(controller.getState()).toBe('IDLE');
  });

  it('should transition correctly through live lifecycle: READY -> STARTING -> CAPTURING -> PAUSED -> CAPTURING -> STOPPING -> COMPLETED', () => {
    controller.transition('PLATFORM_DETECTED');
    controller.transition('MEETING_DETECTED');
    controller.transition('CONSENT_REQUIRED');
    controller.transition('PERMISSION_REQUIRED');
    controller.transition('READY');
    expect(controller.getState()).toBe('READY');

    controller.transition('STARTING', { meetingId: 'test-meet-1' });
    expect(controller.getState()).toBe('STARTING');

    controller.transition('CAPTURING');
    expect(controller.getState()).toBe('CAPTURING');

    // Pause
    controller.transition('PAUSED');
    expect(controller.getState()).toBe('PAUSED');
    expect(controller.getSession().pausedAt).toBeDefined();

    // Resume
    controller.transition('CAPTURING');
    expect(controller.getState()).toBe('CAPTURING');
    expect(controller.getSession().pausedAt).toBeUndefined();

    // Stop & Complete
    controller.transition('STOPPING');
    expect(controller.getState()).toBe('STOPPING');

    controller.transition('COMPLETED');
    expect(controller.getState()).toBe('COMPLETED');
  });

  it('should handle failure transition from any active state', () => {
    controller.transition('PLATFORM_DETECTED');
    controller.transition('FAILED', { error: 'Device disconnect' });
    expect(controller.getState()).toBe('FAILED');
    expect(controller.getSession().error).toBe('Device disconnect');
  });
});
