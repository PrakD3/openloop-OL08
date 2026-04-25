import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Eye, Globe, GitMerge, Server, Cpu } from 'lucide-react';

export default function HowItWorksPage() {
  const pipeline = [
    {
      step: 1,
      icon: Cpu,
      name: 'Preprocess',
      desc: 'FFmpeg extracts keyframes every 2 seconds and audio track from the video',
      tech: ['FFmpeg', 'OpenCV'],
    },
    {
      step: 2,
      icon: Zap,
      name: 'DeepFake Detector',
      desc: 'CrossEfficientViT model analyses each keyframe for GAN artifacts and AI generation signatures',
      tech: ['Hive AI', 'DeepSafe', 'CrossEfficientViT'],
    },
    {
      step: 3,
      icon: Eye,
      name: 'Source Hunter',
      desc: 'Perceptual hashing + Google Vision reverse image search finds the earliest known upload and EXIF metadata',
      tech: ['pHash', 'Google Vision', 'TinEye', 'ExifTool'],
    },
    {
      step: 4,
      icon: Globe,
      name: 'Context Analyser',
      desc: 'Whisper transcribes audio, EasyOCR reads on-screen text, vision LLM verifies location and temporal context',
      tech: ['Whisper', 'EasyOCR', 'Groq', 'Ollama'],
    },
    {
      step: 5,
      icon: GitMerge,
      name: 'Orchestrator',
      desc: 'LLM synthesises all agent findings into a final public verdict with credibility score and panic index',
      tech: ['LangGraph', 'Groq', 'LangSmith'],
    },
  ];

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-black mb-3">How Vigilens Works</h1>
          <p className="text-muted-foreground text-lg">
            A three-stage AI pipeline that analyses disaster videos for authenticity
          </p>
        </div>

        {/* Architecture Diagram */}
        <Card className="mb-10 bg-secondary/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Architecture Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs font-mono text-muted-foreground overflow-x-auto whitespace-pre">
{`Next.js Frontend
      │  POST /api/analyze
      ▼
FastAPI Backend
      │  LangGraph StateGraph
      ▼
  [Preprocess]
   ┌─────────────────────────────────┐
   │  Extract Keyframes + Audio      │
   └─────────────────────────────────┘
      │
      ├──────────────────────────────────┐
      │                                  │
      ▼                                  ▼                      ▼
[DeepFake Detector]          [Source Hunter]          [Context Analyser]
 Hive AI / DeepSafe          Google Vision             Whisper + EasyOCR
 CrossEfficientViT           TinEye / pHash            Vision LLM
      │                                  │                      │
      └──────────────────────────────────┘
                       │
                       ▼
               [Orchestrator]
               Groq / Ollama LLM
               LangSmith Tracing
                       │
                       ▼
               Final Verdict JSON`}
            </pre>
          </CardContent>
        </Card>

        {/* Pipeline Steps */}
        <div className="space-y-4">
          {pipeline.map((step) => (
            <Card key={step.step} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold shrink-0">
                    {step.step}
                  </div>
                  <step.icon className="h-5 w-5 text-accent" />
                  <CardTitle className="text-lg">{step.name}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-3">{step.desc}</p>
                <div className="flex flex-wrap gap-2">
                  {step.tech.map((t) => (
                    <Badge key={t} variant="secondary" className="text-xs">
                      {t}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Mode Guide */}
        <div className="mt-10 grid md:grid-cols-2 gap-4">
          <Card className="border-accent/30">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                🌐 Online Mode
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-1">
              <p>• LLM: Groq API (llama-3.3-70b)</p>
              <p>• DeepFake: Hive AI API</p>
              <p>• Transcription: OpenAI Whisper API</p>
              <p>• Reverse Search: Google Vision + TinEye</p>
              <p>• Requires API keys — see .env.local.example</p>
            </CardContent>
          </Card>
          <Card className="border-secondary">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                📦 Offline Mode
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-1">
              <p>• LLM: Ollama (llama3.3 local)</p>
              <p>• DeepFake: DeepSafe Docker</p>
              <p>• Transcription: Local Whisper model</p>
              <p>• OCR: EasyOCR (always local)</p>
              <p>• Requires 16GB RAM + NVIDIA GPU</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
