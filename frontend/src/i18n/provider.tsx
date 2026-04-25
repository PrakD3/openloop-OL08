'use client';

import { useEffect } from 'react';
import '@/i18n/config';

export function I18nProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // i18n initialized via import side effect
  }, []);

  return <>{children}</>;
}
