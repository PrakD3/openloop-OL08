import Link from 'next/link';
import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t bg-background mt-auto">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-accent" />
            <span className="font-semibold">Vigilens</span>
            <span className="text-muted-foreground text-sm">— Disaster Misinformation Detection</span>
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/how-it-works" className="hover:text-foreground transition-colors">
              How It Works
            </Link>
            <Link href="/incidents" className="hover:text-foreground transition-colors">
              Incidents
            </Link>
            <Link href="/bulletin" className="hover:text-foreground transition-colors">
              Bulletin
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              GitHub
            </a>
          </div>
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} Vigilens. Open source for disaster response.
          </p>
        </div>
      </div>
    </footer>
  );
}
