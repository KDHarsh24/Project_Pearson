import React from 'react';
import { Send, Plus } from 'lucide-react';
export function ChatInput({ selectedModule, loading, input, setInput, sendMessage, error, hasAssistant, onAddFile }) {
  const disabledSend = !selectedModule || loading || !input.trim();
  return (
    <div className="pt-2 pb-2">
      <div className="flex items-center gap-2 w-full px-2">
        {onAddFile && (
          <button
            type="button"
            onClick={()=> onAddFile()}
            disabled={loading}
            className={`h-9 w-9 flex items-center justify-center rounded-2xl border border-border bg-background transition-colors ${loading? 'opacity-50 cursor-not-allowed':'hover:bg-surface'}`}
            title="Add another file"
            style={{ alignSelf: 'center' }}
          >
            <Plus className="w-5 h-5 text-primary" />
          </button>
        )}
        <div className="flex-1 relative flex items-center">
          <textarea
            rows={1}
            value={input}
            disabled={!selectedModule || loading}
            onChange={(e)=> setInput(e.target.value)}
            onKeyDown={(e)=> { if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); } }}
            placeholder={selectedModule ? 'Type your message here…' : 'Select a module to start'}
            className="w-full resize-none rounded-2xl border border-border bg-surface focus:bg-background focus:border-primary focus:ring-2 focus:ring-accent/40 py-2 pl-4 pr-16 text-xs sm:text-sm md:text-base lg:text-lg leading-snug disabled:opacity-60 font-sans placeholder:italic placeholder:text-border"
            style={{ alignSelf: 'center' }}
          />
          <button
            onClick={sendMessage}
            disabled={disabledSend}
            className={`absolute right-0.5 md:right-2 top-1/2 -translate-y-1/2 h-8 md:h-9 w-8 md:w-9 flex items-center justify-center rounded-full transition-colors ${disabledSend ? 'bg-gray-200 text-gray-400':'bg-primary hover:bg-primary-700 text-white'}`}
            style={{ alignSelf: 'center' }}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
  {error && <p className="text-xs text-error mt-2">{error}</p>}
      {!selectedModule && <p className="text-[10px] text-gray-400 mt-2">Select a module to enable the chat.</p>}
      {loading && !hasAssistant && <p className="text-xs text-gray-500 mt-2">Waiting for response...</p>}
    </div>
  );
}
