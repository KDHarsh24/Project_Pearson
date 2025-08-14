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
    <div className="mb-8 w-full">
      <h2 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">Upload Documents {uploadedFiles.length > 0 && `(${uploadedFiles.length})`}</h2>
      <div className={`border-2 border-dashed rounded-lg p-4 sm:p-8 text-center transition-colors mb-6 w-full ${dragActive ? 'border-blue-500 bg-blue-50':'border-gray-300 hover:border-gray-400'}`}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
        <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect} accept=".pdf,.doc,.docx,.txt,.md" multiple />
        <div className="space-y-3 sm:space-y-4">
          <div className="flex items-center justify-center">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gray-100 rounded-full flex items-center justify-center"><Upload className="w-5 h-5 sm:w-6 sm:h-6 text-gray-400" /></div>
          </div>
          <div>
            <p className="text-base sm:text-lg font-medium text-gray-900">Drop your documents here</p>
            <p className="text-gray-500 text-xs sm:text-sm">or</p>
            <button onClick={() => fileInputRef.current?.click()} className="mt-2 px-4 py-2 sm:px-6 sm:py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium w-full sm:w-auto">Browse Files</button>
          </div>
          <p className="text-xs text-gray-400">PDF, DOC, DOCX, TXT, MD (Multiple files supported)</p>
        </div>
      </div>
      {uploadedFiles.length > 0 && (
        <div className="max-h-48 overflow-y-auto space-y-2 sm:space-y-3 pr-1 sm:pr-2">
          {uploadedFiles.map(f => (
            <div key={f.id} className="flex flex-col sm:flex-row items-center sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 p-2 sm:p-3 bg-green-50 rounded-lg border border-green-200 w-full">
              <div className="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 bg-green-100 rounded-full"><FileText className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" /></div>
              <div className="flex-1 w-full text-center sm:text-left">
                <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{f.file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(f.file.size)}</p>
              </div>
              <button onClick={()=> removeFile(f.id)} className="text-gray-400 hover:text-red-500 transition-colors w-8 h-8 flex items-center justify-center"><X className="w-4 h-4" /></button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
