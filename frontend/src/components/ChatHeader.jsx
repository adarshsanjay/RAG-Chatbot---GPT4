import React from 'react';
import { ShoppingBag, FileText, Trash2, RefreshCw } from 'lucide-react';

export default function ChatHeader({ onClearChat, onToggleSidebar, documentCount, isOnline }) {
  return (
    <header className="bg-white border-b border-slate-200 px-4 py-3 sm:px-6 shadow-sm sticky top-0 z-10">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        
        {/* Left: Branding & Status */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShoppingBag className="w-5.5 h-5.5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold text-slate-900 leading-snug">E-Commerce Assistant</h1>
              <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`}></span>
                <span>{isOnline ? 'Online' : 'Offline'}</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Ask about products, orders, shipping, and returns.
            </p>
          </div>
        </div>

        {/* Right: Actions & KB Drawer Toggle */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <button
            onClick={onToggleSidebar}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition border border-slate-200"
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
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 transition border border-transparent hover:border-red-200"
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
