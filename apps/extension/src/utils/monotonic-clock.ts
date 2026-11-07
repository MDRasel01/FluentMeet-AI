/**
 * Monotonic Session Clock
 * Provides precise session-relative monotonic timestamps without wall-clock skew.
 * Specification: Step 05 - Section 10
 */

export class MonotonicSessionClock {
  private sessionStartMonoTime: number | null = null;
  private sessionStartWallTime: number | null = null;

  public start(): void {
    this.sessionStartMonoTime = performance.now();
    this.sessionStartWallTime = Date.now();
  }

  public getSessionRelativeMs(): number {
    if (this.sessionStartMonoTime === null) {
      return 0;
    }
    return Math.max(0, Math.round(performance.now() - this.sessionStartMonoTime));
  }

  public getSessionStartWallTime(): number | null {
    return this.sessionStartWallTime;
  }

  public reset(): void {
    this.sessionStartMonoTime = null;
    this.sessionStartWallTime = null;
  }
}

