"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  dsaApi,
  DsaProblemSummary,
  DsaProblemDetail,
  DsaRunResponse,
  DsaSubmissionItem,
  DsaStats,
  ProblemDifficulty,
  SubmissionStatus,
} from "@/lib/api/dsa";
import {
  Code2,
  CheckCircle2,
  Circle,
  Clock,
  Zap,
  Sparkles,
  RefreshCw,
  Play,
  Send,
  ArrowLeft,
  Search,
  Filter,
  Layers,
  Award,
  BookOpen,
  Terminal,
  HelpCircle,
  History,
  TrendingUp,
  Cpu,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Flame,
  CheckCheck,
} from "lucide-react";

export default function DsaArenaPage() {
  const { user, token } = useAuth();

  // Navigation & View State
  const [selectedProblemSlug, setSelectedProblemSlug] = useState<string | null>(null);
  const [problems, setProblems] = useState<DsaProblemSummary[]>([]);
  const [activeProblem, setActiveProblem] = useState<DsaProblemDetail | null>(null);
  const [stats, setStats] = useState<DsaStats | null>(null);
  const [submissions, setSubmissions] = useState<DsaSubmissionItem[]>([]);

  // Filters State
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Editor State
  const [selectedLanguage, setSelectedLanguage] = useState<string>("python");
  const [code, setCode] = useState<string>("");
  const [customInput, setCustomInput] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"description" | "hints" | "submissions">("description");
  const [activeTestCaseIdx, setActiveTestCaseIdx] = useState<number>(0);

  // Execution State
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [runResult, setRunResult] = useState<DsaRunResponse | null>(null);
  const [latestSubmission, setLatestSubmission] = useState<DsaSubmissionItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Toast State
  const [toast, setToast] = useState<{ type: "success" | "error" | "info"; text: string } | null>(null);

  const showToast = (type: "success" | "error" | "info", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4500);
  };

  // Load Problem Catalog and Candidate Stats
  const loadCatalogAndStats = useCallback(async () => {
    setLoading(true);
    try {
      const [probsRes, statsRes] = await Promise.all([
        dsaApi.list(
          {
            category: selectedCategory || undefined,
            difficulty: selectedDifficulty || undefined,
            search: searchQuery || undefined,
          },
          token || undefined
        ),
        token ? dsaApi.getStats(token) : Promise.resolve({ data: null, error: null }),
      ]);

      if (probsRes.data) {
        setProblems(probsRes.data);
      }
      if (statsRes.data) {
        setStats(statsRes.data);
      }
    } catch (err) {
      console.error("Error loading DSA data", err);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, selectedDifficulty, searchQuery, token]);

  useEffect(() => {
    loadCatalogAndStats();
  }, [loadCatalogAndStats]);

  // Load Selected Problem Detail
  const loadProblemDetail = useCallback(
    async (slug: string) => {
      try {
        const res = await dsaApi.getProblem(slug, token || undefined);
        if (res.data) {
          setActiveProblem(res.data);
          const initialCode =
            res.data.last_submitted_code ||
            res.data.starter_code[selectedLanguage] ||
            res.data.starter_code["python"] ||
            "";
          setCode(initialCode);
          setRunResult(null);
          setLatestSubmission(null);
          setActiveTestCaseIdx(0);

          if (token) {
            const subsRes = await dsaApi.getSubmissions(res.data.id, token);
            if (subsRes.data) {
              setSubmissions(subsRes.data);
            }
          }
        }
      } catch (err) {
        showToast("error", "Failed to load problem details.");
      }
    },
    [selectedLanguage, token]
  );

  useEffect(() => {
    if (selectedProblemSlug) {
      loadProblemDetail(selectedProblemSlug);
    } else {
      setActiveProblem(null);
    }
  }, [selectedProblemSlug, loadProblemDetail]);

  const handleLanguageChange = (newLang: string) => {
    setSelectedLanguage(newLang);
    if (activeProblem) {
      const template = activeProblem.starter_code[newLang] || activeProblem.starter_code["python"] || "";
      setCode(template);
    }
  };

  const handleRunCode = async () => {
    if (!activeProblem) return;
    setIsRunning(true);
    setRunResult(null);
    try {
      const res = await dsaApi.runCode(
        activeProblem.slug,
        selectedLanguage,
        code,
        customInput || undefined
      );
      if (res.data) {
        setRunResult(res.data);
        if (res.data.status === "ACCEPTED") {
          showToast("success", `Sample tests passed in ${res.data.runtime_ms}ms!`);
        } else {
          showToast("info", `Result: ${res.data.status}`);
        }
      } else {
        showToast("error", res.error || "Execution failed.");
      }
    } catch (err) {
      showToast("error", "Error executing code in sandbox.");
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmitCode = async () => {
    if (!token) {
      showToast("error", "Please sign in to submit solutions and track progress in your Career Twin.");
      return;
    }
    if (!activeProblem) return;

    setIsSubmitting(true);
    setLatestSubmission(null);
    try {
      const res = await dsaApi.submitCode(activeProblem.slug, selectedLanguage, code, token);
      if (res.data) {
        setLatestSubmission(res.data);
        setSubmissions((prev) => [res.data!, ...prev]);

        if (res.data.status === "ACCEPTED") {
          showToast(
            "success",
            `Accepted! +0.05 DSA proficiency verified and logged to Career Twin (${res.data.runtime_ms}ms).`
          );
          // Refresh problem catalog & stats
          loadCatalogAndStats();
        } else {
          showToast("error", `Submission result: ${res.data.status}`);
        }
      } else {
        showToast("error", res.error || "Submission failed.");
      }
    } catch (err) {
      showToast("error", "Error submitting code.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDifficultyBadge = (diff: ProblemDifficulty | string) => {
    switch (diff) {
      case "EASY":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "MEDIUM":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "HARD":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
    }
  };

  const getStatusBadge = (status: SubmissionStatus | string) => {
    switch (status) {
      case "ACCEPTED":
        return {
          label: "Accepted",
          className: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-400 mr-1" />,
        };
      case "WRONG_ANSWER":
        return {
          label: "Wrong Answer",
          className: "bg-rose-500/20 text-rose-300 border-rose-500/30",
          icon: <AlertCircle className="w-4 h-4 text-rose-400 mr-1" />,
        };
      case "TIME_LIMIT_EXCEEDED":
        return {
          label: "Time Limit Exceeded",
          className: "bg-amber-500/20 text-amber-300 border-amber-500/30",
          icon: <Clock className="w-4 h-4 text-amber-400 mr-1" />,
        };
      case "SYNTAX_ERROR":
      case "RUNTIME_ERROR":
        return {
          label: status.replace("_", " "),
          className: "bg-purple-500/20 text-purple-300 border-purple-500/30",
          icon: <Terminal className="w-4 h-4 text-purple-400 mr-1" />,
        };
      default:
        return {
          label: status,
          className: "bg-zinc-800 text-zinc-400 border-zinc-700",
          icon: <Circle className="w-4 h-4 text-zinc-400 mr-1" />,
        };
    }
  };

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

      {/* Top Banner & Breadcrumb */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-4 border-b border-zinc-800/80">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 border border-indigo-500/30 text-indigo-400">
                <Code2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-semibold tracking-wider text-indigo-400 uppercase">
                  Phase 8 — Algorithmic Mastery
                </span>
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                  DSA Preparation Arena & Sandbox
                </h1>
              </div>
            </div>
            <p className="mt-1.5 text-xs md:text-sm text-zinc-400 max-w-2xl">
              Curated placement problem bank with multi-language execution sandbox, AST complexity profiler, and verified Career Twin synchronization.
            </p>
          </div>

          {/* Top Analytics Pills */}
          {stats && (
            <div className="flex items-center gap-3 bg-[#111728] border border-zinc-800 rounded-2xl p-2.5 px-4 shadow-lg">
              <div className="text-center px-2">
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Solved</span>
                <span className="text-base font-extrabold text-white">
                  {stats.total_solved} <span className="text-xs text-zinc-500">/ {stats.total_problems}</span>
                </span>
              </div>
              <div className="h-6 w-px bg-zinc-800" />
              <div className="flex items-center gap-2 px-2 text-xs font-semibold">
                <span className="text-emerald-400">{stats.easy_solved} Easy</span>
                <span className="text-amber-400">{stats.medium_solved} Med</span>
                <span className="text-rose-400">{stats.hard_solved} Hard</span>
              </div>
              <div className="h-6 w-px bg-zinc-800" />
              <div className="text-center px-2">
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Accuracy</span>
                <span className="text-base font-extrabold text-cyan-400">
                  {stats.overall_accuracy_percentage}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto">
        {!selectedProblemSlug ? (
          /* ========================================================== */
          /* VIEW 1: PROBLEM CATALOG & EXPLORER                         */
          /* ========================================================== */
          <div className="space-y-6">
            {/* Filter & Search Bar */}
            <div className="bg-[#101524] border border-zinc-800 rounded-2xl p-4 backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  placeholder="Search problem by title or topic..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#0B0F19] border border-zinc-700/80 rounded-xl pl-10 pr-3.5 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto flex-wrap">
                {/* Topic Selector */}
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="bg-[#0B0F19] border border-zinc-700/80 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Topics (14 Categories)</option>
                  <option value="Arrays & Hashing">Arrays & Hashing</option>
                  <option value="Two Pointers">Two Pointers</option>
                  <option value="Sliding Window">Sliding Window</option>
                  <option value="Stack">Stack</option>
                  <option value="Binary Search">Binary Search</option>
                  <option value="Dynamic Programming">Dynamic Programming</option>
                  <option value="Heap / Priority Queue">Heap / Priority Queue</option>
                  <option value="Graphs">Graphs</option>
                </select>

                {/* Difficulty Selector */}
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="bg-[#0B0F19] border border-zinc-700/80 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Difficulties</option>
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard</option>
                </select>

                <button
                  onClick={loadCatalogAndStats}
                  className="p-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition"
                  title="Refresh Problems"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Problem Cards Table */}
            <div className="bg-[#101524] border border-zinc-800 rounded-2xl overflow-hidden shadow-xl">
              <div className="divide-y divide-zinc-800/80">
                {problems.map((prob) => {
                  const diffClass = getDifficultyBadge(prob.difficulty);

                  return (
                    <div
                      key={prob.id}
                      onClick={() => setSelectedProblemSlug(prob.slug)}
                      className="p-4 md:p-5 flex items-center justify-between gap-4 hover:bg-zinc-800/40 cursor-pointer transition select-none group"
                    >
                      <div className="flex items-center gap-4 min-w-0">
                        <div className="shrink-0">
                          {prob.is_solved ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                          ) : (
                            <Circle className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition" />
                          )}
                        </div>

                        <div className="min-w-0">
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <span className="text-sm md:text-base font-bold text-white group-hover:text-indigo-400 transition truncate">
                              {prob.order_index}. {prob.title}
                            </span>
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${diffClass}`}
                            >
                              {prob.difficulty}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-xs text-zinc-400 flex-wrap">
                            <span className="text-zinc-400">{prob.category}</span>
                            <span>•</span>
                            <span className="font-mono text-cyan-400/90">
                              Target: {prob.expected_time_complexity}
                            </span>
                            <span>•</span>
                            <span className="text-zinc-500">{prob.acceptance_rate}% Acceptance</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <button className="px-3.5 py-1.5 rounded-xl bg-indigo-600/20 group-hover:bg-indigo-600 border border-indigo-500/30 group-hover:border-indigo-500 text-indigo-300 group-hover:text-white text-xs font-semibold flex items-center gap-1.5 transition duration-200">
                          <span>{prob.is_solved ? "Solve Again" : "Solve Challenge"}</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}

                {problems.length === 0 && !loading && (
                  <div className="p-12 text-center text-zinc-500 text-sm">
                    No problems match your current filter criteria.
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* ========================================================== */
          /* VIEW 2: SPLIT-PANE PLACEMENT IDE & CODE SANDBOX           */
          /* ========================================================== */
          activeProblem && (
            <div className="space-y-4">
              {/* Back Button & Problem Header Bar */}
              <div className="flex items-center justify-between gap-4 pb-2">
                <button
                  onClick={() => setSelectedProblemSlug(null)}
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-xs font-semibold text-zinc-300 transition"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Problem Catalog
                </button>

                <div className="flex items-center gap-2.5">
                  <span
                    className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getDifficultyBadge(
                      activeProblem.difficulty
                    )}`}
                  >
                    {activeProblem.difficulty}
                  </span>
                  <span className="text-xs font-mono text-zinc-400 bg-zinc-900 px-2.5 py-0.5 rounded-md border border-zinc-800">
                    {activeProblem.category}
                  </span>
                </div>
              </div>

              {/* Split-Pane Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* LEFT PANE: Problem Statement, Hints & Submissions (5 Cols) */}
                <div className="lg:col-span-5 bg-[#101524] border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[750px]">
                  {/* Tab Navigation */}
                  <div className="flex items-center border-b border-zinc-800 bg-[#0B0F19] px-4 pt-2 gap-2">
                    <button
                      onClick={() => setActiveTab("description")}
                      className={`pb-2.5 text-xs font-semibold border-b-2 transition ${
                        activeTab === "description"
                          ? "text-indigo-400 border-indigo-400"
                          : "text-zinc-400 border-transparent hover:text-white"
                      }`}
                    >
                      Description
                    </button>
                    <button
                      onClick={() => setActiveTab("hints")}
                      className={`pb-2.5 text-xs font-semibold border-b-2 transition ${
                        activeTab === "hints"
                          ? "text-indigo-400 border-indigo-400"
                          : "text-zinc-400 border-transparent hover:text-white"
                      }`}
                    >
                      Hints ({activeProblem.hints.length})
                    </button>
                    <button
                      onClick={() => setActiveTab("submissions")}
                      className={`pb-2.5 text-xs font-semibold border-b-2 transition ${
                        activeTab === "submissions"
                          ? "text-indigo-400 border-indigo-400"
                          : "text-zinc-400 border-transparent hover:text-white"
                      }`}
                    >
                      History ({submissions.length})
                    </button>
                  </div>

                  {/* Tab Contents (Scrollable) */}
                  <div className="p-6 overflow-y-auto flex-1 space-y-6 text-sm text-zinc-300 leading-relaxed">
                    {activeTab === "description" && (
                      <div className="space-y-6">
                        <div>
                          <h2 className="text-xl font-bold text-white mb-2">{activeProblem.title}</h2>
                          <div className="flex items-center gap-3 text-xs text-zinc-400">
                            <span>Time Goal: <strong className="text-cyan-300 font-mono">{activeProblem.expected_time_complexity}</strong></span>
                            <span>•</span>
                            <span>Space Goal: <strong className="text-cyan-300 font-mono">{activeProblem.expected_space_complexity}</strong></span>
                          </div>
                        </div>

                        {/* Description Markdown rendered */}
                        <div className="whitespace-pre-line text-zinc-300 text-xs md:text-sm font-sans space-y-3">
                          {activeProblem.description}
                        </div>

                        {/* Constraints */}
                        {activeProblem.constraints.length > 0 && (
                          <div className="space-y-2 pt-2 border-t border-zinc-800">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                              Constraints
                            </h4>
                            <ul className="list-disc list-inside text-xs font-mono text-zinc-400 space-y-1">
                              {activeProblem.constraints.map((c, i) => (
                                <li key={i}>{c}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {activeTab === "hints" && (
                      <div className="space-y-4">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <HelpCircle className="w-4 h-4 text-amber-400" />
                          Placement Interview Hints
                        </h3>
                        {activeProblem.hints.map((hint, i) => (
                          <div
                            key={i}
                            className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-200/90 leading-relaxed space-y-1"
                          >
                            <span className="font-bold text-amber-400 block">Hint {i + 1}</span>
                            <p>{hint}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeTab === "submissions" && (
                      <div className="space-y-3">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <History className="w-4 h-4 text-cyan-400" />
                          Attempt History
                        </h3>
                        {submissions.map((sub) => {
                          const badge = getStatusBadge(sub.status);
                          return (
                            <div
                              key={sub.id}
                              className="p-3.5 rounded-xl bg-[#0B0F19] border border-zinc-800 space-y-2 text-xs"
                            >
                              <div className="flex items-center justify-between">
                                <span
                                  className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[11px] font-bold ${badge.className}`}
                                >
                                  {badge.icon}
                                  {badge.label}
                                </span>
                                <span className="text-zinc-500">
                                  {new Date(sub.created_at).toLocaleDateString()}
                                </span>
                              </div>
                              <div className="flex items-center justify-between text-zinc-400 text-[11px]">
                                <span>Language: {sub.language.toUpperCase()}</span>
                                <span>
                                  Runtime: <strong className="text-zinc-200">{sub.runtime_ms}ms</strong> •{" "}
                                  {sub.passed_test_cases}/{sub.total_test_cases} passed
                                </span>
                              </div>
                              {sub.ai_feedback && (
                                <p className="text-[11px] text-cyan-300/80 italic pt-1 border-t border-zinc-800/80">
                                  {sub.ai_feedback}
                                </p>
                              )}
                            </div>
                          );
                        })}
                        {submissions.length === 0 && (
                          <div className="text-center py-8 text-zinc-500 text-xs">
                            No submissions recorded for this problem yet.
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* RIGHT PANE: Code Editor & Execution Console (7 Cols) */}
                <div className="lg:col-span-7 bg-[#101524] border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[750px]">
                  {/* Editor Header Bar */}
                  <div className="flex items-center justify-between p-3 bg-[#0B0F19] border-b border-zinc-800">
                    <div className="flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-indigo-400" />
                      <select
                        value={selectedLanguage}
                        onChange={(e) => handleLanguageChange(e.target.value)}
                        className="bg-[#121829] border border-zinc-700/80 rounded-lg px-2.5 py-1 text-xs text-zinc-200 font-semibold focus:outline-none focus:border-indigo-500"
                      >
                        <option value="python">Python 3 (AST Profiler)</option>
                        <option value="javascript">JavaScript (Node.js)</option>
                        <option value="cpp">C++ (GCC 13)</option>
                        <option value="java">Java (OpenJDK 21)</option>
                      </select>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleRunCode}
                        disabled={isRunning || isSubmitting}
                        className="px-3.5 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold text-xs flex items-center gap-1.5 transition disabled:opacity-50"
                      >
                        {isRunning ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Play className="w-3.5 h-3.5 text-emerald-400" />
                        )}
                        Run Tests
                      </button>

                      <button
                        onClick={handleSubmitCode}
                        disabled={isRunning || isSubmitting}
                        className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white font-bold text-xs shadow-md shadow-indigo-500/20 flex items-center gap-1.5 transition disabled:opacity-50"
                      >
                        {isSubmitting ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Send className="w-3.5 h-3.5" />
                        )}
                        Submit
                      </button>
                    </div>
                  </div>

                  {/* Code Textarea / IDE Surface */}
                  <div className="flex-1 bg-[#090D16] p-4 relative font-mono text-xs text-zinc-200 overflow-hidden flex flex-col">
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      spellCheck={false}
                      className="w-full flex-1 bg-transparent resize-none focus:outline-none font-mono text-xs leading-relaxed text-cyan-300/90 selection:bg-indigo-500/40"
                    />
                  </div>

                  {/* Bottom Console / Test Results Panel */}
                  <div className="border-t border-zinc-800 bg-[#0E1322] p-4 h-64 overflow-y-auto space-y-3">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                      <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                        Sandbox Output & Test Cases
                      </span>

                      {runResult && (
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${
                            runResult.status === "ACCEPTED"
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : "bg-rose-500/20 text-rose-300 border-rose-500/30"
                          }`}
                        >
                          {runResult.status} ({runResult.passed_count}/{runResult.total_count} Passed •{" "}
                          {runResult.runtime_ms}ms)
                        </span>
                      )}

                      {latestSubmission && (
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${
                            latestSubmission.status === "ACCEPTED"
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30 animate-pulse"
                              : "bg-rose-500/20 text-rose-300 border-rose-500/30"
                          }`}
                        >
                          SUBMISSION: {latestSubmission.status} ({latestSubmission.passed_test_cases}/
                          {latestSubmission.total_test_cases})
                        </span>
                      )}
                    </div>

                    {/* Test Case Selectors */}
                    <div className="flex items-center gap-2 flex-wrap">
                      {activeProblem.test_cases.map((tc, idx) => (
                        <button
                          key={tc.id}
                          onClick={() => setActiveTestCaseIdx(idx)}
                          className={`px-2.5 py-1 rounded-lg text-xs font-mono transition ${
                            activeTestCaseIdx === idx
                              ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40"
                              : "bg-zinc-800/80 text-zinc-400 hover:text-white"
                          }`}
                        >
                          Case {idx + 1}
                        </button>
                      ))}
                    </div>

                    {/* Selected Test Case Details */}
                    {activeProblem.test_cases[activeTestCaseIdx] && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                        <div className="p-2.5 rounded-xl bg-[#0B0F19] border border-zinc-800 space-y-1">
                          <span className="text-[10px] text-zinc-500 uppercase font-bold block">Input</span>
                          <p className="text-zinc-300 truncate">
                            {activeProblem.test_cases[activeTestCaseIdx].input_data}
                          </p>
                        </div>

                        <div className="p-2.5 rounded-xl bg-[#0B0F19] border border-zinc-800 space-y-1">
                          <span className="text-[10px] text-zinc-500 uppercase font-bold block">
                            Expected Output
                          </span>
                          <p className="text-emerald-400 font-bold truncate">
                            {activeProblem.test_cases[activeTestCaseIdx].expected_output}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* AI Placement Coach Feedback Banner */}
                    {latestSubmission?.ai_feedback && (
                      <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-xs text-cyan-300/90 flex items-start gap-2">
                        <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-cyan-400 block">Placement Coach Analysis</span>
                          <p className="whitespace-pre-line text-zinc-300">{latestSubmission.ai_feedback}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
