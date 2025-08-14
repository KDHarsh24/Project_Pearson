import React, { useState, useRef, useEffect } from "react";
import { Upload, X, Plus, FileText } from "lucide-react";

// Chart component using Chart.js
const ChartComponent = ({ chartData }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !chartData) return;

    // Destroy previous chart if it exists
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // Load Chart.js dynamically
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
    script.onload = () => {
      const ctx = canvasRef.current.getContext('2d');
      chartRef.current = new window.Chart(ctx, {
        type: chartData.type,
        data: chartData.data,
        options: {
          ...chartData.options,
          maintainAspectRatio: false,
          responsive: true,
        }
      });
    };

    if (!document.querySelector('script[src*="chart.min.js"]')) {
      document.head.appendChild(script);
    } else {
      // Chart.js already loaded
      const ctx = canvasRef.current.getContext('2d');
      chartRef.current = new window.Chart(ctx, {
        type: chartData.type,
        data: chartData.data,
        options: {
          ...chartData.options,
          maintainAspectRatio: false,
          responsive: true,
        }
      });
    }

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [chartData]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">{chartData.title}</h3>
      <div style={{ position: 'relative', height: '300px' }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
};

// Enhanced Messages component with chart support
const Messages = ({ messages, loading, analysisRef }) => {
  const formatAnalysisText = (text) => {
    return text.split('\n').map((line, index) => {
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-xl font-bold mt-6 mb-3 text-gray-800">{line.replace('## ', '')}</h2>;
      } else if (line.startsWith('### ')) {
        return <h3 key={index} className="text-lg font-semibold mt-4 mb-2 text-gray-700">{line.replace('### ', '')}</h3>;
      } else if (line.startsWith('*') && line.includes(':')) {
        return <h4 key={index} className="font-medium mt-3 mb-1 text-gray-600">{line.replace(/^\*/, '').replace(':', ':')}</h4>;
      } else if (line.startsWith('- **')) {
        return <p key={index} className="ml-4 mb-1 text-gray-600">{line}</p>;
      } else if (line.startsWith('- *')) {
        return <p key={index} className="ml-4 mb-1 text-gray-500 text-sm">{line}</p>;
      } else if (line.trim()) {
        return <p key={index} className="mb-2 text-gray-600">{line}</p>;
      }
      return <br key={index} />;
    });
  };

  const renderMessage = (message) => {
    // Check if message contains structured response with charts
    if (message.role === 'assistant' && message.content) {
      let parsedContent;
      try {
        // Try to parse as JSON (structured response)
        parsedContent = JSON.parse(message.content);
      } catch {
        // If not JSON, treat as regular text
        parsedContent = null;
      }

      // If it's a structured response with charts
      if (parsedContent && parsedContent.has_charts && parsedContent.charts) {
        return (
          <div className="space-y-6">
            {/* Response Header */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  {parsedContent.case_title || 'Analysis Results'}
                </h2>
                {parsedContent.status && (
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    {parsedContent.status}
                  </span>
                )}
              </div>
              {parsedContent.case_id && (
                <p className="text-gray-600 mb-2">
                  <strong>Case ID:</strong> {parsedContent.case_id}
                </p>
              )}
              {parsedContent.model_type && (
                <p className="text-gray-600 mb-2">
                  <strong>Model:</strong> {parsedContent.model_type}
                </p>
              )}
              {parsedContent.user_prompt && (
                <p className="text-gray-600">
                  <strong>User Prompt:</strong> {parsedContent.user_prompt}
                </p>
              )}
            </div>

            {/* Analysis Content */}
            {parsedContent.analysis && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="prose max-w-none">
                  {formatAnalysisText(parsedContent.analysis)}
                </div>
              </div>
            )}

            {/* Charts Section */}
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-gray-900">Visual Analysis</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {parsedContent.charts.map((chart, index) => (
                  <ChartComponent key={index} chartData={chart} />
                ))}
              </div>
            </div>

            {/* Metadata */}
            {parsedContent.metadata && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Analysis Metadata</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Confidence:</span>
                    <span className="ml-2 capitalize">{parsedContent.metadata.confidence}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Analysis Type:</span>
                    <span className="ml-2">{parsedContent.metadata.analysis_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Charts Generated:</span>
                    <span className="ml-2">{parsedContent.metadata.chart_count}</span>
                  </div>
                  {parsedContent.timestamp && (
                    <div>
                      <span className="text-gray-500">Timestamp:</span>
                      <span className="ml-2">{new Date(parsedContent.timestamp).toLocaleString()}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      }
    }

    // Regular message rendering (text-based)
    return (
      <div className="whitespace-pre-wrap">
        {message.content}
      </div>
    );
  };

  return (
    <div className="space-y-6" ref={analysisRef}>
      {messages.map((message, index) => (
        <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
          {message.role === 'assistant' && (
            <div className="relative h-9 w-9 flex items-center justify-center flex-shrink-0">
              <img 
                src={require('../image/mikeross.webp')} 
                alt="Mike Ross" 
                className="h-8 w-8 rounded-full border-2 border-blue-200 shadow" 
              />
            </div>
          )}
          <div className={`max-w-3xl rounded-xl px-4 py-3 ${
            message.role === 'user' 
              ? 'bg-blue-500 text-white ml-12' 
              : 'bg-gray-50 border border-gray-200'
          }`}>
            {renderMessage(message)}
          </div>
        </div>
      ))}
      {loading && (
        <div className="flex gap-3">
          <div className="relative h-9 w-9 flex items-center justify-center">
            <img 
              src={require('../image/mikeross.webp')} 
              alt="Mike Ross" 
              className="h-8 w-8 rounded-full border-2 border-blue-200 shadow" 
            />
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">Mike is analyzing...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// UploadArea component
const UploadArea = ({ 
  dragActive, 
  handleDrag, 
  handleDrop, 
  fileInputRef, 
  handleFileSelect, 
  uploadedFiles, 
  removeFile 
}) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="mb-8">
      <h2 className="text-lg font-medium text-gray-900 mb-4">
        Upload Documents {uploadedFiles.length > 0 && `(${uploadedFiles.length})`}
      </h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors mb-6 bg-white ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileSelect}
          accept=".pdf,.doc,.docx,.txt,.md"
          multiple
        />

        <div className="space-y-4">
          <div className="flex items-center justify-center">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <Upload className="w-6 h-6 text-gray-400" />
            </div>
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              Drop your documents here
            </p>
            <p className="text-gray-500 text-sm">or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="mt-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              Browse Files
            </button>
          </div>
          <p className="text-xs text-gray-400">PDF, DOC, DOCX, TXT, MD (Multiple files supported)</p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="max-h-48 overflow-y-auto space-y-3 pr-2">
          {uploadedFiles.map((fileObj) => (
            <div
              key={fileObj.id}
              className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-200"
            >
              <FileText className="w-5 h-5 text-green-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  {fileObj.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(fileObj.file.size)}
                </p>
              </div>
              <button
                onClick={() => removeFile(fileObj.id)}
                className="text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Header component
const Header = () => (
  <div className="border-b border-gray-200">
    <div className="max-w-4xl mx-auto px-6 py-4">
      <h1 className="text-2xl font-semibold text-gray-900">
        Document Processing
      </h1>
    </div>
  </div>
);

// ModuleBar component
const ModuleBar = ({ modules, selectedModule, setSelectedModule, caseTitle }) => (
  <div className="flex items-center space-x-3">
    {modules.map((module) => (
      <button
        key={module.id}
        onClick={() => setSelectedModule(module.id)}
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg border-2 transition-all ${
          selectedModule === module.id
            ? "border-blue-500 bg-blue-50 text-blue-700"
            : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
        }`}
      >
        <span className="text-sm">{module.icon}</span>
        <span className="font-medium text-xs">{module.title}</span>
      </button>
    ))}
  </div>
);

// ChatInput component
const ChatInput = ({ 
  selectedModule, 
  loading, 
  input, 
  setInput, 
  sendMessage, 
  error, 
  hasAssistant, 
  onAddFile 
}) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !loading) {
        sendMessage();
      }
    }
  };

  const handleSendClick = () => {
    if (input.trim() && !loading) {
      sendMessage();
    }
  };

  return (
    <div className="flex items-center gap-2">
      {hasAssistant && (
        <button
          onClick={onAddFile}
          className="flex items-center justify-center w-8 h-8 border border-gray-300 rounded-full hover:bg-gray-50"
        >
          <Plus className="w-4 h-4 text-gray-600" />
        </button>
      )}
      <div className="flex-1">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={selectedModule ? `Ask Mike about ${selectedModule}...` : "Select a module first..."}
          className="w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={!selectedModule || loading}
        />
      </div>
      <button
        onClick={handleSendClick}
        disabled={!selectedModule || loading || !input.trim()}
        className="px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Send
      </button>
      {error && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 bg-red-100 border border-red-300 rounded text-red-700 text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

// Mock hook for demonstration
const useCaseChat = () => {
  const [selectedModule, setSelectedModule] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const analysisRef = useRef(null);

  const modules = [
    { id: "analysis", title: "Analysis", icon: "📊" },
    { id: "summarize", title: "Summarize", icon: "📝" },
    { id: "translate", title: "Translate", icon: "🌍" },
    { id: "extract", title: "Extract", icon: "🔍" },
  ];

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Mock API call - replace with your actual API
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock response with charts (replace with actual API call)
      const mockResponse = {
        "case_id": "case_1755121996",
        "model_type": "case-breaker",
        "case_title": "TechCorp Analysis",
        "user_prompt": input,
        "analysis": "## Case Analysis Results\n\n### Key Findings\n\nBased on your inquiry, here are the main findings...",
        "timestamp": new Date().toISOString(),
        "status": "completed",
        "has_charts": true,
        "charts": [
          {
            "type": "pie",
            "title": "Risk Distribution",
            "data": {
              "labels": ["High Risk", "Medium Risk", "Low Risk"],
              "datasets": [{
                "data": [30, 45, 25],
                "backgroundColor": ["#EF4444", "#F59E0B", "#10B981"],
                "borderWidth": 2,
                "borderColor": "#ffffff"
              }]
            },
            "options": {
              "responsive": true,
              "plugins": {
                "legend": {"position": "bottom"},
                "title": {"display": true, "text": "Risk Assessment"}
              }
            }
          }
        ],
        "metadata": {
          "model": "Case Breaker",
          "analysis_type": "AI-generated",
          "confidence": "high",
          "chart_count": 1
        }
      };

      const assistantMessage = { 
        role: 'assistant', 
        content: JSON.stringify(mockResponse) 
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return {
    selectedModule,
    setSelectedModule,
    caseTitle: 'Demo Case',
    messages,
    input,
    setInput,
    loading,
    error,
    analysisRef,
    modules,
    sendMessage
  };
};

// Main component
export default function DocumentUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadedDocsMeta, setUploadedDocsMeta] = useState([]);
  const [caseType, setCaseType] = useState('General Legal');
  const fileInputRef = useRef(null);
  const { selectedModule, setSelectedModule, caseTitle, messages, input, setInput, loading, error, analysisRef, modules, sendMessage } = useCaseChat();
  const hasAssistant = messages.some(m => m.role === 'assistant');

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
      // Your existing upload logic here
      console.log('Uploading:', file.name);
      // Mock upload success
      setUploadedDocsMeta(prev => [...prev, {
        document_id: Date.now(),
        filename: file.name,
        status: 'uploaded'
      }]);
    } catch (e) {
      console.error('Document upload failed', e);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-white flex flex-col">
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
                onChange={e => setCaseType(e.target.value)}
                className="border rounded px-3 py-2 text-sm focus:outline-none focus:ring focus:border-blue-400"
              >
                <option>General Legal</option>
                <option>Civil</option>
                <option>Criminal</option>
                <option>Corporate</option>
                <option>Family</option>
                <option>Tax</option>
              </select>
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
            onAddFile={() => { if(fileInputRef.current) { fileInputRef.current.click(); }}}
          />
        </div>
      </div>
    </>
  );
}