'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';
import { AgentPanel } from '@/components/analysis/AgentPanel';
import { VerdictCard } from '@/components/analysis/VerdictCard';
import { CommunityFeed } from '@/components/community/CommunityFeed';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function AnalysisPage() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const videoUrl = searchParams.get('url') ?? '';
  const isDemo = searchParams.get('demo') !== 'false';

  const { result, isLoading, agentProgress, error, analyze } = useAnalysis();

  useEffect(() => {
    if (videoUrl) {
      analyze(videoUrl, isDemo);
    }
  }, [videoUrl, isDemo, analyze]);

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-2xl font-bold mb-2">{t('analysis.title')}</h1>
        {videoUrl && (
          <p className="text-sm text-muted-foreground mb-6 truncate">
            Analysing: {videoUrl}
          </p>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
            {error}
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            {isLoading || agentProgress.length > 0 ? (
              <AgentPanel agents={agentProgress} />
            ) : !result ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Initialising agents...</span>
              </div>
            ) : null}
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <>
                <VerdictCard result={result} />
                <CommunityFeed />
              </>
            ) : isLoading ? (
              <div className="flex flex-col items-center justify-center h-64 gap-4">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
                <p className="text-muted-foreground">Running AI analysis pipeline...</p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
