import { NextRequest, NextResponse } from 'next/server';
import { config } from '@/lib/config';
import { DEMO_VIDEOS } from '@/lib/demoData';

export async function POST(req: NextRequest) {
  const body = (await req.json()) as { videoUrl: string };
  const { videoUrl } = body;

  if (config.isDemo) {
    const demo = DEMO_VIDEOS.find((v) => v.url === videoUrl) ?? DEMO_VIDEOS[0];
    await new Promise((r) => setTimeout(r, 2000));
    return NextResponse.json(demo.precomputedResult);
  }

  try {
    const response = await fetch(`${config.backendUrl}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_url: videoUrl }),
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Backend analysis failed' }, { status: 502 });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 503 });
  }
}
