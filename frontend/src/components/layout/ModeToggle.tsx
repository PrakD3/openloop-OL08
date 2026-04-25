'use client';

import { useMode } from '@/hooks/useMode';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { config } from '@/lib/config';
import { AlertTriangle } from 'lucide-react';

export function ModeToggle() {
  const { appMode, inferenceMode, toggleAppMode } = useMode();

  return (
    <div className="flex items-center gap-2">
      <Badge variant={inferenceMode === 'online' ? 'default' : 'secondary'} className="text-xs">
        {inferenceMode === 'online' ? '🌐 Online' : '📦 Offline'}
      </Badge>

      <Button
        variant="outline"
        size="sm"
        onClick={toggleAppMode}
        className="text-xs h-7 px-2"
      >
        {appMode === 'demo' ? '🎬 Demo' : '🔴 Real'}
      </Button>

      {appMode === 'real' && inferenceMode === 'offline' && (
        <div className="flex items-center gap-1 text-xs text-destructive">
          <AlertTriangle className="h-3 w-3" />
          <span className="hidden lg:inline">Local models required</span>
        </div>
      )}
    </div>
  );
}
