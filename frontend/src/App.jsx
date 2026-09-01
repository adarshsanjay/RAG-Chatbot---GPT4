import React, { useState, useEffect, useRef } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DocumentUpload from './components/DocumentUpload';
import { fetchHealth, fetchDocuments, sendChatMessage } from './services/api';
import { Bot, Sparkles, ShoppingBag, ShieldCheck, AlertCircle } from 'lucide-react';

const INITIAL_WELCOME_MESSAGE = {
  role: 'assistant',
  content: `Hello! 👋 I'm your AI E-Commerce Assistant powered by Retrieval-Augmented Generation (RAG).

I can help you with:
• **Products**: Specifications, availability, warranty, size charts, authenticity.
• **Orders**: Placing orders, modifications, auto-cancellation rules, order tracking.
• **Shipping & Delivery**: Rates, timelines, courier details.
• **Returns & Refunds**: Return windows, refund processing times, return conditions.

How can I assist you today?`,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  intent: 'faq',
  sources: []
};

export default function App() {
  const [messages, setMessages] = useState([INITIAL_WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [isApiConfigured, setIsApiConfigured] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  
  const chatEndRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Initial load: Check health & indexed documents
  const loadInitialData = async () => {
    try {
      const health = await fetchHealth();
      setIsOnline(health.status === 'ok');
      setIsApiConfigured(health.groq_api_configured === true);
      const docsRes = await fetchDocuments();
      setDocuments(docsRes.documents || []);
    } catch (err) {
      console.error('Failed to load initial backend status:', err);
      setIsOnline(false);
      setIsApiConfigured(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleSendMessage = async (userText) => {
    if (!userText.trim()) return;

    const userTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = {
      role: 'user',
      content: userText,
      timestamp: userTimestamp
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const chatHistory = messages.filter(m => m.role === 'user' || m.role === 'assistant');
      const res = await sendChatMessage(userText, chatHistory);

      const assistantMsg = {
        role: 'assistant',
        content: res.answer,
        intent: res.intent,
        sources: res.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Error calling chat endpoint:', err);
      setErrorMessage(err.message || 'Unable to connect to assistant service.');
      
      const errorMsg = {
        role: 'assistant',
        content: `⚠️ **Error**: ${err.message || 'Failed to process response from server.'}\n\nPlease check that the backend server is running at http://localhost:8000 and try again.`,
        intent: 'unknown',
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([INITIAL_WELCOME_MESSAGE]);
    setErrorMessage(null);
  };

  return (
    <div className="flex flex-col h-screen bg-black text-slate-100 overflow-hidden">
      
      {/* Header */}
      <ChatHeader
        onClearChat={handleClearChat}
        onToggleSidebar={() => setIsSidebarOpen(true)}
        documentCount={documents.length}
        isOnline={isOnline}
        isApiConfigured={isApiConfigured}
      />

      {/* Main Chat View */}
      <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        <div className="max-w-4xl mx-auto space-y-4">
          
          {/* API Key Warning Banner */}
          {!isApiConfigured && (
            <div className="bg-amber-50 border border-amber-300 rounded-2xl p-4 mb-4 flex items-start space-x-3 shadow-sm">
              <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold text-amber-800">Groq API Key Not Configured</p>
                <p className="text-xs text-amber-700 mt-0.5">
                  The backend cannot reach the Groq LLM. Please add your <code className="bg-amber-100 px-1 rounded font-mono">GROQ_API_KEY</code> to the{' '}
                  <code className="bg-amber-100 px-1 rounded font-mono">backend/.env</code> file and restart the server.
                </p>
              </div>
            </div>
          )}

          {/* Welcome Banner Card */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-5 text-white shadow-md mb-6">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-amber-300 animate-spin" style={{ animationDuration: '4s' }} />
                  <h2 className="text-lg font-bold">Smart Knowledge Retrieval Active</h2>
                </div>
                <p className="text-xs text-blue-100 max-w-xl">
                  Answers are dynamically synthesized using PyMuPDF context extraction, local FAISS vector search (`all-MiniLM-L6-v2`), and Groq LLM logic.
                </p>
              </div>
              <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white/10 text-xs font-medium border border-white/20 backdrop-blur-sm">
                <ShieldCheck className="w-4 h-4 text-emerald-300" />
                <span>Zero Fact Hallucination Mode</span>
              </div>
            </div>
          </div>

          {/* Messages Stream */}
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}

          {/* Typing / Loading Indicator */}
          {isLoading && (
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-white shadow-sm border border-zinc-700">
                <Bot className="w-4.5 h-4.5 text-blue-400" />
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm flex items-center space-x-1.5 text-zinc-300">
                <span className="text-xs font-medium text-zinc-400 mr-1">Synthesizing answer...</span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-typing-1"></span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-typing-2"></span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-typing-3"></span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Fixed Bottom Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />

      {/* Knowledge Base Modal / Drawer */}
      <DocumentUpload
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        documents={documents}
        onDocumentsUpdated={loadInitialData}
      />

    </div>
  );
}
