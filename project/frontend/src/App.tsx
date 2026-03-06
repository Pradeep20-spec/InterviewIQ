import { useState } from 'react';
import LandingPage from './components/LandingPage';
import ResumeUpload from './components/ResumeUpload';
import PersonalitySelection from './components/PersonalitySelection';
import InterviewSimulation from './components/InterviewSimulation';
import PerformanceResults from './components/PerformanceResults';
import AuthPage from './components/AuthPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { sessionApi } from './services/api';
import { Loader2 } from 'lucide-react';

type Page = 'landing' | 'upload' | 'personality' | 'interview' | 'results';

export interface InterviewSession {
  sessionId?: string;
  resumeFile?: File;
  resumeText?: string;
  resumeAnalysis?: Record<string, unknown>;
  personality?: string;
  responses?: Array<{
    question: string;
    answer: string;
    timestamp: number;
  }>;
}

function AppContent() {
  const { isAuthenticated, isLoading, user, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [session, setSession] = useState<InterviewSession>({});

  const navigateTo = (page: Page) => {
    setCurrentPage(page);
  };

  const updateSession = (data: Partial<InterviewSession>) => {
    setSession(prev => ({ ...prev, ...data }));
  };

  const startInterview = async (personality: string) => {
    updateSession({ personality });

    // Create session on backend
    try {
      const result = await sessionApi.create({
        resume_text: session.resumeText,
        resume_filename: session.resumeFile?.name,
        personality,
        user_id: user?.id,
      });
      if (result.success && result.data) {
        updateSession({ personality, sessionId: result.data.id });
      }
    } catch (err) {
      console.warn('Backend unavailable, continuing offline:', err);
    }

    navigateTo('interview');
  };

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
      </div>
    );
  }

  // Show auth page if not logged in
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={() => {}} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {currentPage === 'landing' && (
        <LandingPage
          onGetStarted={() => navigateTo('upload')}
          userName={user?.name}
          onLogout={logout}
        />
      )}
      {currentPage === 'upload' && (
        <ResumeUpload
          onBack={() => navigateTo('landing')}
          onNext={(file, text, analysis) => {
            updateSession({ resumeFile: file, resumeText: text, resumeAnalysis: analysis });
            navigateTo('personality');
          }}
        />
      )}
      {currentPage === 'personality' && (
        <PersonalitySelection
          onBack={() => navigateTo('upload')}
          onNext={(personality) => startInterview(personality)}
        />
      )}
      {currentPage === 'interview' && (
        <InterviewSimulation
          personality={session.personality || 'friendly'}
          sessionId={session.sessionId}
          onComplete={(responses) => {
            updateSession({ responses });
            navigateTo('results');
          }}
        />
      )}
      {currentPage === 'results' && (
        <PerformanceResults
          session={session}
          onRetry={() => {
            setSession({});
            navigateTo('landing');
          }}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
