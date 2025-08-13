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
        <div key={idx} className="flex flex-col">
          <div className={`text-[10px] mb-1 ${m.role==='user' ? 'text-blue-500':'text-green-600'}`}>{m.role==='user' ? 'You':'Assistant'}</div>
          <div className={`rounded-lg px-4 py-3 text-sm leading-relaxed shadow-sm prose prose-sm max-w-full ${m.role==='user' ? 'bg-blue-600 text-white w-[calc(80%)]':'bg-gray-100'}`}> 
            {m.role === 'assistant' ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown> : <span className="whitespace-pre-wrap">{m.content}</span>}
          </div>
        </div>
      ))}
      {loading && <p className="text-xs text-gray-500">Thinking...</p>}
      <div ref={endRef} />
    </div>
  );
}
