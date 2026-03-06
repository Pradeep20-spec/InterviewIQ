import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, ArrowLeft, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import { aiApi } from '../services/api';

interface ResumeUploadProps {
  onBack: () => void;
  onNext: (file: File, text: string, analysis?: Record<string, unknown>) => void;
}

export default function ResumeUpload({ onBack, onNext }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string>('');
  const [resumeText, setResumeText] = useState<string>('');
  const [isParsing, setIsParsing] = useState(false);
  const [parsedSkills, setParsedSkills] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateFile = (file: File): boolean => {
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 5 * 1024 * 1024;

    if (!validTypes.includes(file.type)) {
      setError('Please upload a PDF, DOC, DOCX, or TXT file');
      return false;
    }

    if (file.size > maxSize) {
      setError('File size must be less than 5MB');
      return false;
    }

    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setError('');

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError('');
    const selectedFile = e.target.files?.[0];
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
    }
  };

  const handleContinue = async () => {
    setError('');
    setIsParsing(true);

    try {
      if (file) {
        // Upload the actual file → backend parses PDF/DOCX and runs AI analysis
        const result = await aiApi.uploadResume(file);
        if (result.success && result.data) {
          setParsedSkills(result.data.analysis?.skills ?? []);
          onNext(file, result.data.resume_text, result.data.analysis as unknown as Record<string, unknown>);
        } else {
          setError(result.error || 'Failed to parse resume. Try pasting it as text instead.');
          setIsParsing(false);
        }
      } else if (resumeText.trim()) {
        // Plain text → still wrap it in a File so the rest of the flow works
        const textFile = new File([resumeText], 'resume.txt', { type: 'text/plain' });
        onNext(textFile, resumeText);
      }
    } catch {
      setError('Network error. Is the backend server running?');
      setIsParsing(false);
    }
  };

  const canContinue = file !== null || resumeText.trim().length > 0;

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Home
        </button>

        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 border border-slate-200">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-3">
              Upload Your Resume
            </h1>
            <p className="text-slate-600 text-lg">
              Upload your resume so we can generate personalized interview questions based on your experience
            </p>
          </div>

          <div className="space-y-6">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-3 border-dashed rounded-xl p-12 text-center transition-all ${
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : file
                  ? 'border-green-500 bg-green-50'
                  : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />

              {file ? (
                <div className="flex flex-col items-center gap-4">
                  <CheckCircle className="w-16 h-16 text-green-600" />
                  <div>
                    <p className="text-lg font-semibold text-slate-900">{file.name}</p>
                    <p className="text-slate-600">{(file.size / 1024).toFixed(2)} KB</p>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <Upload className="w-16 h-16 text-slate-400" />
                  <div>
                    <p className="text-lg font-semibold text-slate-900 mb-2">
                      Drag and drop your resume here
                    </p>
                    <p className="text-slate-600 mb-4">or</p>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                    >
                      Browse Files
                    </button>
                  </div>
                  <p className="text-sm text-slate-500">
                    Supported formats: PDF, DOC, DOCX, TXT (Max 5MB)
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            )}

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-slate-500">Or paste your resume text</span>
              </div>
            </div>

            <div>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume content here..."
                className="w-full h-48 px-4 py-3 border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none text-slate-900"
              />
              <p className="text-sm text-slate-500 mt-2">
                {resumeText.length} characters
              </p>
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={handleContinue}
              disabled={!canContinue || isParsing}
              className={`flex items-center gap-2 px-8 py-3 rounded-lg font-semibold transition-all ${
                canContinue && !isParsing
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg'
                  : 'bg-slate-300 text-slate-500 cursor-not-allowed'
              }`}
            >
              {isParsing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analysing Resume with AI...
                </>
              ) : (
                <>
                  Continue to Personality Selection
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          {parsedSkills.length > 0 && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-green-600" />
                <h4 className="font-semibold text-green-800">AI-Detected Skills</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {parsedSkills.map((skill, i) => (
                  <span key={i} className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex gap-3">
            <FileText className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Why do we need your resume?</h3>
              <p className="text-slate-700 text-sm leading-relaxed">
                Your resume helps our AI generate personalized interview questions relevant to your experience,
                skills, and the roles you're targeting. The more detailed your resume, the more realistic your
                mock interview will be.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
