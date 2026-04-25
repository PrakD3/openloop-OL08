'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import { Shield, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ModeToggle } from './ModeToggle';
import { cn } from '@/lib/utils';
import { useState } from 'react';

export function Navbar() {
  const { t, i18n } = useTranslation();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { href: '/', label: t('nav.home') },
    { href: '/analysis', label: t('nav.analysis') },
    { href: '/incidents', label: t('nav.incidents') },
    { href: '/bulletin', label: t('nav.bulletin') },
    { href: '/how-it-works', label: t('nav.howItWorks') },
  ];

  const languages = ['en', 'hi', 'ta', 'ar', 'es'];

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-accent" />
            <span className="text-lg font-bold">Vigilens</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'text-sm font-medium transition-colors hover:text-foreground',
                  pathname === link.href ? 'text-foreground' : 'text-muted-foreground'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <select
              value={i18n.language}
              onChange={(e) => i18n.changeLanguage(e.target.value)}
              className="text-xs bg-background border border-input rounded px-2 py-1"
            >
              {languages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang.toUpperCase()}
                </option>
              ))}
            </select>
            <ModeToggle />
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden border-t py-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'block px-3 py-2 text-sm rounded-md',
                  pathname === link.href
                    ? 'bg-accent/10 text-accent font-medium'
                    : 'text-muted-foreground hover:bg-secondary'
                )}
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
