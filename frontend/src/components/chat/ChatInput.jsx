import React from 'react';
import { Send, Plus } from 'lucide-react';
export function ChatInput({ selectedModule, loading, input, setInput, sendMessage, error, hasAssistant, onAddFile }) {
  const disabledSend = !selectedModule || loading || !input.trim();
  return (
    <div className="pt-3 pb-3">
      <div className="relative">
        {onAddFile && (
          <button
            type="button"
            onClick={()=> onAddFile()}
            disabled={loading}
            className={`absolute left-2 bottom-2 h-9 w-9 flex items-center justify-center rounded-full border bg-white transition-colors ${loading? 'opacity-50 cursor-not-allowed':'hover:bg-gray-100'}`}
            title="Add another file"
          >
            <Plus className="w-5 h-5 text-gray-600" />
          </button>
        )}
        <textarea
          rows={1}
          value={input}
          disabled={!selectedModule || loading}
          onChange={(e)=> setInput(e.target.value)}
          onKeyDown={(e)=> { if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); } }}
          placeholder={selectedModule ? 'Ask something about your documents...' : 'Select a module to start'}
          className="w-full resize-none rounded-2xl border border-gray-300 bg-gray-50 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 py-3 pl-14 pr-14 text-sm leading-snug disabled:opacity-60"
        />
        <button
          onClick={sendMessage}
          disabled={disabledSend}
          className={`absolute right-2 bottom-2 h-9 w-9 flex items-center justify-center rounded-full transition-colors ${disabledSend ? 'bg-gray-200 text-gray-400':'bg-blue-600 hover:bg-blue-700 text-white'}`}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
      {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
      {!selectedModule && <p className="text-[10px] text-gray-400 mt-2">Select a module to enable the chat.</p>}
      {loading && !hasAssistant && <p className="text-xs text-gray-500 mt-2">Waiting for response...</p>}
    </div>
  );
}
