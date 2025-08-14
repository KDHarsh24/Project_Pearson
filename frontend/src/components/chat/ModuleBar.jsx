import React from 'react';

export function ModuleBar({ modules, selectedModule, setSelectedModule, caseTitle }) {
  return (
    <div className="flex gap-2 p-2 overflow-x-auto">
      {modules.map(m => (
        <button key={m.id} onClick={()=> setSelectedModule(m.id)} className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${selectedModule===m.id ? 'bg-blue-600 text-white shadow':'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>{m.icon} {m.title}</button>
      ))}
      {caseTitle && <span className="ml-auto px-2 py-1 bg-gray-100 rounded text-[10px] font-mono border" title="Case ID">{caseTitle}</span>}
    </div>
  );
}
