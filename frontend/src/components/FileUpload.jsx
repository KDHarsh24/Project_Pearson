import React, { useState, useRef } from "react";
import { useCaseChat } from './chat/useCaseChat';
import { UploadArea } from './chat/UploadArea';
import Header from './Header';
import { ModuleBar } from './chat/ModuleBar';
import { ChatInput } from './chat/ChatInput';
import { Messages } from './chat/Messages';
import { apiJoin } from '../config/api';

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
      e.target.value = ""; // reset
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
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main Content */}
      <div className="flex-1">
      <Header />

        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Mike Ross intro bubble */}
          <div className="mb-6">
            <div className="flex items-start gap-3">
              <div className="relative h-9 w-9 flex items-center justify-center">
                <img src={require('../image/mikeross.webp')} alt="Mike Ross" className="h-8 w-8 rounded-full border-2 border-blue-200 shadow" />
              </div>
              <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 text-sm text-blue-900 shadow-sm max-w-xl">
                <span className="font-semibold text-blue-700">Hi, I'm Mike Ross.</span><br/>
                I can analyze your legal documents, summarize contracts, strategize depositions, and research precedents. Upload your files and select a module below to get started!
              </div>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Case Type</label>
            <select
              value={caseType}
              onChange={e=>setCaseType(e.target.value)}
              className="border rounded px-3 py-2 text-sm focus:outline-none focus:ring focus:border-blue-400"
            >
                <option className="hover:bg-blue-50">General Legal</option>
                <option className="hover:bg-blue-50">Civil</option>
                <option className="hover:bg-blue-50">Criminal</option>
                <option className="hover:bg-blue-50">Corporate</option>
                <option className="hover:bg-blue-50">Family</option>
                <option className="hover:bg-blue-50">Tax</option>
            </select>
              <span className="pointer-events-none absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-400">
                <svg width="20" height="20" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M6 9l6 6 6-6"/></svg>
              </span>
          </div>
          {!hasAssistant && (
            <UploadArea
              dragActive={dragActive}
              handleDrag={handleDrag}
              handleDrop={handleDrop}
              fileInputRef={fileInputRef}
              handleFileSelect={handleFileSelect}
              uploadedFiles={uploadedFiles}
              removeFile={removeFile}
            />
          )}
          {hasAssistant && (
            // Hidden file input for plus button after initial upload area is removed
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.txt,.md"
              multiple
            />
          )}
          {uploadedDocsMeta.length > 0 && (
            <div className="mt-4 text-xs text-gray-600 space-y-1">
              {uploadedDocsMeta.map(doc => (
                <div key={doc.document_id || doc.filename} className="flex items-center justify-between border rounded px-2 py-1">
                  <span className="truncate mr-2" title={doc.filename}>{doc.filename}</span>
                  <span className="text-green-600">{doc.status || 'uploaded'}</span>
                </div>
              ))}
            </div>
          )}
          <div className="mt-4">
            <Messages messages={messages} loading={loading} analysisRef={analysisRef} />
            <div className="h-48" /> {/* spacer so last messages not hidden behind floating bar */}
          </div>
        </div>
      </div>
    </div>
    {/* Floating bottom chat bar */}
    <div className="fixed bottom-0 left-0 w-full bg-white/90 backdrop-blur border-t border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-2 space-y-1">
        <ModuleBar modules={modules} selectedModule={selectedModule} setSelectedModule={setSelectedModule} caseTitle={caseTitle} />
        <ChatInput
          selectedModule={selectedModule}
          loading={loading}
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
          error={error}
          hasAssistant={hasAssistant}
          onAddFile={()=> { if(fileInputRef.current){ fileInputRef.current.click(); }}}
        />
      </div>
    </div>
    </>
  );
}