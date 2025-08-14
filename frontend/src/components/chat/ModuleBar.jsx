import React from 'react';

// Keeps original color scheme but adds responsiveness:
// - Mobile: grid (2 columns) so all modules visible without horizontal scroll
// - Medium+: flex wrap row style like original
// - Case ID shown at end (takes full row on very small screens)
export function ModuleBar({ modules = [], selectedModule, setSelectedModule, caseTitle }) {
  return (
    <div className="p-2 bg-transparent">
      <div className="grid grid-cols-2 gap-2 md:flex md:flex-wrap md:gap-2">
        {modules.map(m => {
          const active = selectedModule === m.id;
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => setSelectedModule(m.id)}
              className={`flex items-center justify-center md:justify-start gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:ring-offset-0
                ${active ? 'bg-blue-600 text-white shadow' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              aria-pressed={active}
            >
              <span className="truncate">{m.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
