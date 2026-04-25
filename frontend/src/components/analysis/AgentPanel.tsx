'use client';

import { useTranslation } from 'react-i18next';
import { CheckCircle2, Loader2, XCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import type { AgentFinding } from '@/types';

interface AgentPanelProps {
  agents: AgentFinding[];
}

function AgentStatusIcon({ status }: { status: AgentFinding['status'] }) {
  switch (status) {
    case 'running':
      return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
    case 'done':
      return <CheckCircle2 className="h-4 w-4 text-accent" />;
    case 'error':
      return <XCircle className="h-4 w-4 text-destructive" />;
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

export function AgentPanel({ agents }: AgentPanelProps) {
  const { t } = useTranslation();

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
        {t('analysis.agents')}
      </h3>
      {agents.map((agent) => (
        <Card
          key={agent.agentId}
          className={cn(
            'transition-all duration-300',
            agent.status === 'running' && 'border-primary/50 shadow-sm',
            agent.status === 'done' && 'border-accent/30'
          )}
        >
          <CardHeader className="p-4 pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AgentStatusIcon status={agent.status} />
                <CardTitle className="text-sm">{agent.agentName}</CardTitle>
              </div>
              {agent.score !== null && (
                <Badge variant={agent.score > 50 ? 'destructive' : 'real'} className="text-xs">
                  {agent.agentId === 'deepfake-detector'
                    ? `${agent.score}% fake`
                    : `${agent.score}% authentic`}
                </Badge>
              )}
            </div>
          </CardHeader>
          {agent.status === 'running' && (
            <CardContent className="px-4 pb-4 pt-0">
              <Progress value={undefined} className="h-1 animate-pulse" />
            </CardContent>
          )}
          {agent.status === 'done' && agent.findings.length > 0 && (
            <CardContent className="px-4 pb-4 pt-0">
              <ul className="space-y-1">
                {agent.findings.map((finding, i) => (
                  <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                    <span className="text-accent mt-0.5">•</span>
                    {finding}
                  </li>
                ))}
              </ul>
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
}
