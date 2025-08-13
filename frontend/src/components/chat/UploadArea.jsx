import React from 'react';
import { Upload, X, FileText } from 'lucide-react';

export function UploadArea({ dragActive, handleDrag, handleDrop, fileInputRef, handleFileSelect, uploadedFiles, removeFile }) {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024; const sizes = ['Bytes','KB','MB','GB'];
    const i = Math.floor(Math.log(bytes)/Math.log(k));
    return parseFloat((bytes/Math.pow(k,i)).toFixed(2)) + ' ' + sizes[i];
  };
  return (
    <div className="mb-8">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Documents {uploadedFiles.length > 0 && `(${uploadedFiles.length})`}</h2>
      <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors mb-6 ${dragActive ? 'border-blue-500 bg-blue-50':'border-gray-300 hover:border-gray-400'}`}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
        <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect} accept=".pdf,.doc,.docx,.txt,.md" multiple />
        <div className="space-y-4">
          <div className="flex items-center justify-center">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center"><Upload className="w-6 h-6 text-gray-400" /></div>
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">Drop your documents here</p>
            <p className="text-gray-500 text-sm">or</p>
            <button onClick={() => fileInputRef.current?.click()} className="mt-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium">Browse Files</button>
          </div>
          <p className="text-xs text-gray-400">PDF, DOC, DOCX, TXT, MD (Multiple files supported)</p>
        </div>
      </div>
      {uploadedFiles.length > 0 && (
        <div className="max-h-48 overflow-y-auto space-y-3 pr-2">
          {uploadedFiles.map(f => (
            <div key={f.id} className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-200">
              <FileText className="w-5 h-5 text-green-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{f.file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(f.file.size)}</p>
              </div>
              <button onClick={()=> removeFile(f.id)} className="text-gray-400 hover:text-red-500 transition-colors"><X className="w-4 h-4" /></button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
