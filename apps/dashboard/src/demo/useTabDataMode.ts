import { useState, useEffect, useCallback } from 'react';
import { TabDataMode, TabModeStateMap } from './types';

const STORAGE_KEY_PREFIX = 'fluentmeet_tab_data_modes_';

export function useTabDataMode(userId: string = 'default') {
  const storageKey = `${STORAGE_KEY_PREFIX}${userId}`;
  const [tabModes, setTabModes] = useState<TabModeStateMap>({});
  const [isHydrated, setIsHydrated] = useState(false);

  // Load persisted modes on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === 'object') {
          setTabModes(parsed);
        }
      }
    } catch (e) {
      console.warn('Failed to parse tab data modes from localStorage:', e);
    } finally {
      setIsHydrated(true);
    }
  }, [storageKey]);

  // Persist whenever tabModes change
  const persistModes = useCallback(
    (newModes: TabModeStateMap) => {
      setTabModes(newModes);
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem(storageKey, JSON.stringify(newModes));
        } catch (e) {
          console.warn('Failed to save tab data modes to localStorage:', e);
        }
      }
    },
    [storageKey]
  );

  /**
   * Get mode for a specific tab.
   * STRICT REQUIREMENT: Defaults to 'REAL' unless explicitly set by the user to 'DEMO'.
   */
  const getMode = useCallback(
    (tabKey: string): TabDataMode => {
      return tabModes[tabKey] === 'DEMO' ? 'DEMO' : 'REAL';
    },
    [tabModes]
  );

  const isDemo = useCallback(
    (tabKey: string): boolean => {
      return getMode(tabKey) === 'DEMO';
    },
    [getMode]
  );

  const setMode = useCallback(
    (tabKey: string, mode: TabDataMode) => {
      persistModes({
        ...tabModes,
        [tabKey]: mode,
      });
    },
    [tabModes, persistModes]
  );

  const toggleMode = useCallback(
    (tabKey: string) => {
      const current = getMode(tabKey);
      const next: TabDataMode = current === 'REAL' ? 'DEMO' : 'REAL';
      setMode(tabKey, next);
    },
    [getMode, setMode]
  );

  return {
    getMode,
    setMode,
    toggleMode,
    isDemo,
    isHydrated,
  };
}

