import React, { useState, useRef } from "react";
import { Upload, X, Check, ArrowRight, Plus, FileText } from "lucide-react";

export default function DocumentUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedModule, setSelectedModule] = useState(null);
  const fileInputRef = useRef(null);

  const modules = [
    { id: "analysis", title: "Analysis", icon: "📊" },
    { id: "summarize", title: "Summarize", icon: "📝" },
    { id: "translate", title: "Translate", icon: "🌍" },
    { id: "extract", title: "Extract", icon: "🔍" },
  ];

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

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const newFile = {
        id: Date.now(),
        file: e.target.files[0],
      };
      setUploadedFiles((prev) => [...prev, newFile]);
      // Reset input
      e.target.value = "";
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const handleContinue = () => {
    if (selectedModule) {
      console.log("Processing documents:", uploadedFiles.map((f) => f.file.name));
      console.log("Selected module:", selectedModule);
      console.log("Number of files:", uploadedFiles.length);
      if (uploadedFiles.length > 0) {
        console.log(
          "File details:",
          uploadedFiles.map((f) => ({
            name: f.file.name,
            size: f.file.size,
            type: f.file.type,
          }))
        );
      } else {
        console.log("Proceeding without documents");
      }
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
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main Content */}
      <div className="flex-1">
        <div className="border-b border-gray-200">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <h1 className="text-2xl font-semibold text-gray-900">
              Document Processing
            </h1>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Upload Area - Always Visible */}
          <div className="mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Upload Documents {uploadedFiles.length > 0 && `(${uploadedFiles.length})`}
            </h2>
            
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors mb-6 ${
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

          {/* Instructions */}
          <div className="text-center text-gray-600 mb-0">
            <p className="text-sm">
              Upload documents above or select a processing module below to continue
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Module Selection Bar - Always Visible */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2 p-3 font-extrabold text-black border border-black rounded-full hover:bg-blue-50 transition-colors"
              title="Add Document"
            >
              <Plus className="w-4 h-4" />
            </button>
            
            {/* Module Buttons */}
            <div className="flex space-x-3 flex-1">
              {modules.map((module) => (
                <button
                  key={module.id}
                  onClick={() => setSelectedModule(module.id)}
                  className={`flex items-center space-x-2 px-4 py-3 rounded-lg border-2 transition-all flex-1 justify-center ${
                    selectedModule === module.id
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-lg">{module.icon}</span>
                  <span className="font-medium text-sm">{module.title}</span>
                </button>
              ))}
            </div>

            {/* Continue Button */}
            <button
              onClick={handleContinue}
              disabled={!selectedModule}
              className={`flex items-center space-x-2 px-6 py-3 rounded-md font-medium transition-all whitespace-nowrap ${
                selectedModule
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}