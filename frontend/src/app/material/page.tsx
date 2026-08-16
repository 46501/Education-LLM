"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, CheckCircle, AlertCircle, X } from "lucide-react";

export default function StudyMaterial() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");

  const handleFile = async (file: File) => {
    setIsUploading(true);
    setStatus("idle");
    setUploadProgress(20);
    
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/documents/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      
      setUploadProgress(100);
      if (res.ok) {
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch (err) {
      console.error(err);
      setStatus("error");
    } finally {
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 2000);
    }
  };

  const onDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Study Material</h1>
        <p className="text-gray-500 mt-1">Upload PDFs to augment your AI Tutor's knowledge base.</p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
          dragActive ? "border-indigo-500 bg-indigo-50" : "border-gray-200 bg-white hover:border-indigo-300 hover:bg-gray-50"
        }`}
        onDragEnter={onDrag}
        onDragLeave={onDrag}
        onDragOver={onDrag}
        onDrop={onDrop}
      >
        <div className="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <UploadCloud size={32} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Drag and drop your files here</h3>
        <p className="text-sm text-gray-500 mb-6">Supported formats: .pdf (Max size: 10MB)</p>
        
        <label className="inline-flex cursor-pointer bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm">
          Browse Files
          <input 
            type="file" 
            className="hidden" 
            accept=".pdf"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) handleFile(e.target.files[0]);
            }}
          />
        </label>
      </div>

      {isUploading && (
        <div className="mt-8 bg-white p-5 rounded-xl border border-gray-100 premium-shadow">
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium text-gray-700 flex items-center gap-2">
              <FileText size={18} className="text-indigo-500" /> Uploading document...
            </span>
            <span className="text-sm font-semibold text-indigo-600">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <div className="bg-indigo-600 h-2 transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
          </div>
        </div>
      )}

      {status === "success" && (
        <div className="mt-8 bg-emerald-50 border border-emerald-100 text-emerald-800 p-4 rounded-xl flex items-start gap-3">
          <CheckCircle className="text-emerald-500 mt-0.5 shrink-0" />
          <div>
            <h4 className="font-semibold">Upload Complete</h4>
            <p className="text-sm text-emerald-700 mt-1">Your document has been processed and vectorized. The AI Tutor can now answer questions about it.</p>
          </div>
          <button onClick={() => setStatus("idle")} className="ml-auto text-emerald-500 hover:text-emerald-700">
            <X size={20} />
          </button>
        </div>
      )}

      {status === "error" && (
        <div className="mt-8 bg-red-50 border border-red-100 text-red-800 p-4 rounded-xl flex items-start gap-3">
          <AlertCircle className="text-red-500 mt-0.5 shrink-0" />
          <div>
            <h4 className="font-semibold">Upload Failed</h4>
            <p className="text-sm text-red-700 mt-1">There was a problem processing your document. Please ensure it is a valid PDF and try again.</p>
          </div>
          <button onClick={() => setStatus("idle")} className="ml-auto text-red-500 hover:text-red-700">
            <X size={20} />
          </button>
        </div>
      )}

      <div className="mt-12 flex-1">
        <h2 className="font-semibold text-gray-900 mb-4 border-b border-gray-100 pb-2">Your Documents</h2>
        {/* Placeholder for fetching actual document list from backend if an endpoint exists */}
        <div className="text-center p-12 bg-white rounded-xl border border-gray-100 border-dashed">
          <p className="text-gray-500 text-sm">You haven't uploaded any study material yet.</p>
        </div>
      </div>
    </div>
  );
}
