import { useState } from 'react';
import { Briefcase, Mail, Lock, User, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthPageProps {
  onAuthSuccess: () => void;
}

export default function AuthPage({ onAuthSuccess }: AuthPageProps) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const switchMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login');
    setError('');
    setName('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }

    if (mode === 'signup') {
      if (!name.trim()) {
        setError('Please enter your name');
        return;
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }
    }

    setIsSubmitting(true);
    try {
      const result =
        mode === 'login'
          ? await login(email, password)
          : await register(name, email, password);

      if (result.success) {
        onAuthSuccess();
      } else {
        setError(result.error || 'Something went wrong');
      }
    } catch {
      setError('Unable to connect to server. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left panel — background image */}
      <div
        className="hidden lg:flex lg:w-1/2 xl:w-3/5 relative flex-col justify-between p-12 overflow-hidden"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1400&q=80')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Dark overlay for readability */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 via-slate-900/70 to-slate-800/80" />

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <Briefcase className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">InterviewIQ</span>
          </div>
        </div>

        <div className="relative z-10">
          <h2 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-6">
            Ace Your Next<br />
            <span className="text-blue-300">Interview</span> with<br />
            AI-Powered Practice
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed max-w-md">
            Practice with realistic mock interviews, get instant feedback, and build the confidence to land your dream job.
          </p>
          <div className="mt-10 flex gap-8">
            <div>
              <div className="text-3xl font-bold text-white">4+</div>
              <div className="text-slate-400 text-sm mt-1">Interview Styles</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">AI</div>
              <div className="text-slate-400 text-sm mt-1">Powered Scoring</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">Live</div>
              <div className="text-slate-400 text-sm mt-1">Speech-to-Text</div>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-slate-500 text-xs">
          © 2026 InterviewIQ · AI-Based Mock Interview System
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-white">
      <div className="w-full max-w-md">
        {/* Logo (mobile only) */}
        <div className="text-center mb-8 lg:hidden">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl mb-4 shadow-lg">
            <Briefcase className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">InterviewIQ</h1>
        </div>

        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900">
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h2>
          <p className="text-slate-500 mt-1">
            {mode === 'login' ? 'Sign in to continue to InterviewIQ.' : 'Get started — it only takes a minute.'}
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-0">
          {/* Tab switcher */}
          <div className="flex bg-slate-100 rounded-lg p-1 mb-6 mx-8 mt-8">
            <button
              onClick={() => switchMode()}
              className={`flex-1 py-2.5 text-sm font-semibold rounded-md transition-all ${
                mode === 'login'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => switchMode()}
              className={`flex-1 py-2.5 text-sm font-semibold rounded-md transition-all ${
                mode === 'signup'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm mx-8">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 px-8 pb-8">
            {/* Name (signup only) */}
            {mode === 'signup' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Doe"
                    className="w-full pl-10 pr-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-slate-900 placeholder-slate-400 transition-colors"
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-slate-900 placeholder-slate-400 transition-colors"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-11 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-slate-900 placeholder-slate-400 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password (signup only) */}
            {mode === 'signup' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-slate-900 placeholder-slate-400 transition-colors"
                  />
                </div>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold text-white transition-all ${
                isSubmitting
                  ? 'bg-blue-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
              }`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                </>
              ) : (
                mode === 'login' ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="text-center text-sm text-slate-500 mt-6 mb-8 px-8">
            {mode === 'login' ? (
              <>
                Don't have an account?{' '}
                <button onClick={switchMode} className="text-blue-600 font-semibold hover:underline">
                  Sign Up
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button onClick={switchMode} className="text-blue-600 font-semibold hover:underline">
                  Sign In
                </button>
              </>
            )}
          </p>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          By continuing, you agree to InterviewIQ's Terms of Service and Privacy Policy.
        </p>
      </div>
      </div>
    </div>
  );
}
