'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Zap, Eye, Globe, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DEMO_VIDEOS, MOCK_INCIDENTS } from '@/lib/demoData';
import { useMode } from '@/hooks/useMode';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { t } = useTranslation();
  const { isDemo } = useMode();
  const router = useRouter();
  const [videoUrl, setVideoUrl] = useState('');
  const [selectedDemo, setSelectedDemo] = useState(DEMO_VIDEOS[0].url);

  const handleAnalyse = () => {
    const url = isDemo ? selectedDemo : videoUrl;
    if (!url) return;
    router.push(`/analysis?url=${encodeURIComponent(url)}&demo=${isDemo}`);
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background to-secondary/20 py-20 px-4">
        <div className="mx-auto max-w-4xl text-center space-y-6">
          <div className="flex justify-center">
            <Badge variant="secondary" className="text-sm px-4 py-1">
              🛡️ AI-Powered Verification
            </Badge>
          </div>
          <h1 className="text-4xl md:text-6xl font-black tracking-tight">
            {t('home.hero')}
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {t('home.subtitle')}
          </p>

          {/* Video Submission */}
          <div className="max-w-2xl mx-auto mt-8">
            {isDemo ? (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">Select a demo video to analyse:</p>
                <div className="grid gap-2">
                  {DEMO_VIDEOS.map((video) => (
                    <button
                      key={video.id}
                      onClick={() => setSelectedDemo(video.url)}
                      className={`text-left p-3 rounded-lg border transition-all text-sm ${
                        selectedDemo === video.url
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      {video.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex gap-2">
                <Input
                  type="url"
                  placeholder={t('home.submitPlaceholder')}
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  className="flex-1"
                />
              </div>
            )}
            <Button onClick={handleAnalyse} size="lg" className="w-full mt-3">
              {t('home.analyseButton')}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="mx-auto max-w-6xl">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Zap, title: 'DeepFake Detector', desc: 'CrossEfficientViT model analyses every keyframe for AI generation artifacts' },
              { icon: Eye, title: 'Source Hunter', desc: 'Reverse image search + EXIF metadata to find the earliest known source' },
              { icon: Globe, title: 'Context Analyser', desc: 'Whisper transcription + vision LLM verifies location, language, and timing' },
            ].map((feature) => (
              <Card key={feature.title} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <feature.icon className="h-8 w-8 text-accent mb-2" />
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{feature.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Active Incidents Preview */}
      <section className="py-16 px-4 bg-secondary/20">
        <div className="mx-auto max-w-6xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Active Incidents</h2>
            <Button variant="outline" size="sm" asChild>
              <a href="/incidents">View All <ArrowRight className="ml-1 h-3 w-3" /></a>
            </Button>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {MOCK_INCIDENTS.map((incident) => (
              <Card key={incident.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge variant={incident.verdict as 'real' | 'misleading' | 'unverified'}>
                      {incident.verdict.toUpperCase()}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{incident.date}</span>
                  </div>
                  <CardTitle className="text-sm leading-tight mt-2">{incident.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">{incident.location}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-destructive rounded-full"
                        style={{ width: `${incident.misinfoRate}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{incident.misinfoRate}% misinfo</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4">
        <div className="mx-auto max-w-4xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { value: '2,847', label: 'Videos Analysed' },
              { value: '61%', label: 'Misinformation Rate' },
              { value: '94%', label: 'Detection Accuracy' },
              { value: '< 30s', label: 'Analysis Time' },
            ].map((stat) => (
              <div key={stat.label} className="space-y-1">
                <p className="text-3xl font-black text-accent">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
