'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MOCK_INCIDENTS } from '@/lib/demoData';
import type { VerdictType } from '@/types';

const filters: Array<{ label: string; value: string }> = [
  { label: 'All', value: 'all' },
  { label: 'Real', value: 'real' },
  { label: 'Misleading', value: 'misleading' },
  { label: 'AI Generated', value: 'ai-generated' },
  { label: 'Unverified', value: 'unverified' },
];

export default function IncidentsPage() {
  const { t } = useTranslation();
  const [activeFilter, setActiveFilter] = useState('all');

  const filtered = MOCK_INCIDENTS.filter(
    (i) => activeFilter === 'all' || i.verdict === activeFilter
  );

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">{t('incidents.title')}</h1>
          <p className="text-muted-foreground mt-1">
            All disaster video verification incidents tracked by Vigilens
          </p>
        </div>

        <div className="flex gap-2 flex-wrap mb-6">
          {filters.map((f) => (
            <Button
              key={f.value}
              variant={activeFilter === f.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveFilter(f.value)}
            >
              {f.label}
            </Button>
          ))}
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((incident) => (
            <Card key={incident.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant={incident.verdict as VerdictType}>
                    {incident.verdict.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{incident.date}</span>
                </div>
                <CardTitle className="text-sm leading-tight">{incident.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-muted-foreground">{incident.location}</p>
                <p className="text-xs">{incident.summary}</p>

                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">{t('incidents.misinfoRate')}</span>
                    <span className="font-medium text-destructive">{incident.misinfoRate}%</span>
                  </div>
                  <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-destructive rounded-full transition-all"
                      style={{ width: `${incident.misinfoRate}%` }}
                    />
                  </div>
                </div>

                <div className="flex flex-wrap gap-1">
                  {incident.tags.map((tag) => (
                    <span key={tag} className="text-xs bg-secondary rounded-full px-2 py-0.5">
                      #{tag}
                    </span>
                  ))}
                </div>

                <p className="text-xs text-muted-foreground">
                  {t('incidents.videoCount')}: {incident.videoCount}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
