'use client';

import { useState, useCallback } from 'react';
import { config } from '@/lib/config';
import type { AppMode, InferenceMode } from '@/types';

export function useMode() {
  const [appMode, setAppMode] = useState<AppMode>(config.appMode);
  const [inferenceMode] = useState<InferenceMode>(config.inferenceMode);

  const toggleAppMode = useCallback(() => {
    setAppMode((prev) => (prev === 'demo' ? 'real' : 'demo'));
  }, []);

  return {
    appMode,
    inferenceMode,
    isDemo: appMode === 'demo',
    isReal: appMode === 'real',
    isOnline: inferenceMode === 'online',
    isOffline: inferenceMode === 'offline',
    toggleAppMode,
  };
}
