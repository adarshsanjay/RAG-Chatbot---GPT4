import React from 'react';
import { ShoppingBag, FileText, Trash2, AlertTriangle } from 'lucide-react';

export default function ChatHeader({ onClearChat, onToggleSidebar, documentCount, isOnline, isApiConfigured }) {
  return (
    <header className="bg-black border-b border-zinc-800 px-4 py-3 sm:px-6 shadow-sm sticky top-0 z-10">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        
        {/* Left: Branding & Status */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShoppingBag className="w-5.5 h-5.5" />
          </div>
          <div>
            <div className="flex items-center space-x-2 flex-wrap gap-y-1">
              <h1 className="text-base font-bold text-white leading-snug">E-Commerce Assistant</h1>
              <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`}></span>
                <span>{isOnline ? 'Online' : 'Offline'}</span>
              </span>
              {!isApiConfigured && (
                <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-300">
                  <AlertTriangle className="w-3 h-3" />
                  <span>API Key Missing</span>
                </span>
              )}
            </div>
            <p className="text-xs text-zinc-400 hidden sm:block">
              Ask about products, orders, shipping, and returns.
            </p>
          </div>
        </div>

        {/* Right: Actions & KB Drawer Toggle */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <button
            onClick={onToggleSidebar}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-900 hover:bg-zinc-800 text-zinc-200 transition border border-zinc-700"
            title="Manage Knowledge Base Documents"
          >
            <FileText className="w-4 h-4 text-blue-600" />
            <span className="hidden sm:inline">Knowledge Base</span>
            {documentCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 text-[10px] font-bold bg-blue-600 text-white rounded-full">
                {documentCount}
              </span>
            )}
          </button>

          <button
            onClick={onClearChat}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-red-400 hover:bg-zinc-900 transition border border-transparent hover:border-zinc-700"
            title="Clear Chat Conversation"
          >
            <Trash2 className="w-4 h-4" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>

      </div>
    </header>
  );
}
