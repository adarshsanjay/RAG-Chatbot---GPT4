import React, { useState } from 'react';
import { FileUp, FileText, CheckCircle2, AlertCircle, Trash2, X, RefreshCw, Database } from 'lucide-react';
import { uploadDocument, resetIndex } from '../services/api';

export default function DocumentUpload({ isOpen, onClose, documents, onDocumentsUpdated }) {
  const [uploading, setUploading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMsg('Only PDF files are supported.');
      return;
    }

    setUploading(true);
    setStatusMsg(null);
    setErrorMsg(null);

    try {
      const res = await uploadDocument(file);
      setStatusMsg(res.message);
      if (onDocumentsUpdated) onDocumentsUpdated();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to upload file.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleResetIndex = async () => {
    if (!window.confirm('Are you sure you want to reset the knowledge base index? This will clear custom uploaded documents and re-index the default KB.')) {
      return;
    }

    setResetting(true);
    setStatusMsg(null);
    setErrorMsg(null);

    try {
      const res = await resetIndex();
      setStatusMsg(res.message);
      if (onDocumentsUpdated) onDocumentsUpdated();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to reset index.');
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
        
        {/* Header */}
        <div>
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-blue-600" />
              <h2 className="font-bold text-slate-800 text-base">Knowledge Base Manager</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 space-y-4">
            
            {/* Status & Error Alerts */}
            {statusMsg && (
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 flex items-start space-x-2 text-xs text-emerald-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>{statusMsg}</span>
              </div>
            )}

            {errorMsg && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start space-x-2 text-xs text-red-800">
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Upload Drag/Drop Box */}
            <div className="border-2 border-dashed border-blue-200 hover:border-blue-500 rounded-xl p-6 text-center bg-blue-50/40 transition">
              <FileUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">Upload New PDF Document</p>
              <p className="text-xs text-slate-500 mt-1 mb-3">Add product specs, policy updates, or extra store FAQs.</p>
              
              <label className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow cursor-pointer transition">
                <FileUp className="w-4 h-4" />
                <span>{uploading ? 'Processing PDF...' : 'Select PDF File'}</span>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
            </div>

            {/* Document Listing */}
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Indexed Documents ({documents.length})
              </h3>

              {documents.length === 0 ? (
                <p className="text-xs text-slate-400 italic py-3 text-center border border-dashed border-slate-200 rounded-lg">
                  No documents indexed yet.
                </p>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {documents.map((doc, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-3 overflow-hidden">
                        <div className="p-2 rounded bg-blue-100 text-blue-700">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div className="truncate">
                          <p className="text-xs font-semibold text-slate-800 truncate">{doc.filename}</p>
                          <p className="text-[11px] text-slate-500">
                            {doc.total_pages} pages • {doc.total_chunks} vector chunks
                          </p>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold">
                        Indexed
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Footer: Reset Button */}
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <button
            onClick={handleResetIndex}
            disabled={resetting}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-white hover:bg-red-50 text-red-600 border border-red-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${resetting ? 'animate-spin' : ''}`} />
            <span>{resetting ? 'Resetting Index...' : 'Reset Vector Index to Default'}</span>
          </button>
        </div>

      </div>
    </div>
  );
}
