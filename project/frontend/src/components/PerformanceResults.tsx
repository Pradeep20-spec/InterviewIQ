import { useEffect, useRef, useState } from 'react';
import { Trophy, Target, MessageCircle, Smile, TrendingUp, BarChart3, RefreshCw, Download, Loader2, Sparkles, Mail, CheckCircle, AlertCircle, Mic, Gauge, Volume2 } from 'lucide-react';
import { InterviewSession } from '../App';
import { aiApi, interviewApi, reportApi } from '../services/api';
import jsPDF from 'jspdf';

interface PerformanceResultsProps {
  session: InterviewSession;
  onRetry: () => void;
}

interface Metric {
  name: string;
  score: number;
  icon: typeof Trophy;
  color: string;
  bgColor: string;
  description: string;
}

interface PerQuestionFeedback {
  question_index: number;
  score: number;
  strength: string;
  improvement: string;
  input_mode?: string;
  delivery?: {
    speaking_pace_wpm: number;
    filler_count: number;
    filler_density: number;   // percentage
    utilization_ratio: number; // percentage
    delivery_quality: number;
    confidence_marker_count: number;
  };
}

export default function PerformanceResults({ session, onRetry }: PerformanceResultsProps) {
  const hasSavedResults = useRef(false);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [overallScore, setOverallScore] = useState(0);
  const [isEvaluating, setIsEvaluating] = useState(true);
  const [aiPowered, setAiPowered] = useState(false);
  const [perQuestionFeedback, setPerQuestionFeedback] = useState<PerQuestionFeedback[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [summaryFeedback, setSummaryFeedback] = useState('');
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailAddress, setEmailAddress] = useState('');
  const [emailName, setEmailName] = useState('');
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [emailStatus, setEmailStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    if (hasSavedResults.current) return;
    hasSavedResults.current = true;

    const runEvaluation = async () => {
      setIsEvaluating(true);

      // Try AI evaluation first
      if (session.sessionId) {
        try {
          const result = await aiApi.evaluateInterview(session.sessionId);
          if (result.success && result.data) {
            const d = result.data;
            setAiPowered(true);
            setPerQuestionFeedback(d.per_question_feedback || []);
            setRecommendations(d.recommendations || []);
            setSummaryFeedback(d.summary_feedback || '');

            const builtMetrics = buildMetrics(
              d.technical_accuracy,
              d.language_proficiency,
              d.confidence_level,
              d.sentiment_score,
              d.emotional_stability,
            );
            setMetrics(builtMetrics);
            setOverallScore(Math.round(d.overall_score));
            setIsEvaluating(false);
            return;
          }
        } catch {
          // AI unavailable, fall through to basic scoring
        }
      }

      // Fallback: basic text-length heuristic scoring
      const responses = session.responses || [];
      const avgLen = responses.reduce((s, r) => s + r.answer.length, 0) / Math.max(responses.length, 1);
      const base = Math.min(90, 40 + avgLen * 0.3);

      const builtMetrics = buildMetrics(
        Math.round(base + 2),
        Math.round(base + 5),
        Math.round(base - 3),
        Math.round(base + 1),
        Math.round(base + 3),
      );
      setMetrics(builtMetrics);
      setOverallScore(Math.round(builtMetrics.reduce((s, m) => s + m.score, 0) / builtMetrics.length));
      setRecommendations([
        'Continue practicing with different interviewer personalities.',
        'Focus on technical accuracy by reviewing fundamental concepts.',
        'Improve confidence through mock interviews.',
        'Maintain emotional stability with stress management techniques.',
      ]);

      // Save fallback results to backend
      if (session.sessionId) {
        interviewApi.saveResults({
          session_id: session.sessionId,
          technical_accuracy: builtMetrics[0].score,
          language_proficiency: builtMetrics[1].score,
          confidence_level: builtMetrics[2].score,
          sentiment_score: builtMetrics[3].score,
          emotional_stability: builtMetrics[4].score,
          feedback: `Overall score: ${Math.round(base + 1.6)}%`,
        }).catch(() => {});
      }

      setIsEvaluating(false);
    };

    runEvaluation();
  }, []);

  function buildMetrics(tech: number, lang: number, conf: number, sent: number, emo: number): Metric[] {
    return [
      { name: 'Technical Accuracy', score: tech, icon: Target, color: 'text-blue-600', bgColor: 'bg-blue-50', description: 'Correctness and depth of technical responses' },
      { name: 'Language Proficiency', score: lang, icon: MessageCircle, color: 'text-emerald-600', bgColor: 'bg-emerald-50', description: 'Clarity, grammar, and communication effectiveness' },
      { name: 'Confidence Level', score: conf, icon: TrendingUp, color: 'text-orange-600', bgColor: 'bg-orange-50', description: 'Voice tone, pace, and assertiveness' },
      { name: 'Sentiment Score', score: sent, icon: Smile, color: 'text-pink-600', bgColor: 'bg-pink-50', description: 'Overall positivity and enthusiasm' },
      { name: 'Emotional Stability', score: emo, icon: BarChart3, color: 'text-cyan-600', bgColor: 'bg-cyan-50', description: 'Composure and consistency throughout' },
    ];
  }

  const downloadPdfReport = () => {
    const doc = new jsPDF();
    const pageW = doc.internal.pageSize.getWidth();
    const margin = 18;
    const cW = pageW - margin * 2;
    let y = 0;

    const nextLine = (extra = 6) => { y += extra; };
    const checkPage = (need = 18) => {
      if (y + need > 275) { doc.addPage(); y = 20; }
    };

    // ── Header bar ───────────────────────────────────────────
    doc.setFillColor(37, 99, 235);
    doc.rect(0, 0, pageW, 28, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('InterviewIQ', margin, 12);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text('AI-Powered Performance Report', margin, 20);
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    doc.text(dateStr, pageW - margin, 20, { align: 'right' });
    y = 36;

    // ── Summary strip ────────────────────────────────────────
    doc.setFillColor(241, 245, 249);
    doc.roundedRect(margin - 2, y - 5, cW + 4, 18, 2, 2, 'F');
    doc.setTextColor(60, 60, 60);
    doc.setFontSize(9.5);
    doc.setFont('helvetica', 'normal');
    doc.text(`Interview Type:`, margin + 2, y + 3);
    doc.setFont('helvetica', 'bold');
    doc.text(getPersonalityName(session.personality || 'friendly'), margin + 34, y + 3);
    doc.setFont('helvetica', 'normal');
    doc.text(`Questions Answered:`, margin + 85, y + 3);
    doc.setFont('helvetica', 'bold');
    doc.text(`${session.responses?.length || 0}`, margin + 122, y + 3);
    doc.setFont('helvetica', 'normal');
    doc.text(`Overall Score:`, margin + 130, y + 3);
    const [sr, sg, sb] = overallScore >= 85 ? [22, 163, 74] : overallScore >= 70 ? [37, 99, 235] : overallScore >= 50 ? [234, 88, 12] : [220, 38, 38];
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(sr, sg, sb);
    doc.text(`${overallScore}% — ${getScoreLabel(overallScore)}`, margin + 157, y + 3);
    y += 22;

    // ── Section: Performance Metrics ────────────────────────
    doc.setTextColor(15, 23, 42);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Performance Metrics', margin, y);
    nextLine(8);

    metrics.forEach(m => {
      checkPage(13);
      const [fr, fg, fb2] = m.score >= 85 ? [22, 163, 74] : m.score >= 70 ? [37, 99, 235] : m.score >= 50 ? [234, 88, 12] : [220, 38, 38];
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9.5);
      doc.setTextColor(60, 60, 60);
      doc.text(m.name, margin, y);
      // Bar bg
      const bX = margin + 52; const bW = 80; const bH = 4;
      doc.setFillColor(220, 220, 220);
      doc.roundedRect(bX, y - 3.5, bW, bH, 1.5, 1.5, 'F');
      // Bar fill
      doc.setFillColor(fr, fg, fb2);
      doc.roundedRect(bX, y - 3.5, (m.score / 100) * bW, bH, 1.5, 1.5, 'F');
      // Score label
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(fr, fg, fb2);
      doc.text(`${m.score}%`, bX + bW + 4, y);
      nextLine(9);
    });
    nextLine(2);

    // Horizontal divider
    doc.setDrawColor(200, 210, 220);
    doc.line(margin, y, pageW - margin, y);
    nextLine(8);

    // ── Section: Per-Question Feedback ───────────────────────
    checkPage(20);
    doc.setTextColor(15, 23, 42);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Question-by-Question Feedback', margin, y);
    nextLine(8);

    (session.responses || []).forEach((resp, i) => {
      checkPage(35);
      const fb = perQuestionFeedback.find(f => f.question_index === i);

      // Number badge
      doc.setFillColor(37, 99, 235);
      doc.circle(margin + 4, y - 1.5, 4, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'bold');
      doc.text(`${i + 1}`, margin + 4, y, { align: 'center' });

      // Question
      doc.setTextColor(20, 20, 40);
      doc.setFontSize(9.5);
      doc.setFont('helvetica', 'bold');
      const qL = doc.splitTextToSize(resp.question, cW - 12);
      doc.text(qL, margin + 12, y);
      y += qL.length * 5.5;

      // Answer
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(90, 90, 110);
      doc.setFontSize(8.5);
      const aL = doc.splitTextToSize(resp.answer.length > 300 ? resp.answer.slice(0, 300) + '…' : resp.answer, cW - 12);
      checkPage(aL.length * 5 + 14);
      doc.text(aL, margin + 12, y);
      y += aL.length * 5;

      if (fb) {
        checkPage(18);
        const [qsr, qsg, qsb] = fb.score >= 70 ? [22, 163, 74] : fb.score >= 40 ? [234, 88, 12] : [220, 38, 38];
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(9);
        doc.setTextColor(qsr, qsg, qsb);
        doc.text(`Score: ${fb.score}/100`, margin + 12, y + 1);
        nextLine(6);
        // Strength
        doc.setFillColor(240, 253, 244);
        const strL = doc.splitTextToSize(`✓ ${fb.strength}`, cW - 14);
        checkPage(strL.length * 5 + 5);
        doc.roundedRect(margin + 12, y - 3, cW - 14, strL.length * 5 + 2, 1, 1, 'F');
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8.5);
        doc.setTextColor(21, 128, 61);
        doc.text(strL, margin + 14, y);
        y += strL.length * 5 + 2;
        // Improvement
        const impL = doc.splitTextToSize(`↑ ${fb.improvement}`, cW - 14);
        checkPage(impL.length * 5 + 5);
        doc.setFillColor(255, 251, 235);
        doc.roundedRect(margin + 12, y - 1, cW - 14, impL.length * 5 + 2, 1, 1, 'F');
        doc.setTextColor(146, 64, 14);
        doc.text(impL, margin + 14, y + 1);
        y += impL.length * 5 + 4;
      }
      nextLine(5);
    });

    // Horizontal divider
    checkPage(15);
    doc.setDrawColor(200, 210, 220);
    doc.line(margin, y, pageW - margin, y);
    nextLine(8);

    // ── Section: Recommendations ─────────────────────────────
    checkPage(25);
    doc.setFillColor(239, 246, 255);
    const recH = (summaryFeedback ? 18 : 0) + recommendations.length * 14 + 18;
    doc.roundedRect(margin - 2, y - 5, cW + 4, Math.min(recH, 260), 3, 3, 'F');
    doc.setTextColor(15, 23, 42);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Key Recommendations', margin + 2, y + 2);
    nextLine(10);

    if (summaryFeedback) {
      const sfL = doc.splitTextToSize(summaryFeedback, cW - 6);
      checkPage(sfL.length * 5.5 + 6);
      doc.setFont('helvetica', 'italic');
      doc.setFontSize(9);
      doc.setTextColor(55, 75, 120);
      doc.text(sfL, margin + 2, y);
      y += sfL.length * 5.5 + 5;
    }

    recommendations.forEach((rec, ri) => {
      checkPage(16);
      doc.setFillColor(37, 99, 235);
      doc.circle(margin + 4, y - 1.5, 3, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'bold');
      doc.text(`${ri + 1}`, margin + 4, y, { align: 'center' });
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(20, 40, 80);
      const recL = doc.splitTextToSize(rec, cW - 12);
      doc.text(recL, margin + 12, y);
      y += recL.length * 5.5 + 4;
    });

    // ── Footer on every page ──────────────────────────────────
    const pages = (doc as any).getNumberOfPages();
    for (let p = 1; p <= pages; p++) {
      doc.setPage(p);
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(160, 160, 170);
      doc.text(
        `InterviewIQ — AI-Powered Interview Platform  |  Generated ${dateStr}`,
        pageW / 2, 291, { align: 'center' },
      );
      doc.text(`Page ${p} of ${pages}`, pageW - margin, 291, { align: 'right' });
    }

    doc.save(`InterviewIQ_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
  };

  const handleSendEmail = async () => {
    if (!emailAddress.trim()) return;
    setIsSendingEmail(true);
    setEmailStatus(null);

    try {
      if (session.sessionId) {
        const result = await reportApi.emailReport(session.sessionId, emailAddress.trim(), emailName.trim() || undefined);
        if (result.success && result.data) {
          if (result.data.delivered) {
            setEmailStatus({ type: 'success', message: `Report sent successfully to ${emailAddress}!` });
          } else if (result.data.fallback && result.data.report_text) {
            // SMTP not configured — auto-download the report
            const blob = new Blob([result.data.report_text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `InterviewIQ_Report_${new Date().toISOString().slice(0, 10)}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            setEmailStatus({ type: 'success', message: 'Email service is being set up. Report has been downloaded instead.' });
          } else {
            setEmailStatus({ type: 'error', message: result.data.message || 'Failed to send report.' });
          }
        } else {
          setEmailStatus({ type: 'error', message: result.error || 'Failed to send report.' });
        }
      } else {
        // No session ID — download locally
        downloadPdfReport();
        setEmailStatus({ type: 'success', message: 'Report downloaded (no session available for email delivery).' });
      }
    } catch {
      setEmailStatus({ type: 'error', message: 'Network error. Please try downloading instead.' });
    } finally {
      setIsSendingEmail(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Fair';
    return 'Needs Improvement';
  };

  const getPersonalityName = (personality: string) => {
    const names: Record<string, string> = {
      friendly: 'Friendly HR',
      technical: 'Strict Technical',
      stress: 'Stress Interview',
      panel: 'Panel Interview'
    };
    return names[personality] || personality;
  };

  if (isEvaluating) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-slate-600 text-lg font-medium">AI is evaluating your interview performance...</p>
          <p className="text-slate-500 text-sm mt-2">Analysing responses, scoring, and generating feedback</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
            <Trophy className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Interview Complete!
          </h1>
          <p className="text-slate-600 text-lg">
            {aiPowered ? 'AI-powered performance analysis' : 'Here\'s your detailed performance analysis'}
          </p>
          {aiPowered && (
            <div className="inline-flex items-center gap-1 mt-2 px-3 py-1 rounded-full bg-purple-50 text-purple-700 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              Evaluated by InterviewIQ AI
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8 mb-6">
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 bg-slate-50 rounded-xl">
              <div className="text-sm text-slate-600 mb-1">Interview Type</div>
              <div className="text-xl font-bold text-slate-900">
                {getPersonalityName(session.personality || 'friendly')}
              </div>
            </div>
            <div className="text-center p-6 bg-slate-50 rounded-xl">
              <div className="text-sm text-slate-600 mb-1">Questions Answered</div>
              <div className="text-xl font-bold text-slate-900">
                {session.responses?.length || 0}
              </div>
            </div>
            <div className="text-center p-6 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl text-white">
              <div className="text-sm text-blue-50 mb-1">Overall Score</div>
              <div className="text-4xl font-bold">{overallScore}%</div>
              <div className="text-sm font-medium text-blue-50 mt-1">
                {getScoreLabel(overallScore)}
              </div>
            </div>
          </div>

          <div className="border-t border-slate-200 pt-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Performance Metrics</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {metrics.map((metric, index) => {
                const Icon = metric.icon;
                return (
                  <div
                    key={index}
                    className="border-2 border-slate-200 rounded-xl p-6 hover:border-blue-300 transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`${metric.bgColor} w-12 h-12 rounded-lg flex items-center justify-center`}>
                          <Icon className={`w-6 h-6 ${metric.color}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900">{metric.name}</h3>
                          <p className="text-sm text-slate-600">{metric.description}</p>
                        </div>
                      </div>
                      <div className={`text-2xl font-bold ${getScoreColor(metric.score)}`}>
                        {metric.score}%
                      </div>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-3">
                      <div
                        className={`${metric.bgColor} h-3 rounded-full transition-all duration-500`}
                        style={{ width: `${metric.score}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {session.responses && session.responses.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8 mb-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Your Responses</h2>
            <div className="space-y-4">
              {session.responses.map((response, index) => {
                const fb = perQuestionFeedback.find(f => f.question_index === index);
                return (
                  <div
                    key={index}
                    className="border-2 border-slate-200 rounded-lg p-4 hover:border-blue-300 transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-100 text-blue-600 font-bold w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-slate-900 mb-2">{response.question}</p>
                        <p className="text-slate-600 text-sm mb-2">{response.answer}</p>
                        {fb && (
                          <div className="mt-3 space-y-2">
                            <div className="grid sm:grid-cols-3 gap-2 text-xs">
                              <div className="bg-slate-50 rounded px-3 py-2">
                                <span className="font-medium text-slate-500">Score:</span>{' '}
                                <span className={`font-bold ${fb.score >= 70 ? 'text-green-600' : fb.score >= 40 ? 'text-orange-600' : 'text-red-600'}`}>{fb.score}/100</span>
                              </div>
                              <div className="bg-green-50 rounded px-3 py-2 text-green-700">
                                <span className="font-medium">Strength:</span> {fb.strength}
                              </div>
                              <div className="bg-amber-50 rounded px-3 py-2 text-amber-700">
                                <span className="font-medium">Improve:</span> {fb.improvement}
                              </div>
                            </div>

                            {/* Video / Audio delivery metrics */}
                            {fb.delivery && (
                              <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-3">
                                <div className="flex items-center gap-1.5 mb-2">
                                  {fb.input_mode === 'video' ? <Volume2 className="w-3.5 h-3.5 text-blue-500" /> : <Mic className="w-3.5 h-3.5 text-blue-500" />}
                                  <span className="text-xs font-semibold text-blue-700 uppercase tracking-wide">
                                    {fb.input_mode === 'video' ? 'Video' : 'Audio'} Delivery Analysis
                                  </span>
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                                  <div>
                                    <div className="flex items-center gap-1 text-slate-500 mb-0.5">
                                      <Gauge className="w-3 h-3" />
                                      Speaking Pace
                                    </div>
                                    <div className={`font-bold ${
                                      fb.delivery.speaking_pace_wpm >= 131 && fb.delivery.speaking_pace_wpm <= 165
                                        ? 'text-green-600'
                                        : fb.delivery.speaking_pace_wpm > 0
                                        ? 'text-orange-600'
                                        : 'text-slate-400'
                                    }`}>
                                      {fb.delivery.speaking_pace_wpm > 0 ? `${fb.delivery.speaking_pace_wpm} WPM` : 'N/A'}
                                    </div>
                                    <div className="text-slate-400 text-[10px]">ideal: 131–165 WPM</div>
                                  </div>
                                  <div>
                                    <div className="text-slate-500 mb-0.5">Filler Words</div>
                                    <div className={`font-bold ${
                                      fb.delivery.filler_density < 3 ? 'text-green-600'
                                      : fb.delivery.filler_density < 8 ? 'text-orange-600'
                                      : 'text-red-600'
                                    }`}>
                                      {fb.delivery.filler_count} ({fb.delivery.filler_density}%)
                                    </div>
                                    <div className="text-slate-400 text-[10px]">um, uh, like, you know…</div>
                                  </div>
                                  <div>
                                    <div className="text-slate-500 mb-0.5">Delivery Score</div>
                                    <div className={`font-bold ${
                                      fb.delivery.delivery_quality >= 70 ? 'text-green-600'
                                      : fb.delivery.delivery_quality >= 50 ? 'text-orange-600'
                                      : 'text-red-600'
                                    }`}>
                                      {fb.delivery.delivery_quality}/100
                                    </div>
                                    <div className="text-slate-400 text-[10px]">confidence + stability + sentiment</div>
                                  </div>
                                  <div>
                                    <div className="text-slate-500 mb-0.5">Time Used</div>
                                    <div className={`font-bold ${fb.delivery.utilization_ratio >= 70 ? 'text-green-600' : 'text-orange-600'}`}>
                                      {fb.delivery.utilization_ratio}%
                                    </div>
                                    <div className="text-slate-400 text-[10px]">of recording time spoken</div>
                                  </div>
                                  <div>
                                    <div className="text-slate-500 mb-0.5">Strong Phrases</div>
                                    <div className={`font-bold ${fb.delivery.confidence_marker_count >= 2 ? 'text-green-600' : fb.delivery.confidence_marker_count >= 1 ? 'text-orange-600' : 'text-slate-500'}`}>
                                      {fb.delivery.confidence_marker_count}
                                    </div>
                                    <div className="text-slate-400 text-[10px]">confident action phrases</div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl border-2 border-blue-200 p-8 mb-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            Key Recommendations
            {aiPowered && <Sparkles className="w-5 h-5 text-purple-500" />}
          </h2>

          {summaryFeedback && (
            <p className="text-slate-700 mb-4 bg-white/60 rounded-lg p-4 border border-blue-100">
              {summaryFeedback}
            </p>
          )}

          <div className="space-y-3">
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-slate-700">{rec}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={onRetry}
            className="flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
          >
            <RefreshCw className="w-5 h-5" />
            Try Another Interview
          </button>
          <button
            onClick={downloadPdfReport}
            className="flex items-center gap-2 bg-white text-slate-700 px-8 py-3 rounded-lg font-semibold hover:bg-slate-50 transition-all shadow-md border-2 border-slate-300"
          >
            <Download className="w-5 h-5" />
            Download PDF
          </button>
          <button
            onClick={() => { setShowEmailModal(true); setEmailStatus(null); }}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
          >
            <Mail className="w-5 h-5" />
            Email Report
          </button>
        </div>

        {/* Email Report Modal */}
        {showEmailModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 relative">
              <button
                onClick={() => setShowEmailModal(false)}
                className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 text-xl font-bold"
              >
                &times;
              </button>

              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-14 h-14 bg-purple-100 rounded-full mb-3">
                  <Mail className="w-7 h-7 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">Send Report via Email</h3>
                <p className="text-slate-500 text-sm mt-1">Receive a copy of your performance report</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Your Name (optional)</label>
                  <input
                    type="text"
                    value={emailName}
                    onChange={(e) => setEmailName(e.target.value)}
                    placeholder="John Doe"
                    className="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address *</label>
                  <input
                    type="email"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full px-4 py-2.5 border-2 border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none text-slate-900"
                  />
                </div>

                {emailStatus && (
                  <div className={`flex items-start gap-2 p-3 rounded-lg text-sm ${
                    emailStatus.type === 'success'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    {emailStatus.type === 'success'
                      ? <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      : <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    }
                    <p>{emailStatus.message}</p>
                  </div>
                )}

                <button
                  onClick={handleSendEmail}
                  disabled={!emailAddress.trim() || isSendingEmail}
                  className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold transition-all ${
                    emailAddress.trim() && !isSendingEmail
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md'
                      : 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  {isSendingEmail ? (
                    <><Loader2 className="w-5 h-5 animate-spin" /> Sending...</>
                  ) : (
                    <><Mail className="w-5 h-5" /> Send Report</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
