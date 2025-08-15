import React, { useState, useRef } from "react";
import { useCaseChat } from './chat/useCaseChat';
import { UploadArea } from './chat/UploadArea';
import Header from './Header';
import { ModuleBar } from './chat/ModuleBar';
import { ChatInput } from './chat/ChatInput';
import { Messages } from './chat/Messages';
import { apiJoin } from '../config/api';
import logoUrl from '../image/mikeross.svg';

export default function DocumentUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadedDocsMeta, setUploadedDocsMeta] = useState([]);
  const [caseType, setCaseType] = useState('General Legal');
  const fileInputRef = useRef(null);
  const { selectedModule, setSelectedModule, caseTitle, messages, input, setInput, loading, error, analysisRef, modules, sendMessage } = useCaseChat();
  const hasAssistant = messages.some(m=> m.role==='assistant');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFile = {
        id: Date.now(),
        file: e.dataTransfer.files[0],
      };
      setUploadedFiles((prev) => [...prev, newFile]);
    }
  };

  const handleFileSelect = async (e) => {
    if (e.target.files && e.target.files.length) {
      const fileList = Array.from(e.target.files);
      for (const file of fileList) {
        const newFile = { id: Date.now() + Math.random(), file };
        setUploadedFiles((prev) => [...prev, newFile]);
        await uploadDocument(file);
      }
      e.target.value = "";
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const uploadDocument = async (file) => {
    try {
      let active = localStorage.getItem('case_title');
      if (!active) {
        const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
        active = `case-guid-${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`;
        localStorage.setItem('case_title', active);
      }
      const formData = new FormData();
      formData.append('file', file);
      formData.append('case_title', active);
      formData.append('case_type', caseType);
      const res = await fetch(apiJoin('/upload-document'), { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      setUploadedDocsMeta(prev => [...prev, data]);
    } catch (e) {
      console.error('Document upload failed', e);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <>
  <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-brand-100/20 flex flex-col w-full">
        {/* Background Pattern */}
        <div className="fixed inset-0 bg-[url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23f1f5f9\' fill-opacity=\'0.4\'%3E%3Ccircle cx=\'30\' cy=\'30\' r=\'1\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] pointer-events-none"/>

        {/* Main Content */}
        <div className="flex-1 relative">
          <Header />

          <div className="max-w-full sm:max-w-2xl md:max-w-3xl lg:max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8 w-full">
            
            {/* Hero Section with Mike Ross */}
            <div className="mb-8 sm:mb-12">
              <div className="relative bg-white/80 backdrop-blur-sm border border-white/20 rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-xl shadow-brand-500/10">
                {/* Decorative Elements */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-brand-300/10 to-brand-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-emerald-500/10 to-brand-400/10 rounded-full blur-2xl" />
                
                <div className="relative flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6">
                  {/* Profile Image */}
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-brand-500 to-brand-400 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="relative w-20 h-20 sm:w-24 sm:h-24">
                      <img 
                        src={logoUrl} 
                        alt="Mike Ross" 
                        className="w-full h-full object-cover rounded-full border-4 border-white shadow-2xl" 
                      />
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-emerald-500 rounded-full border-2 border-white flex items-center justify-center">
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                      </div>
                    </div>
                  </div>

                  {/* Welcome Message */}
                  <div className="flex-1 text-center sm:text-left">
                    <div className="inline-flex items-center gap-2 mb-3">
                      <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-slate-800 via-brand-500 to-brand-400 bg-clip-text text-transparent">
                        Mike Ross
                      </h1>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                    
                    <p className="text-slate-600 leading-relaxed mb-4">
                      <span className="font-semibold text-brand-500">Your AI Legal Assistant</span> is ready to help you analyze documents, 
                      summarize contracts, strategize depositions, and research legal precedents with precision and expertise.
                    </p>

                    {/* Feature Pills */}
                    <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
                      {['Document Analysis', 'Contract Review', 'Case Strategy', 'Legal Research'].map((feature, idx) => (
                        <span 
                          key={feature}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-brand-100/50 text-brand-500 rounded-full text-xs font-small border border-brand-200 hover:bg-brand-100 transition-colors duration-200"
                        >
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Case Type Selection */}
            <div className="mb-6 sm:mb-8">
              
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Case Classification
                </label>
                <select
                  value={caseType}
                  onChange={e => setCaseType(e.target.value)}
                  className="w-full sm:w-auto px-4 py-3 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-300 focus:border-transparent shadow-sm hover:border-slate-300 transition-all duration-200"
                >
                  <option value="General Legal">General Legal</option>
                  <option value="Civil">Civil Law</option>
                  <option value="Criminal">Criminal Law</option>
                  <option value="Corporate">Corporate Law</option>
                  <option value="Family">Family Law</option>
                  <option value="Tax">Tax Law</option>
                </select>
            </div>

            {/* Upload Area */}
            {!hasAssistant && (
              <div className="mb-6 sm:mb-8">
                <UploadArea
                  dragActive={dragActive}
                  handleDrag={handleDrag}
                  handleDrop={handleDrop}
                  fileInputRef={fileInputRef}
                  handleFileSelect={handleFileSelect}
                  uploadedFiles={uploadedFiles}
                  removeFile={removeFile}
                />
              </div>
            )}

            {/* Hidden file input for later uploads */}
            {hasAssistant && (
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.txt,.md"
                multiple
              />
            )}

            {/* Uploaded Documents List */}
            {uploadedDocsMeta.length > 0 && (
              <div className="mb-6 sm:mb-8">
                <div className="bg-white/60 backdrop-blur-sm border border-white/20 rounded-xl p-4 sm:p-6 shadow-lg">
                  <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
                    <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Uploaded Documents ({uploadedDocsMeta.length})
                  </h3>
                  <div className="space-y-2">
                    {uploadedDocsMeta.map((doc, idx) => (
                      <div 
                        key={doc.document_id || doc.filename} 
                        className="group flex items-center justify-between p-3 bg-gradient-to-r from-emerald-50 to-brand-100 border border-emerald-200/50 rounded-lg hover:shadow-md transition-all duration-200"
                      >
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                            {idx + 1}
                          </div>
                          <span className="text-slate-700 font-medium truncate flex-1" title={doc.filename}>
                            {doc.filename}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
                            ✓ {doc.status || 'Uploaded'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Messages Area */}
            <div className="mb-8">
              <Messages messages={messages} loading={loading} analysisRef={analysisRef} />
              <div className="h-48" /> {/* Spacer for floating chat bar */}
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Floating Chat Bar */}
      <div className="fixed bottom-0 left-0 w-full bg-white/95 backdrop-blur-xl border-t border-white/20 shadow-2xl shadow-slate-900/10">
        {/* Decorative top border */}
  <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-brand-400/50 to-transparent" />
        
        <div className="max-w-full sm:max-w-2xl md:max-w-3xl lg:max-w-4xl mx-auto px-4 sm:px-6 py-3 sm:py-4 space-y-3">
          <ModuleBar 
            modules={modules} 
            selectedModule={selectedModule} 
            setSelectedModule={setSelectedModule} 
            caseTitle={caseTitle} 
          />
          <ChatInput
            selectedModule={selectedModule}
            loading={loading}
            input={input}
            setInput={setInput}
            sendMessage={sendMessage}
            error={error}
            hasAssistant={hasAssistant}
            onAddFile={() => { if(fileInputRef.current) { fileInputRef.current.click(); }}}
          />
        </div>
      </div>
    </>
  );
}