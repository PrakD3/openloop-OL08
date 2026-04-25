'use client';

import { useTranslation } from 'react-i18next';
import { CheckCircle2, XCircle, HelpCircle, Megaphone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MOCK_BULLETINS } from '@/lib/demoData';
import { cn } from '@/lib/utils';
import type { VerdictType } from '@/types';

const VerdictIcon = ({ verdict }: { verdict: VerdictType }) => {
  switch (verdict) {
    case 'real':
      return <CheckCircle2 className="h-4 w-4 text-accent" />;
    case 'misleading':
    case 'ai-generated':
      return <XCircle className="h-4 w-4 text-destructive" />;
    case 'unverified':
    default:
      return <HelpCircle className="h-4 w-4 text-muted-foreground" />;
  }
};

export function BulletinBoard() {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Megaphone className="h-5 w-5 text-accent" />
        <h2 className="text-xl font-bold">{t('bulletin.title')}</h2>
      </div>
      <div className="space-y-3">
        {MOCK_BULLETINS.map((item) => (
          <Card
            key={item.id}
            className={cn(
              'border-l-4',
              item.verdict === 'real' && 'border-l-accent',
              (item.verdict === 'misleading' || item.verdict === 'ai-generated') && 'border-l-destructive',
              item.verdict === 'unverified' && 'border-l-muted-foreground'
            )}
          >
            <CardHeader className="p-4 pb-2">
              <div className="flex items-start gap-2">
                <VerdictIcon verdict={item.verdict} />
                <div className="flex-1">
                  <CardTitle className="text-sm leading-tight">{item.title}</CardTitle>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={item.verdict as 'real' | 'misleading' | 'unverified'} className="text-xs">
                      {t(`verdict.${item.verdict}`)}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{item.region}</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-4 pb-4 pt-0">
              <p className="text-sm text-muted-foreground">{item.content}</p>
              <p className="text-xs text-muted-foreground mt-2">
                Source: {item.source} · {new Date(item.timestamp).toLocaleDateString()}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
