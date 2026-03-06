import { Briefcase, Brain, TrendingUp, Users, Video, Mic, FileText, ChevronRight, LogOut, UserCircle, MessageCircle, Code2, Flame, LayoutGrid } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
  userName?: string;
  onLogout?: () => void;
}

export default function LandingPage({ onGetStarted, userName, onLogout }: LandingPageProps) {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Questions',
      description: 'Questions tailored to your resume and target role',
      gradient: 'from-violet-500 to-purple-600',
      bg: 'bg-violet-50',
    },
    {
      icon: Users,
      title: 'Multiple Personalities',
      description: 'Practice with different interviewer styles',
      gradient: 'from-blue-500 to-cyan-500',
      bg: 'bg-blue-50',
    },
    {
      icon: Video,
      title: 'Multi-Modal Input',
      description: 'Respond via audio, video, or text',
      gradient: 'from-emerald-500 to-teal-500',
      bg: 'bg-emerald-50',
    },
    {
      icon: TrendingUp,
      title: 'Performance Analytics',
      description: 'Detailed metrics on your interview performance',
      gradient: 'from-orange-500 to-amber-500',
      bg: 'bg-orange-50',
    }
  ];

  const personalities = [
    {
      name: 'Friendly HR',
      icon: MessageCircle,
      gradient: 'from-emerald-400 to-teal-500',
      shadow: 'shadow-emerald-200',
      badge: 'Supportive',
      badgeBg: 'bg-emerald-100 text-emerald-700',
      description: 'Warm, encouraging tone. Great for building confidence and practicing behavioral questions.',
      border: 'border-emerald-200 hover:border-emerald-400',
      iconBg: 'bg-emerald-50',
    },
    {
      name: 'Strict Technical',
      icon: Code2,
      gradient: 'from-red-500 to-rose-600',
      shadow: 'shadow-red-200',
      badge: 'Challenging',
      badgeBg: 'bg-red-100 text-red-700',
      description: 'Deep technical evaluation with precise, demanding follow-up questions on your expertise.',
      border: 'border-red-200 hover:border-red-400',
      iconBg: 'bg-red-50',
    },
    {
      name: 'Stress Interview',
      icon: Flame,
      gradient: 'from-orange-400 to-red-500',
      shadow: 'shadow-orange-200',
      badge: 'High Pressure',
      badgeBg: 'bg-orange-100 text-orange-700',
      description: 'Pressure-tests your resilience and composure under tough, rapid-fire questioning.',
      border: 'border-orange-200 hover:border-orange-400',
      iconBg: 'bg-orange-50',
    },
    {
      name: 'Panel Interview',
      icon: LayoutGrid,
      gradient: 'from-blue-500 to-indigo-600',
      shadow: 'shadow-blue-200',
      badge: 'Multi-Perspective',
      badgeBg: 'bg-blue-100 text-blue-700',
      description: 'Simulates a multi-member panel assessing you from technical, cultural, and strategic angles.',
      border: 'border-blue-200 hover:border-blue-400',
      iconBg: 'bg-blue-50',
    }
  ];

  return (
    <div className="min-h-screen" style={{
      backgroundImage: `url('https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1800&q=80')`,
      backgroundBlendMode: 'luminosity',
      backgroundSize: 'cover',
      backgroundPosition: 'center top',
      backgroundAttachment: 'fixed',
    }}>
      {/* Global overlay */}
      <div className="min-h-screen" style={{ background: 'rgba(248,250,255,0.92)' }}>

      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Briefcase className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold text-slate-900">InterviewIQ</span>
            </div>
            <div className="flex items-center gap-4">
              {userName && (
                <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-lg text-slate-700">
                  <UserCircle className="w-5 h-5 text-blue-500" />
                  <span className="font-medium text-sm hidden sm:inline">{userName}</span>
                </div>
              )}
              {onLogout && (
                <button
                  onClick={onLogout}
                  className="flex items-center gap-1.5 text-slate-500 hover:text-red-600 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              )}
              <button
                onClick={onGetStarted}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-1.5 rounded-full text-sm font-semibold mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse inline-block"></span>
            AI-Powered · Real-time Feedback · Speech Recognition
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Master Your Interview Skills with{' '}
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">AI-Powered</span> Practice
          </h1>
          <p className="text-xl text-slate-600 mb-10 leading-relaxed">
            InterviewIQ provides realistic mock interviews tailored to your resume, with multiple interviewer
            personalities and comprehensive performance analytics to boost your confidence and readiness.
          </p>
          <button
            onClick={onGetStarted}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-indigo-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center gap-2"
          >
            Start Your Mock Interview
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-20 grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-md hover:shadow-xl transition-all border border-slate-100 hover:border-slate-300 group"
            >
              <div className={`bg-gradient-to-br ${feature.gradient} w-14 h-14 rounded-xl flex items-center justify-center mb-4 shadow-md group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
              <p className="text-slate-500 text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white/70 backdrop-blur-md rounded-3xl shadow-2xl p-8 md:p-12 border border-slate-200">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">
              Practice with Different Interviewer Personalities
            </h2>
            <p className="text-slate-500 max-w-2xl mx-auto">
              Experience various interview styles to prepare for any situation
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {personalities.map((personality, index) => (
              <div
                key={index}
                className={`relative bg-white rounded-2xl border-2 ${personality.border} p-6 shadow-md hover:shadow-xl transition-all group overflow-hidden`}
              >
                {/* Gradient top bar */}
                <div className={`absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r ${personality.gradient} rounded-t-2xl`} />

                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${personality.gradient} flex items-center justify-center mb-4 shadow-md group-hover:scale-110 transition-transform`}>
                  <personality.icon className="w-7 h-7 text-white" />
                </div>

                {/* Badge */}
                <span className={`inline-block text-xs font-bold px-2.5 py-1 rounded-full mb-3 ${personality.badgeBg}`}>
                  {personality.badge}
                </span>

                <h3 className="text-lg font-bold text-slate-900 mb-2">{personality.name}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{personality.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl shadow-xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Get Detailed Performance Metrics
          </h2>
          <p className="text-xl mb-8 text-blue-50 max-w-2xl mx-auto">
            Track your technical accuracy, language proficiency, confidence level, sentiment, and emotional stability
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg">
              <FileText className="w-5 h-5" />
              <span className="font-medium">Technical Accuracy</span>
            </div>
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg">
              <Mic className="w-5 h-5" />
              <span className="font-medium">Language Proficiency</span>
            </div>
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg">
              <TrendingUp className="w-5 h-5" />
              <span className="font-medium">Confidence Level</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-white/80 backdrop-blur-md border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center gap-2 text-slate-600">
            <Briefcase className="w-5 h-5" />
            <span>InterviewIQ - AI-Based Mock Interview System</span>
          </div>
        </div>
      </footer>
      </div>{/* end overlay */}
    </div>
  );
}
