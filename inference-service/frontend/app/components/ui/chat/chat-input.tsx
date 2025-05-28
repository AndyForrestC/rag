"use client";

import { useState } from "react";
import { PaperclipIcon } from "../../icons";

export interface ChatInputProps {
  /** The current value of the input */
  input?: string;
  /** An input/textarea-ready onChange handler to control the value of the input */
  handleInputChange?: (
    e:
      | React.ChangeEvent<HTMLInputElement>
      | React.ChangeEvent<HTMLTextAreaElement>,
  ) => void;
  /** Form submission handler to automatically reset input and append a user message  */
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
  multiModal?: boolean;
}

export default function ChatInput(props: ChatInputProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setSelectedFile(file || null);
    setUploadMessage(""); // Clear any previous messages
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    setUploadMessage("");
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch('http://localhost:8001/api/ingestion/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const result = await response.json();
      setUploadMessage(`✅ File uploaded successfully: ${result.filename}`);
      console.log("Upload result:", result);
      
      // Reset selected file after successful upload
      setSelectedFile(null);
      
      // Clear success message after 3 seconds
      setTimeout(() => setUploadMessage(""), 3000);
      
    } catch (error) {
      console.error("Upload error:", error);
      setUploadMessage(`❌ Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <form
        onSubmit={props.handleSubmit}
        className="flex flex-col items-start justify-between w-full p-0 gap-4"
      >
        {/* Upload message display */}
        {uploadMessage && (
          <div className={`w-full p-3 rounded-lg text-sm ${
            uploadMessage.startsWith('✅') 
              ? 'bg-green-50 text-green-700 border border-green-200' 
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {uploadMessage}
          </div>
        )}

        {/* File upload section */}
        {selectedFile && (
          <div className="flex items-center gap-4 w-full p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2 flex-1">
              <PaperclipIcon className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700 truncate">
                {selectedFile.name}
              </span>
              <span className="text-xs text-gray-500">
                ({(selectedFile.size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleFileUpload}
                disabled={uploading}
                className="px-3 py-1 bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white text-sm rounded-lg transition-colors"
              >
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                disabled={uploading}
                className="px-3 py-1 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 text-gray-700 text-sm rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Chat input section */}
        <div className="relative w-full">
          <div className="flex items-end gap-2 px-4 py-3 border border-gray-300 rounded-3xl bg-white focus-within:border-gray-400 transition-colors shadow-sm">
            <input
              autoFocus
              name="message"
              placeholder="Message Internal RAG System"
              className="flex-1 resize-none border-0 bg-transparent p-0 text-base text-gray-900 placeholder-gray-500 focus:outline-none"
              value={props.input}
              onChange={props.handleInputChange}
            />
            <div className="flex items-center gap-2">
              <input
                type="file"
                id="file-upload"
                onChange={handleFileChange}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.md"
              />
              <label
                htmlFor="file-upload"
                className="p-1.5 text-gray-500 hover:text-gray-700 rounded-full cursor-pointer transition-colors flex items-center justify-center"
                title="Attach file"
              >
                <PaperclipIcon className="w-5 h-5" />
              </label>
              <button
                disabled={props.isLoading || !props.input?.trim()}
                type="submit"
                className="w-8 h-8 text-white bg-black hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-full transition-colors flex items-center justify-center"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </form>
    </>
  );
}
