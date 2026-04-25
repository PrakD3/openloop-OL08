'use client';

import { useTranslation } from 'react-i18next';
import { Share2, MapPin, Calendar, AlertTriangle, CheckCircle2, XCircle, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScoreRing } from './ScoreRing';
import { ModelBreakdown } from './ModelBreakdown';
import { SOSMap } from './SOSMap';
import { cn, getVerdictBg, getVerdictColor } from '@/lib/utils';
import type { AnalysisResult } from '@/types';

interface VerdictCardProps {
  result: AnalysisResult;
}

const DISASTER_EMOJI: Record<string, string> = {
  flood: '🌊',
  earthquake: '🏚️',
  cyclone: '🌀',
  tsunami: '🌊',
  wildfire: '🔥',
  landslide: '⛰️',
  unknown: '⚠️',
};

export function VerdictCard({ result }: VerdictCardProps) {
  const { t } = useTranslation();

  const verdictLabel = t(`verdict.${result.verdict}`);
  const deepfakeAgent = result.agents.find((a) => a.agentId === 'deepfake-detector');
  const hasModelScores = (deepfakeAgent?.modelScores?.length ?? 0) > 0;

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Vigilens — ${verdictLabel}`,
        text: result.summary,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className="space-y-4">
      {/* Main verdict card */}
      <Card className={cn('border-2 transition-all', getVerdictBg(result.verdict))}>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              {/* Disaster type badge */}
              {result.disasterType && result.disasterType !== 'unknown' && (
                <p className="text-xs text-muted-foreground mb-1">
                  {DISASTER_EMOJI[result.disasterType]} Disaster type:{' '}
                  <span className="font-semibold capitalize">{result.disasterType}</span>
                </p>
              )}
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                {t('analysis.verdict')}
              </p>
              <CardTitle className={cn('text-3xl font-black', getVerdictColor(result.verdict))}>
                {verdictLabel}
              </CardTitle>
            </div>
            <div className="flex items-center gap-4">
              <ScoreRing
                score={result.credibilityScore}
                label={t('analysis.credibilityScore')}
                size={100}
                strokeWidth={8}
                colorClass={result.verdict === 'real' ? 'text-accent' : 'text-destructive'}
              />
              <ScoreRing
                score={result.panicIndex * 10}
                label={t('analysis.panicIndex')}
                size={100}
                strokeWidth={8}
                colorClass="text-primary"
              />
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* Plain-English summary — black & white style */}
          <div className="rounded-lg border border-border bg-background p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Summary
              </p>
            </div>
            <p className="text-sm leading-relaxed text-foreground font-normal">
              {result.summary}
            </p>
          </div>

          {/* Key flags */}
          {result.keyFlags.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {t('analysis.keyFlags')}
              </p>
              <div className="flex flex-wrap gap-2">
                {result.keyFlags.map((flag, i) => (
                  <div key={i} className="flex items-center gap-1 text-xs bg-secondary rounded-full px-3 py-1">
                    <AlertTriangle className="h-3 w-3 text-destructive" />
                    {flag}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Per-model deepfake breakdown */}
          {hasModelScores && (
            <ModelBreakdown modelScores={deepfakeAgent!.modelScores!} />
          )}

          {/* Metadata grid */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            {result.sourceOrigin && (
              <div className="space-y-1">
                <p className="font-medium text-muted-foreground">{t('analysis.sourceOrigin')}</p>
                <a
                  href={result.sourceOrigin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline truncate block"
                >
                  {result.sourceOrigin}
                </a>
              </div>
            )}
            {result.originalDate && (
              <div className="space-y-1">
                <p className="font-medium text-muted-foreground flex items-center gap-1">
                  <Calendar className="h-3 w-3" /> Original Date
                </p>
                <p>{result.originalDate}</p>
              </div>
            )}
            {result.claimedLocation && (
              <div className="space-y-1">
                <p className="font-medium text-muted-foreground flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> Claimed Location
                </p>
                <p>{result.claimedLocation}</p>
              </div>
            )}
            {result.actualLocation && result.actualLocation !== result.claimedLocation && (
              <div className="space-y-1">
                <p className="font-medium text-destructive flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> Actual Location
                </p>
                <p className="text-destructive">{result.actualLocation}</p>
              </div>
            )}
          </div>

          <Button onClick={handleShare} variant="outline" size="sm" className="w-full">
            <Share2 className="h-4 w-4 mr-2" />
            {t('analysis.shareResult')}
          </Button>
        </CardContent>
      </Card>

      {/* SOS Map — only when genuine disaster confirmed */}
      {result.sosRegion?.sosActive && (
        <Card className="border-2 border-destructive/40 bg-destructive/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-destructive flex items-center gap-2">
              🆘 SOS Impact Region
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SOSMap sosRegion={result.sosRegion} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
