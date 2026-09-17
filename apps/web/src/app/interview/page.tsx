"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  interviewsApi,
  InterviewSessionDetail,
  InterviewSessionSummary,
  InterviewQuestionItem,
  InterviewTurnItem,
  InterviewType,
  InterviewDifficulty,
} from "@/lib/api/interviews";
import {
  Mic,
  MicOff,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  TrendingUp,
  Award,
  Layers,
  HelpCircle,
  Play,
  RotateCcw,
  BookOpen,
  Send,
  MessageSquare,
  Cpu,
  BrainCircuit,
  ChevronRight,
  ChevronDown,
  Check,
  CheckCheck,
  RefreshCw,
  Target,
  Sliders,
  Terminal,
} from "lucide-react";

export default function MockInterviewPage() {
  const { user, token } = useAuth();

  // Setup Configuration State
  const [selectedRole, setSelectedRole] = useState<string>("AI Engineer");
  const [selectedType, setSelectedType] = useState<InterviewType>("MIXED");
  const [selectedDifficulty, setSelectedDifficulty] = useState<InterviewDifficulty>("MEDIUM");
  const [questionCount, setQuestionCount] = useState<number>(3);

  // Active Simulation State
  const [session, setSession] = useState<InterviewSessionDetail | null>(null);
  const [historicalSessions, setHistoricalSessions] = useState<InterviewSessionSummary[]>([]);
  const [responseText, setResponseText] = useState<string>("");
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [audioTimer, setAudioTimer] = useState<number>(0);

  // Interaction & UI State
  const [loading, setLoading] = useState<boolean>(true);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [isSubmittingTurn, setIsSubmittingTurn] = useState<boolean>(false);
  const [latestTurnFeedback, setLatestTurnFeedback] = useState<InterviewTurnItem | null>(null);
  const [showStarGuide, setShowStarGuide] = useState<boolean>(false);
  const [expandedExemplary, setExpandedExemplary] = useState<boolean>(false);

  // Toast State
  const [toast, setToast] = useState<{ type: "success" | "error" | "info"; text: string } | null>(null);

  const showToast = (type: "success" | "error" | "info", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4500);
  };

  // Audio timer ticker
  useEffect(() => {
    let interval: any;
    if (isRecording) {
      interval = setInterval(() => {
        setAudioTimer((prev) => prev + 1);
      }, 1000);
    } else {
      setAudioTimer(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  // Load Active Session and Historical List
  const loadInitialData = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const [activeRes, listRes] = await Promise.all([
        interviewsApi.getActiveSession(token),
        interviewsApi.listSessions(token),
      ]);

      if (activeRes.data) {
        setSession(activeRes.data);
      }
      if (listRes.data) {
        setHistoricalSessions(listRes.data);
      }
    } catch (err) {
      console.error("Error loading interview data", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle Starting a New Interview
  const handleStartInterview = async () => {
    if (!token) {
      showToast("error", "Please sign in to start a placement interview simulation.");
      return;
    }

    setIsCreating(true);
    setLatestTurnFeedback(null);
    setResponseText("");
    try {
      const res = await interviewsApi.createSession(
        {
          interview_type: selectedType,
          target_role: selectedRole,
          difficulty: selectedDifficulty,
          total_questions: questionCount,
        },
        token
      );

      if (res.data) {
        setSession(res.data);
        showToast(
          "success",
          `Started ${res.data.target_role} simulation (${res.data.total_questions} rounds)!`
        );
      } else {
        showToast("error", res.error || "Failed to create interview session.");
      }
    } catch (err) {
      showToast("error", "Error creating interview session.");
    } finally {
      setIsCreating(false);
    }
  };

  // Handle Submitting Answer for Current Turn
  const handleSubmitResponse = async () => {
    if (!token || !session) return;
    if (!responseText.trim()) {
      showToast("error", "Please type or speak your answer before submitting.");
      return;
    }

    setIsSubmittingTurn(true);
    try {
      const res = await interviewsApi.respondToQuestion(
        session.id,
        {
          candidate_response_text: responseText,
          audio_duration_seconds: audioTimer > 0 ? audioTimer : undefined,
        },
        token
      );

      if (res.data) {
        setLatestTurnFeedback(res.data.turn_response);
        setResponseText("");
        setIsRecording(false);

        // Fetch refreshed session state
        const updatedSession = await interviewsApi.getSession(session.id, token);
        if (updatedSession.data) {
          setSession(updatedSession.data);
        }

        if (res.data.is_session_completed) {
          showToast(
            "success",
            `Interview completed! Overall score: ${res.data.overall_session_score}/100 verified in Career Twin.`
          );
          // Refresh historical sessions list
          const listRes = await interviewsApi.listSessions(token);
          if (listRes.data) setHistoricalSessions(listRes.data);
        } else {
          showToast(
            "info",
            `Turn score: ${res.data.turn_response.score}/100. Moving to Question ${
              session.current_question_index + 2
            }.`
          );
        }
      } else {
        showToast("error", res.error || "Failed to evaluate answer.");
      }
    } catch (err) {
      showToast("error", "Error submitting response.");
    } finally {
      setIsSubmittingTurn(false);
    }
  };

  const handleNextQuestion = () => {
    setLatestTurnFeedback(null);
    setResponseText("");
    setExpandedExemplary(false);
  };

  const currentQuestion =
    session && session.questions && session.current_question_index < session.questions.length
      ? session.questions[session.current_question_index]
      : null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0B0F19] via-[#0D1322] to-[#0B0F19] text-white p-4 md:p-8">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl border backdrop-blur-xl shadow-2xl transition-all duration-300 ${
            toast.type === "success"
              ? "bg-emerald-950/80 border-emerald-500/40 text-emerald-200"
              : toast.type === "error"
              ? "bg-rose-950/80 border-rose-500/40 text-rose-200"
              : "bg-sky-950/80 border-sky-500/40 text-sky-200"
          }`}
        >
          {toast.type === "success" && <CheckCheck className="w-5 h-5 text-emerald-400" />}
          {toast.type === "error" && <AlertCircle className="w-5 h-5 text-rose-400" />}
          {toast.type === "info" && <Sparkles className="w-5 h-5 text-sky-400" />}
          <span className="text-sm font-medium">{toast.text}</span>
        </div>
      )}

      {/* Top Hero Banner */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-zinc-800/80">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-600/20 border border-purple-500/30 text-purple-400">
                <Mic className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-semibold tracking-wider text-purple-400 uppercase">
                  Phase 9 — Multi-Modal Interview Agent
                </span>
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                  Mock Interview Simulation Arena
                </h1>
              </div>
            </div>
            <p className="mt-2 text-sm text-zinc-400 max-w-2xl">
              Multi-round technical deep dives, STAR behavioral evaluations, real-time rubric feedback, and verifiable Career Twin evidence generation.
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href="/learning"
              className="px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-sm font-medium text-zinc-200 flex items-center gap-2 transition"
            >
              <BookOpen className="w-4 h-4 text-cyan-400" />
              Learning Roadmap
            </Link>
            <Link
              href="/dsa"
              className="px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-sm font-medium text-zinc-200 flex items-center gap-2 transition"
            >
              <Terminal className="w-4 h-4 text-indigo-400" />
              DSA Sandbox
            </Link>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto space-y-8">
        {/* ========================================================== */}
        {/* STAGE 1: LOBBY / SETUP (WHEN NO ACTIVE SESSION)            */}
        {/* ========================================================== */}
        {(!session || session.status === "COMPLETED") && (
          <div className="space-y-8">
            {/* Setup Config Card */}
            <div className="bg-[#101524] border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
                <div className="flex items-center gap-2.5">
                  <Sliders className="w-5 h-5 text-purple-400" />
                  <h2 className="text-lg font-bold text-white">Configure Interview Simulation</h2>
                </div>
                <span className="text-xs text-zinc-500 font-mono">STAR & TECHNICAL RUBRIC</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Target Role */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-zinc-300">Target Role Benchmark</label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full bg-[#0B0F19] border border-zinc-700 rounded-xl px-3.5 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-purple-500"
                  >
                    <option value="AI Engineer">AI Engineer (LangChain / PyTorch)</option>
                    <option value="Backend Engineer">Backend Engineer (Postgres / Redis)</option>
                    <option value="Full-Stack Engineer">Full-Stack Engineer (React / Next.js)</option>
                    <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer (K8s / CI-CD)</option>
                    <option value="Data Scientist">Data Scientist (Applied ML)</option>
                  </select>
                </div>

                {/* Interview Mode */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-zinc-300">Interview Mode</label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value as InterviewType)}
                    className="w-full bg-[#0B0F19] border border-zinc-700 rounded-xl px-3.5 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-purple-500"
                  >
                    <option value="MIXED">Full Placement Simulation (Mixed)</option>
                    <option value="TECHNICAL">Technical Deep Dive</option>
                    <option value="SYSTEM_DESIGN">System Design & Tradeoffs</option>
                    <option value="BEHAVIORAL">Behavioral (STAR Format)</option>
                  </select>
                </div>

                {/* Difficulty */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-zinc-300">Difficulty Caliber</label>
                  <select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value as InterviewDifficulty)}
                    className="w-full bg-[#0B0F19] border border-zinc-700 rounded-xl px-3.5 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-purple-500"
                  >
                    <option value="EASY">Standard Campus Placement</option>
                    <option value="MEDIUM">Tier-1 Product Company</option>
                    <option value="HARD">FAANG / High-Frequency Caliber</option>
                  </select>
                </div>

                {/* Question Count & Start Button */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-zinc-300">Rounds Length</label>
                  <div className="flex items-center gap-3">
                    <select
                      value={questionCount}
                      onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                      className="bg-[#0B0F19] border border-zinc-700 rounded-xl px-3 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-purple-500"
                    >
                      <option value="2">2 Rounds (Sprint)</option>
                      <option value="3">3 Rounds (Standard)</option>
                      <option value="5">5 Rounds (Comprehensive)</option>
                    </select>

                    <button
                      onClick={handleStartInterview}
                      disabled={isCreating}
                      className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-bold text-sm shadow-lg shadow-purple-500/20 flex items-center justify-center gap-2 transition disabled:opacity-50"
                    >
                      {isCreating ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Synthesizing...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" />
                          Start Simulation
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Historical Interview Scorecards */}
            {historicalSessions.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Award className="w-5 h-5 text-purple-400" />
                  Past Interview Performance & Scorecards
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {historicalSessions.map((hs) => (
                    <div
                      key={hs.id}
                      onClick={async () => {
                        if (token) {
                          const res = await interviewsApi.getSession(hs.id, token);
                          if (res.data) setSession(res.data);
                        }
                      }}
                      className="p-5 rounded-2xl bg-[#101524] border border-zinc-800 hover:border-purple-500/40 cursor-pointer transition shadow-lg space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                          {hs.interview_type}
                        </span>
                        <span className="text-xs text-zinc-500">
                          {new Date(hs.started_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div>
                        <h4 className="text-sm font-bold text-white">{hs.title}</h4>
                        <p className="text-xs text-zinc-400 mt-1">{hs.target_role}</p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80">
                        <span className="text-xs text-zinc-400">Scorecard:</span>
                        <span className="text-sm font-extrabold text-cyan-400">
                          {hs.overall_score ? `${hs.overall_score}/100` : "In Progress"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================== */}
        {/* STAGE 2: LIVE INTERVIEW TURN-BY-TURN SIMULATION            */}
        {/* ========================================================== */}
        {session && session.status === "IN_PROGRESS" && currentQuestion && (
          <div className="space-y-6">
            {/* Header Progress Bar */}
            <div className="bg-[#101524] border border-zinc-800 rounded-2xl p-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                  Round {session.current_question_index + 1} of {session.total_questions}
                </span>
                <span className="text-zinc-600">•</span>
                <span className="text-xs font-mono text-zinc-400">{currentQuestion.category}</span>
              </div>

              <div className="flex items-center gap-3">
                {isRecording && (
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono animate-pulse">
                    <span className="h-2 w-2 rounded-full bg-rose-400" />
                    Recording: {Math.floor(audioTimer / 60)}:{(audioTimer % 60).toString().padStart(2, "0")}
                  </div>
                )}
                <button
                  onClick={() => setShowStarGuide(!showStarGuide)}
                  className="px-3 py-1 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                  STAR Guide
                </button>
              </div>
            </div>

            {/* STAR Framework Drawer (Collapsible) */}
            {showStarGuide && (
              <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200/90 grid grid-cols-1 md:grid-cols-4 gap-4 animate-in fade-in">
                <div>
                  <strong className="text-amber-400 block mb-1">1. Situation</strong>
                  <p className="text-zinc-400">Context, project scale, and the specific problem you encountered.</p>
                </div>
                <div>
                  <strong className="text-amber-400 block mb-1">2. Task</strong>
                  <p className="text-zinc-400">Your direct engineering responsibility and target constraints.</p>
                </div>
                <div>
                  <strong className="text-amber-400 block mb-1">3. Action</strong>
                  <p className="text-zinc-400">Concrete algorithms, tools (LangChain, Postgres, Redis), and architecture decisions.</p>
                </div>
                <div>
                  <strong className="text-amber-400 block mb-1">4. Result</strong>
                  <p className="text-zinc-400">Measurable business/performance metric (e.g. latency reduced by 40%, 10k QPS).</p>
                </div>
              </div>
            )}

            {/* Question Prompt Card */}
            <div className="bg-[#121829] border border-purple-500/30 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-start justify-between gap-4">
                <h3 className="text-lg md:text-xl font-bold text-white leading-snug">
                  {currentQuestion.question_text}
                </h3>
              </div>

              {currentQuestion.context_or_scenario && (
                <div className="p-3.5 rounded-xl bg-[#0B0F19] border border-zinc-800 text-xs text-zinc-300 leading-relaxed">
                  <span className="text-zinc-500 font-bold uppercase block text-[10px] mb-1">Scenario Context</span>
                  {currentQuestion.context_or_scenario}
                </div>
              )}

              {currentQuestion.target_competencies.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap pt-1">
                  <span className="text-xs text-zinc-500">Evaluated Competencies:</span>
                  {currentQuestion.target_competencies.map((comp) => (
                    <span
                      key={comp}
                      className="text-[11px] font-mono px-2.5 py-0.5 rounded-md bg-purple-500/10 text-purple-300 border border-purple-500/20"
                    >
                      {comp}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Live Feedback Display after submitting turn */}
            {latestTurnFeedback ? (
              <div className="bg-[#101524] border border-cyan-500/40 rounded-2xl p-6 shadow-2xl space-y-6 animate-in fade-in zoom-in-95">
                <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-extrabold text-lg">
                      {latestTurnFeedback.score}
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">AI Rubric Evaluation</h4>
                      <p className="text-xs text-zinc-400">Instant turn-by-turn performance breakdown</p>
                    </div>
                  </div>

                  <button
                    onClick={handleNextQuestion}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-500/20 flex items-center gap-2 transition"
                  >
                    <span>Proceed to Next Round</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>

                {/* 4-Rubric Score Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                  <div className="p-3 rounded-xl bg-[#0B0F19] border border-zinc-800">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold block">Technical Depth</span>
                    <span className="text-base font-extrabold text-indigo-400">
                      {latestTurnFeedback.technical_depth_score}/100
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-[#0B0F19] border border-zinc-800">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold block">STAR Structure</span>
                    <span className="text-base font-extrabold text-purple-400">
                      {latestTurnFeedback.structure_star_score}/100
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-[#0B0F19] border border-zinc-800">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold block">Communication</span>
                    <span className="text-base font-extrabold text-cyan-400">
                      {latestTurnFeedback.communication_clarity_score}/100
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-[#0B0F19] border border-zinc-800">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold block">Tradeoffs</span>
                    <span className="text-base font-extrabold text-emerald-400">
                      {latestTurnFeedback.tradeoff_score}/100
                    </span>
                  </div>
                </div>

                {/* Strengths & Improvements */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      Key Strengths Identified
                    </span>
                    <ul className="text-xs text-zinc-300 space-y-1 list-disc list-inside">
                      {latestTurnFeedback.strengths.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                    <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                      <AlertCircle className="w-4 h-4" />
                      Actionable Improvement Tips
                    </span>
                    <ul className="text-xs text-zinc-300 space-y-1 list-disc list-inside">
                      {latestTurnFeedback.improvements.map((imp, idx) => (
                        <li key={idx}>{imp}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Exemplary Model Answer (Expandable) */}
                {latestTurnFeedback.exemplary_answer && (
                  <div className="border border-zinc-800 rounded-xl overflow-hidden">
                    <button
                      onClick={() => setExpandedExemplary(!expandedExemplary)}
                      className="w-full p-3 bg-zinc-900/80 flex items-center justify-between text-xs font-bold text-zinc-300 hover:text-white"
                    >
                      <span className="flex items-center gap-1.5">
                        <Sparkles className="w-4 h-4 text-purple-400" />
                        View Staff Engineer Exemplary Response
                      </span>
                      <ChevronDown className={`w-4 h-4 transition ${expandedExemplary ? "rotate-180" : ""}`} />
                    </button>
                    {expandedExemplary && (
                      <div className="p-4 bg-[#0B0F19] text-xs text-zinc-300 leading-relaxed">
                        {latestTurnFeedback.exemplary_answer}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              /* Response Textarea & Mic Action Area */
              <div className="bg-[#101524] border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                    Your Response
                  </label>
                  <button
                    onClick={() => setIsRecording(!isRecording)}
                    className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition ${
                      isRecording
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-lg shadow-rose-500/20"
                        : "bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-zinc-700"
                    }`}
                  >
                    {isRecording ? <MicOff className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5 text-purple-400" />}
                    {isRecording ? "Stop Voice Capture" : "Voice Response"}
                  </button>
                </div>

                <textarea
                  rows={6}
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  placeholder="Structure your answer clearly: Situation -> Task -> Action -> Result with quantitative impact..."
                  className="w-full bg-[#0B0F19] border border-zinc-700/80 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 leading-relaxed"
                />

                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-zinc-500 font-mono">
                    {responseText.split(/\s+/).filter(Boolean).length} words
                  </span>

                  <button
                    onClick={handleSubmitResponse}
                    disabled={isSubmittingTurn || !responseText.trim()}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-bold text-xs shadow-lg shadow-purple-500/20 flex items-center gap-2 transition disabled:opacity-50"
                  >
                    {isSubmittingTurn ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Evaluating Turn...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Submit Answer & Evaluate
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================== */}
        {/* STAGE 3: POST-INTERVIEW EXECUTIVE SCORECARD                */}
        {/* ========================================================== */}
        {session && session.status === "COMPLETED" && (
          <div className="space-y-6 animate-in fade-in">
            {/* Top Score Summary Banner */}
            <div className="bg-gradient-to-br from-purple-950/40 via-[#101524] to-cyan-950/40 border border-purple-500/30 rounded-2xl p-8 shadow-2xl space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-zinc-800">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      INTERVIEW COMPLETED
                    </span>
                    <span className="text-xs text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-md border border-emerald-500/20 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      LOGGED TO CAREER DIGITAL TWIN
                    </span>
                  </div>
                  <h2 className="text-2xl font-bold text-white mt-2">{session.title}</h2>
                  <p className="text-xs text-zinc-400 mt-1">{session.summary_feedback}</p>
                </div>

                <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-zinc-900/90 border border-zinc-700/80 shrink-0">
                  <span className="text-[11px] text-zinc-400 font-bold uppercase">Overall Readiness</span>
                  <span className="text-3xl font-extrabold text-cyan-400">
                    {session.overall_score}/100
                  </span>
                </div>
              </div>

              {/* Rubric Category Breakdown Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-[#0B0F19] border border-zinc-800 text-center">
                  <span className="text-xs text-zinc-400 block mb-1">Technical Depth</span>
                  <span className="text-xl font-bold text-indigo-400">{session.technical_score}%</span>
                </div>
                <div className="p-4 rounded-xl bg-[#0B0F19] border border-zinc-800 text-center">
                  <span className="text-xs text-zinc-400 block mb-1">STAR Structure</span>
                  <span className="text-xl font-bold text-purple-400">{session.behavioral_score}%</span>
                </div>
                <div className="p-4 rounded-xl bg-[#0B0F19] border border-zinc-800 text-center">
                  <span className="text-xs text-zinc-400 block mb-1">Communication</span>
                  <span className="text-xl font-bold text-cyan-400">{session.communication_score}%</span>
                </div>
                <div className="p-4 rounded-xl bg-[#0B0F19] border border-zinc-800 text-center">
                  <span className="text-xs text-zinc-400 block mb-1">System Tradeoffs</span>
                  <span className="text-xl font-bold text-emerald-400">{session.tradeoff_score}%</span>
                </div>
              </div>

              {/* Strengths & Improvements */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    Key Candidate Strengths
                  </h4>
                  <ul className="text-xs text-zinc-300 space-y-1.5 list-disc list-inside">
                    {session.strengths.map((s, idx) => (
                      <li key={idx}>{s}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-5 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4" />
                    Targeted Action Items For Next Round
                  </h4>
                  <ul className="text-xs text-zinc-300 space-y-1.5 list-disc list-inside">
                    {session.improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-zinc-800 flex-wrap gap-4">
                <button
                  onClick={() => setSession(null)}
                  className="px-5 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-200 transition flex items-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Practice Another Simulation
                </button>

                <div className="flex items-center gap-3">
                  <Link
                    href="/skills"
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-500/20 flex items-center gap-2 transition"
                  >
                    <span>View Updated Twin Graph</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
