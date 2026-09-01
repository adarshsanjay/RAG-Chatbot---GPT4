import React from 'react';
import { Truck, RotateCcw, Package, Sparkles } from 'lucide-react';

const ACTIONS = [
  { label: 'Track my order', query: 'How can I track my order?', icon: Truck },
  { label: 'Shipping info', query: 'What are the shipping times and delivery rates?', icon: Package },
  { label: 'Return policy', query: 'What is the return policy and return window?', icon: RotateCcw },
  { label: 'Recommend product', query: 'Can you recommend products sold in the store?', icon: Sparkles },
];

export default function QuickActions({ onSelectQuery, disabled }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 pt-1 scrollbar-none max-w-full">
      {ACTIONS.map((action, idx) => {
        const Icon = action.icon;
        return (
          <button
            key={idx}
            onClick={() => onSelectQuery(action.query)}
            disabled={disabled}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-zinc-900 text-zinc-300 hover:text-white hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 shadow-sm transition whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon className="w-3.5 h-3.5 text-blue-400" />
            <span>{action.label}</span>
          </button>
        );
      })}
    </div>
  );
}
