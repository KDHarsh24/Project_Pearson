import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export function Messages({ messages, loading, analysisRef }) {
  const hasAssistant = messages.some(m=> m.role==='assistant');
  const endRef = useRef(null);
  useEffect(()=>{
    // If inner container scroll existed previously, still try, else fallback to window scroll
    if (analysisRef?.current && analysisRef.current.scrollHeight > 0) {
      try { analysisRef.current.scrollTo({ top: analysisRef.current.scrollHeight, behavior: 'smooth' }); } catch {}
    }
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, loading, analysisRef]);
  if (!hasAssistant) return null;
  return (
    <div ref={analysisRef} className="mt-4 p-2 space-y-6">
      {messages.map((m, idx) => (
          <div key={idx} className={`flex flex-col ${m.role==='user' ? 'items-end' : 'items-start'}`}>
          <div className="flex items-center gap-2 mb-1">
            {m.role==='assistant' && (
              <img src={require('../../image/mikeross.webp')} alt="Mike Ross" className="h-5 w-5 rounded-full border border-blue-200 shadow" />
            )}
            <span className={`text-[10px] ${m.role==='user' ? 'text-blue-500':'text-blue-700 font-semibold'}`}>{m.role==='user' ? 'You':'Mike Ross'}</span>
          </div>
            <div className={`rounded-lg px-4 py-3 text-sm leading-relaxed shadow-sm prose prose-sm max-w-full ${m.role==='user' ? 'bg-blue-600 text-white':'bg-gray-100'}`}
              style={m.role==='user' ? {borderTopRightRadius: 0, minWidth: '120px'} : {borderTopLeftRadius: 0}}>
            {m.role === 'assistant' ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown> : <span className="whitespace-pre-wrap">{m.content}</span>}
          </div>
        </div>
      ))}
      {loading && <p className="text-xs text-gray-500">Thinking...</p>}
      <div ref={endRef} />
    </div>
  );
}
