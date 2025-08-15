import React, { useEffect, useState } from 'react';
import logoUrl from '../image/mikeross.svg';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close menu on resize to md and above
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 768) setMenuOpen(false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  const navLinks = [
    { href: '#documents', label: 'Documents' },
    { href: '#cases', label: 'Cases' },
    { href: '#settings', label: 'Settings' }
  ];

  return (
    <header className={`sticky top-0 z-50 border-b border-gray-200 bg-white/70 backdrop-blur supports-[backdrop-filter]:backdrop-blur transition-all duration-300 ${scrolled ? 'shadow-sm' : ''}`}>
      <div className={`max-w-full mx-auto px-4 sm:px-6 flex items-center gap-3 transition-all duration-300 ${scrolled ? 'py-2' : 'py-3 sm:py-4'}`}>
        <div className={`relative flex items-center justify-center transition-all duration-300 ${scrolled ? 'h-8 w-8' : 'h-9 w-9 sm:h-10 sm:w-10'}`}>
          <div className="absolute inset-0 bg-white/40 backdrop-blur-lg blur-xl rounded-full" />
          <img
            src={logoUrl}
            alt="Logo"
            className={`rounded-full border-2 border-white/30 transition-all duration-300 ${scrolled ? 'h-7 w-7' : 'h-8 w-8 sm:h-9 sm:w-9'}`}
            style={{ filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.12)) brightness(1.05) saturate(1.15)' }}
          />
        </div>
        <h1 className={`font-semibold text-gray-900 transition-all duration-300 ${scrolled ? 'text-lg sm:text-xl' : 'text-xl sm:text-2xl'}`}>Mike Ross</h1>
        <div className="flex-1" />
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Primary">
          {navLinks.map(l => (
            <a
              key={l.href}
              href={l.href}
              className="px-4 py-2 rounded-md text-gray-700 text-sm font-medium hover:text-brand-500 hover:bg-brand-100/40 transition-colors"
            >
              {l.label}
            </a>
          ))}
        </nav>
        {/* Hamburger menu on far right for mobile */}
        <button
          type="button"
          className="md:hidden ml-2 inline-flex items-center justify-center h-10 w-10 rounded-full text-gray-600 hover:bg-white/70 focus:outline-none focus:ring-2 focus:ring-brand-300/50"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          onClick={() => setMenuOpen(o => !o)}
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            viewBox="0 0 24 24"
          >
            {menuOpen ? (
              <path d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path d="M3 6h18M3 12h18M3 18h18" />
            )}
          </svg>
        </button>
      </div>
      {/* Mobile Menu */}
      <div
        className={`md:hidden overflow-hidden transition-[max-height,opacity] duration-300 ease-out ${menuOpen ? 'max-h-60 opacity-100' : 'max-h-0 opacity-0'}`}
        aria-hidden={!menuOpen}
      >
        <nav className="px-4 pb-4 flex flex-col gap-1" aria-label="Mobile Primary">
          {navLinks.map(l => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setMenuOpen(false)}
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:text-brand-500 hover:bg-brand-100/70 active:bg-brand-100 transition-colors"
            >
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}