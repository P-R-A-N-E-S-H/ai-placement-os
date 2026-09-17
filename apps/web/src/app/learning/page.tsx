"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  roadmapsApi,
  LearningRoadmap,
  RoadmapModuleItem,
  RoadmapTaskItem,
  TaskType,
  ModuleStatus,
} from "@/lib/api/roadmaps";
import { skillsApi, RoleBenchmark } from "@/lib/api/skills";
import { jobsApi, JobSummary } from "@/lib/api/jobs";
import {
  BookOpen,
  CheckCircle2,
  Circle,
  Clock,
  ExternalLink,
  Github,
  Layers,
  Lock,
  PlayCircle,
  RefreshCw,
  Sparkles,
  Target,
  Unlock,
  Video,
  FileCode,
  Flame,
  ArrowRight,
  TrendingUp,
  Award,
  ChevronDown,
  ChevronUp,
  Code2,
  Send,
  Zap,
  Briefcase,
  Sliders,
  AlertCircle,
  Check,
  CheckCheck,
} from "lucide-react";

export default function LearningRoadmapPage() {
  const { user, token } = useAuth();

  // Configuration State
  const [selectedRole, setSelectedRole] = useState<string>("AI Engineer");
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [targetType, setTargetType] = useState<"ROLE" | "JOB">("ROLE");
  const [weeklyHours, setWeeklyHours] = useState<number>(15.0);
  const [learningStyle, setLearningStyle] = useState<"PRACTICAL" | "THEORETICAL" | "SPEEDRUN">("PRACTICAL");

  // Data State
  const [roadmap, setRoadmap] = useState<LearningRoadmap | null>(null);
  const [roleBenchmarks, setRoleBenchmarks] = useState<RoleBenchmark[]>([]);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [togglingTaskId, setTogglingTaskId] = useState<string | null>(null);
  const [expandedModules, setExpandedModules] = useState<Record<string, boolean>>({});

  // Proof-of-work modal state
  const [activeProofTask, setActiveProofTask] = useState<RoadmapTaskItem | null>(null);
  const [proofText, setProofText] = useState<string>("");
  const [proofUrl, setProofUrl] = useState<string>("");

  // Toast State
  const [toast, setToast] = useState<{ type: "success" | "info" | "error"; text: string } | null>(null);

  const showToast = (type: "success" | "info" | "error", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4500);
  };

  const loadInitialData = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Fetch benchmarks
      const benchRes = await skillsApi.getRoleBenchmarks();
      if (benchRes.data) {
        setRoleBenchmarks(benchRes.data);
      }

      // 2. Fetch jobs
      const jobsRes = await jobsApi.list({ page: 1, page_size: 10 });
      if (jobsRes.data) {
        setJobs(jobsRes.data.items);
      }

      // 3. Fetch active roadmap if token present
      if (token) {
        const activeRes = await roadmapsApi.getActive(token);
        if (activeRes.data) {
          setRoadmap(activeRes.data);
          // Auto-expand active / unlocked modules
          const initialExpanded: Record<string, boolean> = {};
          activeRes.data.modules.forEach((mod) => {
            initialExpanded[mod.id] = mod.status !== "LOCKED";
          });
          setExpandedModules(initialExpanded);
        }
      }
    } catch (err) {
      console.error("Error loading roadmap data", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleGenerateRoadmap = async () => {
    if (!token) {
      showToast("error", "Please sign in to generate and track your personalized roadmap.");
      return;
    }

    setGenerating(true);
    try {
      const payload = {
        target_role: targetType === "ROLE" ? selectedRole : undefined,
        target_job_id: targetType === "JOB" ? selectedJobId : undefined,
        weekly_hours: weeklyHours,
        learning_style: learningStyle,
      };

      const res = await roadmapsApi.generate(payload, token);
      if (res.data) {
        setRoadmap(res.data);
        const exp: Record<string, boolean> = {};
        res.data.modules.forEach((mod) => {
          exp[mod.id] = mod.status !== "LOCKED";
        });
        setExpandedModules(exp);
        showToast(
          "success",
          `Generated ${res.data.total_weeks}-week curriculum for ${res.data.target_role} (${res.data.total_tasks} tasks)!`
        );
      } else {
        showToast("error", res.error || "Failed to generate roadmap.");
      }
    } catch (err) {
      showToast("error", "Network or server error while generating roadmap.");
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleTask = async (task: RoadmapTaskItem, forcedCompleted?: boolean) => {
    if (!token || !roadmap) return;

    const willBeCompleted = forcedCompleted !== undefined ? forcedCompleted : !task.is_completed;

    // If candidate is completing task and hasn't opened proof modal, prompt with modal for rich evidence
    if (willBeCompleted && !activeProofTask) {
      setActiveProofTask(task);
      setProofText("");
      setProofUrl("");
      return;
    }

    setTogglingTaskId(task.id);
    try {
      const res = await roadmapsApi.toggleTask(
        task.id,
        {
          is_completed: willBeCompleted,
          evidence_text: proofText || undefined,
          evidence_source_id: proofUrl || undefined,
        },
        token
      );

      if (res.data) {
        setRoadmap(res.data);
        if (willBeCompleted) {
          showToast(
            "success",
            `Task completed! +0.15 proficiency logged to Career Twin for ${task.skill_slug.toUpperCase()}.`
          );
        } else {
          showToast("info", "Task marked as incomplete.");
        }
        setActiveProofTask(null);
        setProofText("");
        setProofUrl("");
      } else {
        showToast("error", res.error || "Failed to toggle task.");
      }
    } catch (err) {
      showToast("error", "Failed to update task completion.");
    } finally {
      setTogglingTaskId(null);
    }
  };

  const toggleModuleAccordion = (moduleId: string) => {
    setExpandedModules((prev) => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  const getTaskTypeBadge = (type: TaskType) => {
    switch (type) {
      case "CONCEPT":
        return {
          label: "CONCEPT",
          bg: "bg-blue-500/10 text-blue-400 border-blue-500/20",
          icon: <BookOpen className="w-3.5 h-3.5 mr-1" />,
        };
      case "PRACTICE":
        return {
          label: "PRACTICE LAB",
          bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
          icon: <Code2 className="w-3.5 h-3.5 mr-1" />,
        };
      case "PROJECT":
        return {
          label: "DELIVERABLE",
          bg: "bg-purple-500/10 text-purple-400 border-purple-500/20",
          icon: <Flame className="w-3.5 h-3.5 mr-1" />,
        };
      case "QUIZ":
        return {
          label: "EVALUATION",
          bg: "bg-amber-500/10 text-amber-400 border-amber-500/20",
          icon: <Award className="w-3.5 h-3.5 mr-1" />,
        };
      default:
        return {
          label: type,
          bg: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
          icon: <Layers className="w-3.5 h-3.5 mr-1" />,
        };
    }
  };

  const getModuleStatusBadge = (status: ModuleStatus) => {
    switch (status) {
      case "COMPLETED":
        return {
          label: "Completed",
          className: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-400 mr-1.5" />,
        };
      case "IN_PROGRESS":
      case "UNLOCKED":
        return {
          label: "In Progress",
          className: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30 animate-pulse",
          icon: <Unlock className="w-4 h-4 text-cyan-400 mr-1.5" />,
        };
      case "LOCKED":
      default:
        return {
          label: "Locked",
          className: "bg-zinc-800 text-zinc-400 border-zinc-700",
          icon: <Lock className="w-4 h-4 text-zinc-500 mr-1.5" />,
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

      {/* Proof of Work Modal */}
      {activeProofTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-[#121829] border border-cyan-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  PROOF OF WORK
                </span>
                <h3 className="text-lg font-bold text-white mt-1.5">{activeProofTask.title}</h3>
                <p className="text-xs text-zinc-400 mt-1">{activeProofTask.description}</p>
              </div>
              <button
                onClick={() => setActiveProofTask(null)}
                className="text-zinc-500 hover:text-white transition p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1.5 flex items-center gap-1.5">
                  <Github className="w-3.5 h-3.5 text-zinc-400" />
                  GitHub Repository / Artifact URL (Optional)
                </label>
                <input
                  type="url"
                  value={proofUrl}
                  onChange={(e) => setProofUrl(e.target.value)}
                  placeholder="https://github.com/username/project-repo"
                  className="w-full bg-[#0B0F19] border border-zinc-700/80 rounded-xl px-3.5 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1.5">
                  Implementation Summary & Insights
                </label>
                <textarea
                  rows={3}
                  value={proofText}
                  onChange={(e) => setProofText(e.target.value)}
                  placeholder="Summarize what you built, algorithmic complexity, or key architecture decisions..."
                  className="w-full bg-[#0B0F19] border border-zinc-700/80 rounded-xl px-3.5 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                />
              </div>

              <div className="p-3 bg-cyan-950/30 border border-cyan-800/40 rounded-xl text-xs text-cyan-300/90 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>Submitting logs verified evidence to Career Twin (+0.15 proficiency in {activeProofTask.skill_slug}).</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setActiveProofTask(null)}
                className="px-4 py-2 rounded-xl text-sm font-medium text-zinc-400 hover:text-zinc-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => handleToggleTask(activeProofTask, true)}
                disabled={togglingTaskId === activeProofTask.id}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition"
              >
                {togglingTaskId === activeProofTask.id ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-4 h-4" />
                )}
                Verify & Complete Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top Hero Banner */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-zinc-800/80">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-semibold tracking-wider text-cyan-400 uppercase">
                  Phase 7 — Adaptive Learning Engine
                </span>
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                  Personalized Career Roadmap
                </h1>
              </div>
            </div>
            <p className="mt-2 text-sm text-zinc-400 max-w-2xl">
              Synthesized week-by-week learning milestones, daily proof-of-work tracking, and curated production resources calibrated to your target career requirements.
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href="/skills"
              className="px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-sm font-medium text-zinc-200 flex items-center gap-2 transition"
            >
              <Layers className="w-4 h-4 text-cyan-400" />
              Skill Gaps & DAG
            </Link>
            <Link
              href="/matches"
              className="px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-zinc-500 text-sm font-medium text-zinc-200 flex items-center gap-2 transition"
            >
              <Briefcase className="w-4 h-4 text-emerald-400" />
              Live Job Matches
            </Link>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Synthesizer & Control Panel */}
        <div className="bg-[#101524]/90 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sliders className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-semibold text-zinc-200">Roadmap Synthesizer Controls</h2>
            </div>
            <span className="text-xs text-zinc-500 font-mono">DETERMINISTIC TOPOLOGICAL SORT</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
            {/* Target Mode */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-400">Target Type</label>
              <div className="grid grid-cols-2 gap-2 bg-[#0B0F19] p-1 rounded-xl border border-zinc-800">
                <button
                  onClick={() => setTargetType("ROLE")}
                  className={`py-1.5 text-xs font-medium rounded-lg transition ${
                    targetType === "ROLE"
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  Role Benchmark
                </button>
                <button
                  onClick={() => setTargetType("JOB")}
                  className={`py-1.5 text-xs font-medium rounded-lg transition ${
                    targetType === "JOB"
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  Live Placement Job
                </button>
              </div>
            </div>

            {/* Target Select */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-400">
                {targetType === "ROLE" ? "Select Career Benchmark" : "Select Placement Posting"}
              </label>
              {targetType === "ROLE" ? (
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full bg-[#0B0F19] border border-zinc-700 rounded-xl px-3.5 py-2 text-sm text-zinc-200 focus:outline-none focus:border-cyan-500"
                >
                  {roleBenchmarks.length > 0 ? (
                    roleBenchmarks.map((b) => (
                      <option key={b.role_slug} value={b.role_name}>
                        {b.role_name} ({b.typical_ctc_range})
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="AI Engineer">AI Engineer (₹18–32 LPA)</option>
                      <option value="Backend Engineer">Backend Engineer (₹15–28 LPA)</option>
                      <option value="Full-Stack Engineer">Full-Stack Engineer (₹14–25 LPA)</option>
                      <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer (₹16–30 LPA)</option>
                      <option value="Data Scientist">Data Scientist (₹16–28 LPA)</option>
                    </>
                  )}
                </select>
              ) : (
                <select
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(e.target.value)}
                  className="w-full bg-[#0B0F19] border border-zinc-700 rounded-xl px-3.5 py-2 text-sm text-zinc-200 focus:outline-none focus:border-cyan-500"
                >
                  {jobs.length > 0 ? (
                    jobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.title} @ {j.company}
                      </option>
                    ))
                  ) : (
                    <option value="">No jobs ingested yet</option>
                  )}
                </select>
              )}
            </div>

            {/* Weekly Hours & Velocity */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs text-zinc-400">
                <span>Study Commitment</span>
                <span className="text-cyan-400 font-semibold">{weeklyHours} hrs/week</span>
              </div>
              <input
                type="range"
                min="5"
                max="40"
                step="5"
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 bg-zinc-800 rounded-lg cursor-pointer"
              />
            </div>

            {/* Generate Action Button */}
            <div>
              <button
                onClick={handleGenerateRoadmap}
                disabled={generating}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition duration-200 disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Synthesizing DAG...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Synthesize Roadmap
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Loading Skeleton */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
            <p className="text-sm text-zinc-400">Loading personalized learning curriculum...</p>
          </div>
        )}

        {/* Roadmap Display */}
        {!loading && roadmap && (
          <div className="space-y-8">
            {/* Top Scorecard Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#121829] border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                    Target Objective
                  </span>
                  <Target className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="mt-2 text-xl font-bold text-white truncate">
                  {roadmap.target_role}
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  {roadmap.target_job_company
                    ? `Tailored for ${roadmap.target_job_company}`
                    : "Calibrated to Top Tech Benchmarks"}
                </p>
              </div>

              <div className="bg-[#121829] border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                    Timeline Commitment
                  </span>
                  <Clock className="w-4 h-4 text-blue-400" />
                </div>
                <div className="mt-2 text-xl font-bold text-white">
                  {roadmap.total_weeks} Weeks
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  {roadmap.weekly_hours} hrs/week • ~{roadmap.total_estimated_hours} total hrs
                </p>
              </div>

              <div className="bg-[#121829] border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                    Task Execution
                  </span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="mt-2 text-xl font-bold text-white">
                  {roadmap.completed_tasks} / {roadmap.total_tasks}
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  {roadmap.total_tasks - roadmap.completed_tasks} tasks remaining
                </p>
              </div>

              <div className="bg-[#121829] border border-zinc-800/80 rounded-2xl p-5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                    Completion Mastery
                  </span>
                  <TrendingUp className="w-4 h-4 text-purple-400" />
                </div>
                <div className="mt-2 text-xl font-bold text-white">
                  {roadmap.progress_percentage.toFixed(1)}%
                </div>
                {/* Visual Progress Bar */}
                <div className="w-full bg-zinc-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-cyan-400 to-emerald-400 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.max(4, roadmap.progress_percentage))}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Weekly Modules List */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Layers className="w-5 h-5 text-cyan-400" />
                  Weekly Curriculum Milestones
                </h2>
                <div className="text-xs text-zinc-400">
                  {roadmap.modules.length} Multi-Day Modules
                </div>
              </div>

              {roadmap.modules.map((module) => {
                const isExpanded = !!expandedModules[module.id];
                const statusBadge = getModuleStatusBadge(module.status as ModuleStatus);
                const completedCount = module.tasks.filter((t) => t.is_completed).length;

                return (
                  <div
                    key={module.id}
                    className={`border rounded-2xl transition-all duration-300 overflow-hidden ${
                      module.status === "LOCKED"
                        ? "bg-[#0D121F]/60 border-zinc-800/60 opacity-80"
                        : module.status === "COMPLETED"
                        ? "bg-[#10192A]/90 border-emerald-500/30 shadow-lg shadow-emerald-500/5"
                        : "bg-[#111728]/95 border-cyan-500/40 shadow-xl shadow-cyan-500/5"
                    }`}
                  >
                    {/* Module Header Bar */}
                    <div
                      onClick={() => toggleModuleAccordion(module.id)}
                      className="p-5 cursor-pointer flex flex-col md:flex-row items-start md:items-center justify-between gap-4 select-none hover:bg-zinc-800/30 transition"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex flex-col items-center justify-center w-12 h-12 rounded-xl bg-zinc-900 border border-zinc-700/80 shrink-0">
                          <span className="text-[10px] uppercase font-bold text-zinc-400">Week</span>
                          <span className="text-base font-extrabold text-white leading-none">
                            {module.week_number}
                          </span>
                        </div>

                        <div>
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <h3 className="text-base font-bold text-white">{module.title}</h3>
                            <span
                              className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full border ${statusBadge.className}`}
                            >
                              {statusBadge.icon}
                              {statusBadge.label}
                            </span>
                          </div>
                          <p className="text-xs text-zinc-400 mt-1">{module.description}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                        {/* Focus Skills Badges */}
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {module.focus_skills.map((skill) => (
                            <span
                              key={skill}
                              className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-zinc-800/90 text-cyan-300 border border-zinc-700/80"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>

                        {/* Task Count & Accordion Trigger */}
                        <div className="flex items-center gap-3 shrink-0">
                          <span className="text-xs text-zinc-400 font-medium">
                            {completedCount}/{module.tasks.length} Done
                          </span>
                          <div className="p-1.5 rounded-lg bg-zinc-800 text-zinc-300">
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Module Tasks List (Expanded) */}
                    {isExpanded && (
                      <div className="px-5 pb-5 pt-2 border-t border-zinc-800/80 space-y-3 bg-[#0B0F19]/50">
                        {module.tasks.map((task) => {
                          const typeBadge = getTaskTypeBadge(task.task_type);
                          const isToggling = togglingTaskId === task.id;

                          return (
                            <div
                              key={task.id}
                              className={`p-4 rounded-xl border transition-all duration-200 ${
                                task.is_completed
                                  ? "bg-emerald-950/20 border-emerald-500/30 text-zinc-300"
                                  : "bg-[#13192B]/90 border-zinc-800 hover:border-zinc-700 text-white"
                              }`}
                            >
                              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                                <div className="flex items-start gap-3 flex-1">
                                  {/* Completion Toggle Button */}
                                  <button
                                    onClick={() => handleToggleTask(task)}
                                    disabled={isToggling}
                                    className={`mt-0.5 p-1 rounded-lg border transition ${
                                      task.is_completed
                                        ? "bg-emerald-500 text-black border-emerald-400"
                                        : "border-zinc-600 hover:border-cyan-400 text-transparent"
                                    }`}
                                  >
                                    {isToggling ? (
                                      <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                                    ) : task.is_completed ? (
                                      <Check className="w-4 h-4 stroke-[3]" />
                                    ) : (
                                      <Circle className="w-4 h-4" />
                                    )}
                                  </button>

                                  <div className="space-y-1 flex-1">
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <span
                                        className={`inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full border ${typeBadge.bg}`}
                                      >
                                        {typeBadge.icon}
                                        {typeBadge.label}
                                      </span>
                                      <span className="text-xs font-semibold text-zinc-400">
                                        Day {task.day_number}
                                      </span>
                                      <span className="text-xs font-mono text-zinc-500">
                                        • {task.estimated_minutes} mins
                                      </span>
                                      {task.is_completed && (
                                        <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                                          ✓ VERIFIED IN CAREER TWIN
                                        </span>
                                      )}
                                    </div>

                                    <h4
                                      className={`text-sm font-semibold ${
                                        task.is_completed
                                          ? "line-through text-zinc-400"
                                          : "text-white"
                                      }`}
                                    >
                                      {task.title}
                                    </h4>
                                    <p className="text-xs text-zinc-400 leading-relaxed">
                                      {task.description}
                                    </p>

                                    {/* Evidence proof link if attached */}
                                    {task.evidence_source_id && (
                                      <div className="flex items-center gap-1.5 pt-1 text-xs text-cyan-400">
                                        <Github className="w-3.5 h-3.5" />
                                        <a
                                          href={task.evidence_source_id}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="hover:underline truncate max-w-sm"
                                        >
                                          {task.evidence_source_id}
                                        </a>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                {/* Curated Resource Links */}
                                {task.resources && task.resources.length > 0 && (
                                  <div className="flex items-center gap-2 flex-wrap pl-7 md:pl-0 shrink-0">
                                    {task.resources.map((res, idx) => (
                                      <a
                                        key={idx}
                                        href={res.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-700/80 hover:border-cyan-500/60 hover:text-cyan-300 text-xs text-zinc-300 transition"
                                      >
                                        {res.type === "DOCS" && <BookOpen className="w-3 h-3 text-blue-400" />}
                                        {res.type === "VIDEO" && <Video className="w-3 h-3 text-rose-400" />}
                                        {res.type === "GITHUB" && <Github className="w-3 h-3 text-purple-400" />}
                                        {res.type === "LAB" && <FileCode className="w-3 h-3 text-emerald-400" />}
                                        <span className="truncate max-w-[140px]">{res.title}</span>
                                        <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                                      </a>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Next Phase Hook Banner */}
            <div className="bg-gradient-to-r from-cyan-950/40 via-blue-950/40 to-purple-950/40 border border-cyan-500/30 rounded-2xl p-6 relative overflow-hidden shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="space-y-1.5">
                <span className="text-xs font-bold tracking-wider text-cyan-400 uppercase">
                  Connected Preparation
                </span>
                <h3 className="text-lg font-bold text-white">
                  Practice DSA Labs & Interview Sandbox
                </h3>
                <p className="text-xs text-zinc-400 max-w-xl">
                  Ready to test your algorithms? Complete live code challenges and get instant feedback in our multi-language sandbox environment.
                </p>
              </div>

              <Link
                href="/skills"
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 flex items-center gap-2 shrink-0 transition"
              >
                <span>View Skill Graph</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}

        {/* Empty State / Not Generated */}
        {!loading && !roadmap && (
          <div className="bg-[#101524] border border-zinc-800 rounded-2xl p-12 text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto">
              <Sparkles className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">No Active Roadmap Generated</h3>
            <p className="text-sm text-zinc-400 max-w-md mx-auto">
              Select your target role benchmark or placement job above and click &quot;Synthesize Roadmap&quot; to build your tailored week-by-week curriculum.
            </p>
            <button
              onClick={handleGenerateRoadmap}
              disabled={generating}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 inline-flex items-center gap-2 transition"
            >
              <Sparkles className="w-4 h-4" />
              Generate First Roadmap
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
