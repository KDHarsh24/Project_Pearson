import React from 'react';

// Makes ModuleBar a single horizontal scrollable line, with all modules and case title in one row, scrolling left if overflow
export function ModuleBar({ modules = [], selectedModule, setSelectedModule, caseTitle }) {
  return (
    <div className="p-1 bg-transparent">
      <div className="flex flex-row items-center gap-2 w-full overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {modules.map(m => {
          const active = selectedModule === m.id;
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => setSelectedModule(m.id)}
              className={`flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:ring-offset-0
                ${active ? 'bg-blue-600 text-white shadow' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              aria-pressed={active}
            >
              <span className="truncate">{m.title}</span>
            </button>
          );
        })}
        {caseTitle && (
          <span className="ml-4 text-xs font-semibold text-gray-600 px-3 py-1.5 whitespace-nowrap">{caseTitle}</span>
        )}
      </div>
    </div>
  );
}
