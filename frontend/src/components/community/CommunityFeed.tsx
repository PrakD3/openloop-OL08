'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ThumbsUp, ThumbsDown, MessageCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MOCK_COMMUNITY_POSTS } from '@/lib/demoData';
import type { CommunityPost } from '@/types';

export function CommunityFeed() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState<CommunityPost[]>(MOCK_COMMUNITY_POSTS);

  const handleVote = (postId: string, vote: 'up' | 'down') => {
    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const wasVoted = p.userVote === vote;
        return {
          ...p,
          votes: wasVoted ? p.votes - 1 : p.userVote ? p.votes : p.votes + 1,
          userVote: wasVoted ? null : vote,
        };
      })
    );
  };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
        Community Reports
      </h3>
      {posts.map((post) => (
        <Card key={post.id} className="animate-fade-in-up">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold shrink-0">
                {post.avatar}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">@{post.author}</span>
                  <Badge variant={post.verdict as 'real' | 'misleading' | 'unverified'} className="text-xs">
                    {t(`verdict.${post.verdict}`)}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{post.content}</p>
                <div className="flex items-center gap-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 gap-1"
                    onClick={() => handleVote(post.id, 'up')}
                  >
                    <ThumbsUp className="h-3 w-3" />
                    <span className="text-xs">{post.votes}</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => handleVote(post.id, 'down')}
                  >
                    <ThumbsDown className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 px-2 gap-1">
                    <MessageCircle className="h-3 w-3" />
                    <span className="text-xs">{post.replies}</span>
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
