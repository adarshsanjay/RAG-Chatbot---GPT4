import React from 'react';
import { FileText, Bookmark } from 'lucide-react';

export default function SourceCitations({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-zinc-800">
      <div className="flex items-center space-x-1.5 mb-2 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
        <Bookmark className="w-3.5 h-3.5 text-blue-400" />
        <span>Verified Citations ({sources.length})</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, idx) => (
          <div
            key={idx}
            className="group relative flex items-center space-x-2 px-2.5 py-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 hover:border-zinc-600 text-xs transition text-zinc-200"
          >
            <FileText className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <div className="truncate">
              <span className="font-medium text-zinc-200 group-hover:text-blue-300">{src.filename}</span>
              <span className="text-zinc-400 text-[11px] ml-1.5 font-mono">Page {src.page}</span>
            </div>
            {src.snippet && (
              <div className="hidden group-hover:block absolute bottom-full left-0 mb-1 w-64 p-2 bg-zinc-950 text-zinc-200 border border-zinc-800 text-[11px] rounded shadow-xl z-20 pointer-events-none">
                "{src.snippet}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
