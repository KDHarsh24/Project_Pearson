import React, { useEffect, useState } from 'react';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  return (
    <div className={`sticky top-0 z-50 border-b border-gray-200 bg-white/70 backdrop-blur transition-all duration-300 ${scrolled ? 'shadow-sm' : ''}`}>
      <div className={`max-w-full mx-auto px-6 flex items-center gap-3 transition-all duration-300 ${scrolled ? 'py-2' : 'py-4'}`}>
        <div className={`relative flex items-center justify-center transition-all duration-300 ${scrolled ? 'h-8 w-8' : 'h-10 w-10'}`}>
          <div className="absolute inset-0 bg-white/40 backdrop-blur-lg blur-xl" />
          <img
            src={require('../image/mikeross.webp')}
            alt="Logo"
            className={`rounded-full border-2 border-white/30 transition-all duration-300 ${scrolled ? 'h-7 w-7' : 'h-9 w-9'}`}
            style={{ filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.12)) brightness(1.1) saturate(1.2)' }}
          />
        </div>
        <h1 className={`font-semibold text-gray-900 transition-all duration-300 ${scrolled ? 'text-xl' : 'text-2xl'}`}>Mike Ross</h1>
        <div className="flex-1" />
        <div className="flex items-center gap-2">
          <a href="#documents" className="px-4 py-1.5 hover:text-blue-700 text-gray-700 text-sm font-medium transition">Documents</a>
          <a href="#cases" className="px-4 py-1.5 hover:text-blue-700 text-gray-700 text-sm font-medium transition">Cases</a>
          <a href="#settings" className="px-4 py-1.5 hover:text-blue-700 text-gray-700 text-sm font-medium transition">Settings</a>
        </div>
      </div>
    </div>
  );
}