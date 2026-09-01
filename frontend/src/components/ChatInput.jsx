import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import QuickActions from './QuickActions';

export default function ChatInput({ onSendMessage, isLoading, onSelectQuickQuery }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-white border-t border-slate-200 px-4 py-3 sm:px-6 sticky bottom-0 z-10 shadow-lg">
      <div className="max-w-4xl mx-auto space-y-2">
        
        {/* Quick Action Presets */}
        <QuickActions
          onSelectQuery={(query) => {
            if (!isLoading) onSendMessage(query);
          }}
          disabled={isLoading}
        />

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <div className="relative flex-grow">
            <textarea
              rows="1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about products, orders, shipping, or returns..."
              disabled={isLoading}
              className="w-full resize-none rounded-xl border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none transition disabled:bg-slate-100 disabled:cursor-not-allowed shadow-inner"
            />
          </div>

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-95 text-white flex items-center justify-center shadow-md shadow-blue-500/20 transition disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            title="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-4.5 h-4.5 ml-0.5" />
            )}
          </button>
        </form>

        {/* Disclaimer */}
        <p className="text-[11px] text-center text-slate-400">
          Responses are generated from uploaded knowledge-base documents. Please verify important details.
        </p>

      </div>
    </div>
  );
}
