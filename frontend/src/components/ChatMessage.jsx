import React from 'react';
import { Bot, User, Tag } from 'lucide-react';
import SourceCitations from './SourceCitations';

const INTENT_LABELS = {
  faq: 'FAQ & General',
  product_question: 'Product Inquiry',
  product_recommendation: 'Product Recommendation',
  review_summary: 'Review Summary',
  order_shipping: 'Order & Shipping',
  returns_refunds: 'Returns & Refunds',
  general_support: 'Customer Support',
  unknown: 'General Inquiry'
};

function renderFormattedContent(content) {
  if (!content) return null;

  // 1. Remove any remaining internal <think>...</think> tags if present
  let clean = content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();

  // 2. Split lines and process markdown-style bold and bullet points
  const lines = clean.split('\n');

  return lines.map((line, lineIdx) => {
    // Check if line is a bullet item (* or -)
    const isBullet = /^\s*[\*\-]\s+/.test(line);
    const lineText = isBullet ? line.replace(/^\s*[\*\-]\s+/, '') : line;

    // Parse bold text **text** into <strong> components
    const parts = lineText.split(/(\*\*.*?\*\*)/g);

    const formattedLine = parts.map((part, partIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={partIdx} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
      }
      return part;
    });

    return (
      <div key={lineIdx} className={`${isBullet ? 'flex items-start space-x-2 my-1 pl-2' : line.trim() === '' ? 'h-2' : 'my-0.5'}`}>
        {isBullet && <span className="text-blue-600 font-bold leading-relaxed flex-shrink-0">•</span>}
        <span className="leading-relaxed">{formattedLine}</span>
      </div>
    );
  });
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[88%] sm:max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse space-x-2' : 'flex-row space-x-3'}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white shadow-sm ${
          isUser ? 'bg-blue-600' : 'bg-slate-800'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4.5 h-4.5 text-blue-400" />}
        </div>

        {/* Message Bubble Container */}
        <div>
          <div className={`rounded-2xl px-4 py-3 text-sm shadow-sm ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-none'
              : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-none'
          }`}>
            
            {/* Main Content */}
            <div className="leading-relaxed">
              {renderFormattedContent(message.content)}
            </div>

            {/* Source Citations for Assistant */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <SourceCitations sources={message.sources} />
            )}

          </div>

          {/* Sub-Metadata: Intent Chip & Timestamp */}
          <div className={`flex items-center space-x-2 mt-1.5 px-1 text-[11px] text-slate-400 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <span>{message.timestamp || 'Just now'}</span>
            
            {!isUser && message.intent && (
              <>
                <span>•</span>
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md font-medium bg-blue-50 text-blue-700 border border-blue-200/60">
                  <Tag className="w-3 h-3 text-blue-500" />
                  <span>Intent: {INTENT_LABELS[message.intent] || message.intent}</span>
                </span>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
