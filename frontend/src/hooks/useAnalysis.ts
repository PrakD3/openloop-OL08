'use client';

import { useState, useCallback } from 'react';
import type { AnalysisResult, AgentFinding } from '@/types';
import { DEMO_VIDEOS } from '@/lib/demoData';
import { sleep } from '@/lib/utils';

interface UseAnalysisReturn {
  result: AnalysisResult | null;
  isLoading: boolean;
  agentProgress: AgentFinding[];
  error: string | null;
  analyze: (videoUrl: string, isDemo?: boolean) => Promise<void>;
  reset: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [agentProgress, setAgentProgress] = useState<AgentFinding[]>([]);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setResult(null);
    setIsLoading(false);
    setAgentProgress([]);
    setError(null);
  }, []);

  const analyze = useCallback(async (videoUrl: string, isDemo = true) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setAgentProgress([]);

    try {
      if (isDemo) {
        const demoVideo = DEMO_VIDEOS.find((v) => v.url === videoUrl) ?? DEMO_VIDEOS[0];
        const precomputed = demoVideo.precomputedResult;

        const initialAgents: AgentFinding[] = precomputed.agents.map((a) => ({
          ...a,
          status: 'idle' as const,
          score: null,
          findings: [],
          detail: null,
        }));
        setAgentProgress(initialAgents);

        for (let i = 0; i < precomputed.agents.length; i++) {
          setAgentProgress((prev) =>
            prev.map((a, idx) => (idx === i ? { ...a, status: 'running' } : a))
          );
          await sleep((i + 1) * 2500);
          setAgentProgress((prev) =>
            prev.map((a, idx) =>
              idx === i ? { ...precomputed.agents[i], status: 'done' } : a
            )
          );
        }

        await sleep(1000);
        setResult(precomputed);
      } else {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ videoUrl }),
        });

        if (!response.ok) {
          throw new Error('Analysis failed. Please try again.');
        }

        const data = (await response.json()) as AnalysisResult;
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { result, isLoading, agentProgress, error, analyze, reset };
}
