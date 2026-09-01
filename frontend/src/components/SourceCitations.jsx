import React from 'react';
import { FileText, Bookmark } from 'lucide-react';

export default function SourceCitations({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-slate-200/80">
      <div className="flex items-center space-x-1.5 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        <Bookmark className="w-3.5 h-3.5 text-blue-600" />
        <span>Verified Citations ({sources.length})</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, idx) => (
          <div
            key={idx}
            className="group relative flex items-center space-x-2 px-2.5 py-1.5 rounded-md bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-xs transition"
          >
            <FileText className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
            <div className="truncate">
              <span className="font-medium text-slate-800 group-hover:text-blue-700">{src.filename}</span>
              <span className="text-slate-500 text-[11px] ml-1.5 font-mono">Page {src.page}</span>
            </div>
            {src.snippet && (
              <div className="hidden group-hover:block absolute bottom-full left-0 mb-1 w-64 p-2 bg-slate-900 text-white text-[11px] rounded shadow-xl z-20 pointer-events-none">
                "{src.snippet}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
