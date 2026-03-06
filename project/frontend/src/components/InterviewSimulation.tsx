import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, Video, MessageSquare, Send, Volume2, Clock, CheckCircle, Loader2, Sparkles, AlertTriangle } from 'lucide-react';
import { interviewApi, sessionApi, aiApi } from '../services/api';

interface InterviewSimulationProps {
  personality: string;
  sessionId?: string;
  onComplete: (responses: Array<{ question: string; answer: string; timestamp: number }>) => void;
}

type InputMode = 'text' | 'audio' | 'video';

const fallbackQuestions: Record<string, string[]> = {
  friendly: [
    "Tell me about yourself and your technical background.",
    "What programming languages and frameworks are you most proficient in?",
    "Can you describe a technically challenging project you're particularly proud of?",
    "How do you approach debugging a complex issue in production?",
    "Explain the difference between SQL and NoSQL databases — when would you use each?",
    "How do you ensure code quality in your projects?",
    "Describe your experience with version control and CI/CD pipelines.",
    "What is your approach to writing testable and maintainable code?",
    "How do you handle constructive criticism during code reviews?",
    "How do you stay current with evolving technologies and best practices?"
  ],
  technical: [
    "Explain the difference between let, const, and var in JavaScript.",
    "How would you optimize a slow database query? Walk me through your process.",
    "Describe the SOLID principles and give a real example from your work.",
    "Explain how garbage collection works in your preferred language.",
    "Describe how you would design a RESTful API for a social media platform.",
    "Explain the concept of closures and provide a practical use case.",
    "How does a hash table work internally? What are its time complexities?",
    "How would you implement authentication and authorization in a web application?",
    "Explain the difference between synchronous and asynchronous programming.",
    "How would you design a system to handle millions of concurrent users?"
  ],
  stress: [
    "Why should we hire you over other candidates?",
    "You discover a critical bug in production at 5 PM on a Friday — walk me through your response.",
    "How do you handle tight deadlines with conflicting priorities?",
    "Convince me why your architecture choice is better than the alternative.",
    "Your manager disagrees with your technical approach — what do you do?",
    "Explain the trade-offs between microservices and monolithic architectures under pressure.",
    "How would you re-architect a failing system with zero downtime?",
    "What would you do if you were assigned a technology stack you have never used?",
    "Tell me about a time you made an architectural decision with incomplete information.",
    "How do you respond when someone challenges your technical decisions publicly?"
  ],
  panel: [
    "How do you approach problem-solving in a team environment?",
    "What's your approach to code reviews — what do you look for?",
    "Tell us about a time you had to make a difficult technical decision.",
    "Describe the concept of containerization and how you've used it.",
    "What design patterns have you used and why?",
    "What is your strategy for managing technical debt in a fast-moving team?",
    "How do you approach estimating the effort for a complex feature?",
    "Describe how you would set up a CI/CD pipeline from scratch.",
    "How do you ensure effective communication across distributed engineering teams?",
    "Explain how you would mentor a junior developer on system design principles."
  ]
};

export default function InterviewSimulation({ personality, sessionId, onComplete }: InterviewSimulationProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [textAnswer, setTextAnswer] = useState('');
  const [responses, setResponses] = useState<Array<{ question: string; answer: string; timestamp: number }>>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [questions, setQuestions] = useState<string[]>([]);
  const [questionMeta, setQuestionMeta] = useState<Array<{ category: string; difficulty: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [aiPowered, setAiPowered] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [micError, setMicError] = useState<string | null>(null);
  const [micReady, setMicReady] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);  // backend STT in progress
  const videoRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const transcriptRef = useRef<string>(''); // always holds latest transcript synchronously
  const recordingTimeRef = useRef<number>(0); // always holds latest recording duration

  // ── WAV Recorder refs ────────────────────────────────────
  const wavContextRef = useRef<AudioContext | null>(null);
  const wavProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const wavSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const wavGainRef = useRef<GainNode | null>(null);
  const wavChunksRef = useRef<Float32Array[]>([]);
  const wavSampleRateRef = useRef<number>(16000);

  const currentQuestion = questions[currentQuestionIndex] || '';
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  // Fetch questions: AI-generated first → DB fallback → hardcoded fallback
  useEffect(() => {
    const loadQuestions = async () => {
      setIsLoading(true);

      // 1. Try AI-generated questions (needs sessionId with resume)
      if (sessionId) {
        try {
          const aiResult = await aiApi.generateQuestions(sessionId, personality, 10);
          if (aiResult.success && aiResult.data?.questions?.length) {
            setQuestions(aiResult.data.questions.map((q) => q.question));
            setQuestionMeta(aiResult.data.questions.map((q) => ({ category: q.category, difficulty: q.difficulty })));
            setAiPowered(true);
            setIsLoading(false);
            return;
          }
        } catch {
          // AI unavailable, fall through
        }
      }

      // 2. Fallback to DB questions
      try {
        const result = await interviewApi.getQuestions(personality);
        if (result.success && Array.isArray(result.data) && result.data.length > 0) {
          setQuestions(result.data.map((q: { question: string }) => q.question));
        } else {
          setQuestions(fallbackQuestions[personality] || fallbackQuestions.friendly);
        }
      } catch {
        setQuestions(fallbackQuestions[personality] || fallbackQuestions.friendly);
      } finally {
        setIsLoading(false);
      }
    };
    loadQuestions();
  }, [personality, sessionId]);

  // Speak the current question when it changes
  useEffect(() => {
    if (!isLoading && currentQuestion) {
      speakQuestion(currentQuestion);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [currentQuestionIndex, isLoading]);

  const speakQuestion = (question: string) => {
    setIsSpeaking(true);
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(question);
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    } else {
      setTimeout(() => setIsSpeaking(false), 3000);
    }
  };

  // ── WAV Encoding Helper ───────────────────────────────────
  const encodeWav = useCallback((samples: Float32Array, sampleRate: number): Blob => {
    // Float32 → Int16
    const pcm16 = new Int16Array(samples.length);
    for (let i = 0; i < samples.length; i++) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    const wavBuf = new ArrayBuffer(44 + pcm16.byteLength);
    const dv = new DataView(wavBuf);
    const writeStr = (off: number, str: string) => {
      for (let i = 0; i < str.length; i++) dv.setUint8(off + i, str.charCodeAt(i));
    };

    writeStr(0, 'RIFF');
    dv.setUint32(4, 36 + pcm16.byteLength, true);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    dv.setUint32(16, 16, true);       // fmt chunk size
    dv.setUint16(20, 1, true);        // PCM format
    dv.setUint16(22, 1, true);        // mono
    dv.setUint32(24, sampleRate, true);
    dv.setUint32(28, sampleRate * 2, true); // byte rate
    dv.setUint16(32, 2, true);        // block align
    dv.setUint16(34, 16, true);       // bits per sample
    writeStr(36, 'data');
    dv.setUint32(40, pcm16.byteLength, true);

    new Uint8Array(wavBuf).set(new Uint8Array(pcm16.buffer), 44);
    return new Blob([wavBuf], { type: 'audio/wav' });
  }, []);

  // ── Start WAV Recorder (Web Audio API) ──────────────────
  const startWavRecorder = useCallback((stream: MediaStream) => {
    try {
      const ctx = new AudioContext({ sampleRate: 16000 });
      wavSampleRateRef.current = ctx.sampleRate; // might differ if 16kHz unsupported
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      const silencer = ctx.createGain();
      silencer.gain.value = 0; // don't play mic audio through speakers

      wavChunksRef.current = [];
      processor.onaudioprocess = (e) => {
        wavChunksRef.current.push(new Float32Array(e.inputBuffer.getChannelData(0)));
      };

      source.connect(processor);
      processor.connect(silencer);
      silencer.connect(ctx.destination); // needed for processing to trigger

      wavContextRef.current = ctx;
      wavSourceRef.current = source;
      wavProcessorRef.current = processor;
      wavGainRef.current = silencer;
    } catch (err) {
      console.warn('WAV recorder init failed:', err);
    }
  }, []);

  // ── Stop WAV Recorder → returns Blob ────────────────────
  const stopWavRecorder = useCallback((): Blob | null => {
    try {
      wavProcessorRef.current?.disconnect();
      wavSourceRef.current?.disconnect();
      wavGainRef.current?.disconnect();
      const sampleRate = wavSampleRateRef.current;
      wavContextRef.current?.close();

      const chunks = wavChunksRef.current;
      if (!chunks.length) return null;

      const totalSamples = chunks.reduce((n, c) => n + c.length, 0);
      if (totalSamples < sampleRate) return null; // less than 1 second of audio

      const pcm = new Float32Array(totalSamples);
      let offset = 0;
      for (const c of chunks) { pcm.set(c, offset); offset += c.length; }

      return encodeWav(pcm, sampleRate);
    } catch (err) {
      console.warn('WAV recorder stop failed:', err);
      return null;
    } finally {
      wavContextRef.current = null;
      wavSourceRef.current = null;
      wavProcessorRef.current = null;
      wavGainRef.current = null;
      wavChunksRef.current = [];
    }
  }, [encodeWav]);

  // ── Speech-to-Text helper ───────────────────────────────
  const startSpeechRecognition = useCallback(() => {
    const SR = (window.SpeechRecognition || window.webkitSpeechRecognition) as typeof SpeechRecognition | undefined;
    if (!SR) {
      setMicError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += t + ' ';
        } else {
          interim += t;
        }
      }
      const combined = finalTranscript + interim;
      transcriptRef.current = combined; // keep ref in sync for stopRecording
      setTranscript(combined);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      const err = event.error;
      switch (err) {
        case 'not-allowed':
          setMicError('Microphone access was denied. Please allow microphone permission in your browser settings and try again.');
          break;
        case 'no-speech':
          // This fires after silence — not critical, recognition keeps running
          console.warn('No speech detected — keep speaking');
          break;
        case 'audio-capture':
          setMicError('No microphone found. Please connect a microphone and try again.');
          break;
        case 'network':
          setMicError('Network error during speech recognition. Check your internet connection.');
          break;
        case 'aborted':
          // User or code stopped it — not an error
          break;
        default:
          setMicError(`Speech recognition error: ${err}`);
      }
    };

    recognition.onstart = () => {
      setMicReady(true);
      setMicError(null);
    };

    recognition.onend = () => {
      // Auto-restart if still recording (recognition can stop after silence)
      if (recognitionRef.current === recognition) {
        try { recognition.start(); } catch { /* already running or stopped intentionally */ }
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, []);

  const stopSpeechRecognition = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = null; // prevent auto-restart on intentional stop
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  }, []);

  const startRecording = async () => {
    setTranscript('');
    transcriptRef.current = '';  // reset ref too
    recordingTimeRef.current = 0; // reset duration ref
    setMicError(null);
    setMicReady(false);

    // ── Get microphone (and optionally camera) stream ──────
    // We ALWAYS request audio from getUserMedia so we can record a WAV
    // file via Web Audio API. SpeechRecognition runs in parallel as an
    // optional live-preview — if it works, great; if not, the WAV
    // blob is sent to the backend for server-side transcription.
    try {
      const constraints: MediaStreamConstraints =
        inputMode === 'video'
          ? { video: true, audio: true }
          : { audio: true };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      audioStreamRef.current = stream;

      // Show camera preview for video mode
      if (inputMode === 'video' && videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Start WAV recorder on the audio track
      startWavRecorder(stream);
    } catch (err) {
      const mediaErr = err as DOMException;
      if (mediaErr.name === 'NotAllowedError') {
        setMicError(
          inputMode === 'video'
            ? 'Camera/microphone access was denied. Please allow permissions in your browser settings and try again.'
            : 'Microphone access was denied. Please allow microphone permission in your browser settings and try again.',
        );
      } else if (mediaErr.name === 'NotFoundError') {
        setMicError(
          inputMode === 'video'
            ? 'No camera/microphone found. Please connect a device and try again.'
            : 'No microphone found. Please connect a microphone and try again.',
        );
      } else {
        setMicError(`Media error: ${mediaErr.message}`);
      }
      return;
    }

    setIsRecording(true);
    setRecordingTime(0);
    recordingTimeRef.current = 0;
    timerRef.current = setInterval(() => {
      recordingTimeRef.current += 1;
      setRecordingTime(recordingTimeRef.current);
    }, 1000);

    // Start browser speech recognition for live transcript preview.
    // If it doesn't work, the WAV recorder is still capturing audio.
    startSpeechRecognition();
  };

  const stopRecording = async () => {
    setIsRecording(false);
    setMicReady(false);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    stopSpeechRecognition();

    // Stop WAV recorder and get the audio blob
    const wavBlob = stopWavRecorder();

    // Release all media streams
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
      audioStreamRef.current = null;
    }
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }

    // Read from refs (always up-to-date) not stale state closure
    const captured = transcriptRef.current.trim();
    const duration = recordingTimeRef.current;

    // ── Dual transcription strategy ────────────────────────
    // 1. If browser SpeechRecognition produced text → use it immediately.
    // 2. Otherwise, send the recorded WAV to the backend for
    //    server-side Google STT (more reliable, works everywhere).
    if (captured) {
      // SpeechRecognition worked — use it directly
      handleSubmitAnswer(captured, duration);
      return;
    }

    // SpeechRecognition failed — fall back to server-side transcription
    if (wavBlob) {
      setIsTranscribing(true);
      setTranscript('Transcribing your response...');
      try {
        const result = await aiApi.transcribeAudio(wavBlob);
        const serverTranscript = result?.data?.transcript?.trim() || '';
        if (serverTranscript) {
          transcriptRef.current = serverTranscript;
          setTranscript(serverTranscript);
          handleSubmitAnswer(serverTranscript, duration);
        } else {
          // Server couldn't transcribe either
          setTranscript('');
          const answer = `[${inputMode.toUpperCase()} Response - ${duration}s — speech not clear enough]`;
          handleSubmitAnswer(answer, duration);
        }
      } catch (err) {
        console.error('Backend transcription failed:', err);
        setTranscript('');
        const answer = `[${inputMode.toUpperCase()} Response - ${duration}s — transcription unavailable]`;
        handleSubmitAnswer(answer, duration);
      } finally {
        setIsTranscribing(false);
      }
    } else {
      // No WAV blob available (recording too short or error)
      const answer = inputMode === 'text'
        ? textAnswer
        : `[${inputMode.toUpperCase()} Response - ${duration}s — no speech detected]`;
      handleSubmitAnswer(answer, duration);
    }
  };

  const handleSubmitAnswer = async (answer: string, duration?: number) => {
    const newResponse = {
      question: currentQuestion,
      answer,
      timestamp: Date.now()
    };

    const updatedResponses = [...responses, newResponse];
    setResponses(updatedResponses);
    setTextAnswer('');
    setRecordingTime(0);

    // Save response to backend
    if (sessionId) {
      try {
        await interviewApi.saveResponse({
          session_id: sessionId,
          question_index: currentQuestionIndex,
          question: currentQuestion,
          answer,
          input_mode: inputMode,
          recording_duration: duration ?? recordingTimeRef.current,
          timestamp: Date.now(),
        });
      } catch (err) {
        console.warn('Failed to save response to backend:', err);
      }
    }

    if (isLastQuestion) {
      // Mark session as completed on the backend
      if (sessionId) {
        try {
          await sessionApi.updateStatus(sessionId, 'completed');
        } catch (err) {
          console.warn('Failed to update session status:', err);
        }
      }
      onComplete(updatedResponses);
    } else {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const personalityStyles = {
    friendly: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
    technical: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
    stress: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
    panel: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' }
  };

  const style = personalityStyles[personality as keyof typeof personalityStyles] || personalityStyles.friendly;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-slate-600 text-lg font-medium">
            {sessionId ? 'AI is generating personalised questions from your resume...' : 'Preparing your interview questions...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`px-4 py-2 rounded-lg ${style.bg} ${style.text} font-medium`}>
              {personality.charAt(0).toUpperCase() + personality.slice(1)} Interview
            </div>
            {aiPowered && (
              <div className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 text-sm font-medium">
                <Sparkles className="w-4 h-4" />
                AI-Powered
              </div>
            )}
            {questionMeta[currentQuestionIndex] && (
              <div className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium uppercase tracking-wide">
                {questionMeta[currentQuestionIndex].category} · {questionMeta[currentQuestionIndex].difficulty}
              </div>
            )}
          </div>
          <div className="text-slate-600 font-medium">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
          <div className={`${style.bg} ${style.border} border-b px-8 py-6`}>
            <div className="flex items-start gap-4">
              {isSpeaking && (
                <Volume2 className={`w-6 h-6 ${style.text} animate-pulse flex-shrink-0 mt-1`} />
              )}
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-slate-900 leading-relaxed">
                  {currentQuestion}
                </h2>
              </div>
            </div>
          </div>

          <div className="p-8">
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-3">
                Choose your response method:
              </label>
              <div className="flex gap-3">
                <button
                  onClick={() => setInputMode('text')}
                  disabled={isRecording}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    inputMode === 'text'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  } ${isRecording ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <MessageSquare className="w-5 h-5" />
                  Text
                </button>
                <button
                  onClick={() => setInputMode('audio')}
                  disabled={isRecording}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    inputMode === 'audio'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  } ${isRecording ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Mic className="w-5 h-5" />
                  Audio
                </button>
                <button
                  onClick={() => setInputMode('video')}
                  disabled={isRecording}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    inputMode === 'video'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  } ${isRecording ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Video className="w-5 h-5" />
                  Video
                </button>
              </div>
            </div>

            {inputMode === 'text' && (
              <div className="space-y-4">
                <textarea
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  className="w-full h-48 px-4 py-3 border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none text-slate-900"
                />
                <button
                  onClick={() => handleSubmitAnswer(textAnswer)}
                  disabled={!textAnswer.trim()}
                  className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold transition-all ${
                    textAnswer.trim()
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
                      : 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  {isLastQuestion ? <CheckCircle className="w-5 h-5" /> : <Send className="w-5 h-5" />}
                  {isLastQuestion ? 'Complete Interview' : 'Submit Answer'}
                </button>
              </div>
            )}

            {(inputMode === 'audio' || inputMode === 'video') && (
              <div className="space-y-4">
                {/* Microphone error banner */}
                {micError && (
                  <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Microphone Issue</p>
                      <p className="mt-1">{micError}</p>
                      <p className="mt-2 text-xs text-red-500">
                        Tip: Click the lock/site-settings icon in the address bar → set Microphone to "Allow" → reload the page.
                      </p>
                    </div>
                  </div>
                )}

                {inputMode === 'video' && (
                  <div className="bg-slate-900 rounded-lg overflow-hidden aspect-video">
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                {isRecording && (
                  <div className="flex items-center justify-center gap-3 py-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <div className="flex items-center gap-2 text-slate-700 font-medium">
                      <Clock className="w-5 h-5" />
                      {formatTime(recordingTime)}
                    </div>
                    {micReady && (
                      <div className="flex items-center gap-1 text-green-600 text-sm font-medium">
                        <Mic className="w-4 h-4" />
                        Listening...
                      </div>
                    )}
                  </div>
                )}

                {/* Live transcript */}
                {isRecording && transcript && (
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-700 text-sm italic">
                    <span className="font-medium text-slate-500 block mb-1">Live transcript:</span>
                    {transcript}
                  </div>
                )}
                {!isRecording && !isTranscribing && transcript && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 text-sm">
                    <span className="font-medium block mb-1">Transcribed answer:</span>
                    {transcript}
                  </div>
                )}

                {/* Backend transcription loading state */}
                {isTranscribing && (
                  <div className="flex items-center justify-center gap-3 py-6">
                    <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                    <span className="text-slate-700 font-medium">Transcribing your response...</span>
                  </div>
                )}

                {!isRecording && !isTranscribing ? (
                  <button
                    onClick={startRecording}
                    className="w-full flex items-center justify-center gap-2 bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 transition-all shadow-md"
                  >
                    {inputMode === 'audio' ? <Mic className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                    Start Recording
                  </button>
                ) : isRecording ? (
                  <button
                    onClick={stopRecording}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all shadow-md"
                  >
                    {isLastQuestion ? <CheckCircle className="w-5 h-5" /> : <Send className="w-5 h-5" />}
                    {isLastQuestion ? 'Complete Interview' : 'Submit Answer'}
                  </button>
                ) : null}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-600 font-medium">Progress</span>
            <span className="text-slate-700 font-semibold">{responses.length} / {questions.length} answered</span>
          </div>
          <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(responses.length / questions.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
