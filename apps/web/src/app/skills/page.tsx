"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  skillsApi,
  SkillGapReport,
  SkillGapItem,
  RoleBenchmark,
} from "@/lib/api/skills";
import { jobsApi, JobSummary } from "@/lib/api/jobs";
import {
  GitCompare,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Lock,
  Unlock,
  Zap,
  Layers,
  ArrowRight,
  TrendingUp,
  SlidersHorizontal,
  GraduationCap,
  Briefcase,
  ChevronRight,
  Target,
} from "lucide-react";

export default function SkillGapPage() {
  const { user, token } = useAuth();

  // Mode & Selection State
  const [evalMode, setEvalMode] = useState<"ROLE" | "JOB">("ROLE");
  const [selectedRole, setSelectedRole] = useState<string>("ai-engineer");
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [weeklyHours, setWeeklyHours] = useState<number>(15.0);

  // Data State
  const [report, setReport] = useState<SkillGapReport | null>(null);
  const [roleBenchmarks, setRoleBenchmarks] = useState<RoleBenchmark[]>([]);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"matrix" | "pathway" | "dag">("matrix");
  const [toastMessage, setToastMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Initial load
  useEffect(() => {
    loadInitialData();
  }, [token]);

  const loadInitialData = async () => {
    setLoading(true);
    // 1. Load benchmarks
    const benchRes = await skillsApi.getRoleBenchmarks();
    if (benchRes.data) {
      setRoleBenchmarks(benchRes.data);
    }

    // 2. Load recent jobs
    const jobsRes = await jobsApi.list({ page: 1, page_size: 15 });
    if (jobsRes.data) {
      setJobs(jobsRes.data.items);
      if (jobsRes.data.items.length > 0) {
        setSelectedJobId(jobsRes.data.items[0].id);
      }
    }

    // 3. Load or calculate latest gap report if authenticated
    if (token) {
      const latestRes = await skillsApi.getLatestGapReport(token);
      if (latestRes.data) {
        setReport(latestRes.data);
        if (latestRes.data.target_type === "ROLE") {
          setSelectedRole(latestRes.data.target_id);
          setEvalMode("ROLE");
        } else if (latestRes.data.target_type === "JOB") {
          setSelectedJobId(latestRes.data.target_id);
          setEvalMode("JOB");
        }
      }
    }
    setLoading(false);
  };

  const handleEvaluate = async (overrideRole?: string, overrideJob?: string, overrideHours?: number) => {
    if (!token) {
      setToastMessage({ type: "error", text: "Please sign in to analyze your Career Twin skill gaps." });
      return;
    }

    setEvaluating(true);
    setToastMessage(null);

    const targetRoleSlug = overrideRole || selectedRole;
    const targetJob = overrideJob || selectedJobId;
    const hours = overrideHours !== undefined ? overrideHours : weeklyHours;

    let res;
    if (evalMode === "ROLE") {
      res = await skillsApi.analyzeRoleGap(targetRoleSlug, hours, token);
    } else {
      if (!targetJob) {
        setToastMessage({ type: "error", text: "Please select a target job." });
        setEvaluating(false);
        return;
      }
      res = await skillsApi.analyzeJobGap(targetJob, hours, token);
    }

    if (res.data) {
      setReport(res.data);
      setToastMessage({
        type: "success",
        text: `Analysis complete for ${res.data.target_title}! Readiness score: ${res.data.readiness_score}%`,
      });
    } else {
      setToastMessage({ type: "error", text: res.error || "Failed to analyze skill gaps." });
    }
    setEvaluating(false);
  };

  return (
    <div className="min-h-screen bg-[#060a12] text-slate-100 p-6 lg:p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Phase 6 Engine
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase tracking-wider">
              Topological DAG & ROI Matrix
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <GitCompare className="h-7 w-7 text-indigo-400" />
            Skill Gap Analysis & Prerequisite DAG Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Deterministically compare your Career Digital Twin verified skills against target industry benchmarks or active job opportunities.
          </p>
        </div>

        {/* Global Evaluation Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleEvaluate()}
            disabled={evaluating}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`h-4 w-4 ${evaluating ? "animate-spin" : ""}`} />
            <span>{evaluating ? "Evaluating DAG Gaps..." : "Re-Calculate Skill Gaps"}</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      {toastMessage && (
        <div
          className={`p-4 rounded-xl border text-sm flex items-center justify-between animate-fadeIn ${
            toastMessage.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-rose-500/10 border-rose-500/30 text-rose-300"
          }`}
        >
          <div className="flex items-center gap-2.5">
            {toastMessage.type === "success" ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />
            )}
            <span>{toastMessage.text}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-xs font-bold opacity-70 hover:opacity-100">
            Dismiss
          </button>
        </div>
      )}

      {/* Control Panel: Target Selector & Study Pace */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          {/* Target Mode Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mr-2 flex items-center gap-1.5">
              <Target className="h-4 w-4 text-indigo-400" /> Target Mode:
            </span>
            <div className="p-1 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-1">
              <button
                onClick={() => {
                  setEvalMode("ROLE");
                  handleEvaluate(selectedRole, undefined, weeklyHours);
                }}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  evalMode === "ROLE"
                    ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Standard Role Benchmark
              </button>
              <button
                onClick={() => {
                  setEvalMode("JOB");
                  handleEvaluate(undefined, selectedJobId, weeklyHours);
                }}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  evalMode === "JOB"
                    ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Specific Ingested Job
              </button>
            </div>
          </div>

          {/* Study Pace Slider */}
          <div className="flex items-center gap-4 text-xs">
            <span className="text-slate-400 font-semibold flex items-center gap-1">
              <Clock className="h-3.5 w-3.5 text-cyan-400" /> Available Study Pace:
            </span>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min="5"
                max="40"
                step="5"
                value={weeklyHours}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setWeeklyHours(val);
                  handleEvaluate(undefined, undefined, val);
                }}
                className="w-28 accent-indigo-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
              <span className="font-mono font-bold text-cyan-300 w-16 text-right">
                {weeklyHours} hrs/wk
              </span>
            </div>
          </div>
        </div>

        {/* Role Chips or Job Dropdown */}
        {evalMode === "ROLE" ? (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-400">Select Industry Role Benchmark:</div>
            <div className="flex flex-wrap items-center gap-2">
              {roleBenchmarks.map((role) => {
                const isSelected = selectedRole === role.role_slug;
                return (
                  <button
                    key={role.role_slug}
                    onClick={() => {
                      setSelectedRole(role.role_slug);
                      handleEvaluate(role.role_slug, undefined, weeklyHours);
                    }}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all border ${
                      isSelected
                        ? "bg-indigo-600/30 border-indigo-500 text-indigo-200 shadow-md shadow-indigo-500/20 font-bold"
                        : "bg-slate-950/60 border-slate-800/90 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span>{role.role_name}</span>
                      <span className="text-[10px] text-emerald-400 font-mono">({role.typical_ctc_range})</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-400">Select Active Target Job:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {jobs.map((job) => {
                const isSelected = selectedJobId === job.id;
                return (
                  <button
                    key={job.id}
                    onClick={() => {
                      setSelectedJobId(job.id);
                      handleEvaluate(undefined, job.id, weeklyHours);
                    }}
                    className={`p-3 rounded-xl text-left transition-all border ${
                      isSelected
                        ? "bg-indigo-600/30 border-indigo-500 text-white shadow-md shadow-indigo-500/20"
                        : "bg-slate-950/60 border-slate-800/90 text-slate-300 hover:bg-slate-800/40"
                    }`}
                  >
                    <div className="text-xs font-bold text-cyan-400 truncate">{job.company}</div>
                    <div className="text-sm font-semibold text-white truncate">{job.title}</div>
                    <div className="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                      <span>{job.location}</span>
                      <span className="font-mono text-emerald-400">
                        {job.min_salary ? `₹${(job.min_salary / 100000).toFixed(0)}L+` : "Competitive"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Executive Gap Summary Metrics */}
      {report && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Readiness Gauge */}
          <div className="p-6 rounded-2xl bg-[#0d1424] border border-indigo-500/30 shadow-xl flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Role Readiness</span>
              <div className="text-2xl lg:text-3xl font-bold text-white flex items-baseline gap-1">
                <span className={report.readiness_score >= 75 ? "text-emerald-400" : report.readiness_score >= 50 ? "text-indigo-300" : "text-amber-400"}>
                  {report.readiness_score}%
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                {report.matched_skills_count} of {report.total_skills_required} competencies verified
              </p>
            </div>
            <div className={`h-14 w-14 rounded-2xl flex items-center justify-center font-bold text-base border ${
              report.readiness_score >= 75
                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                : report.readiness_score >= 50
                ? "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
                : "bg-amber-500/20 text-amber-300 border-amber-500/40"
            }`}>
              <TrendingUp className="h-6 w-6" />
            </div>
          </div>

          {/* Total Effort Hours */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Learning Effort</span>
              <div className="text-2xl lg:text-3xl font-bold text-cyan-300 font-mono">
                {report.total_estimated_hours}h
              </div>
              <p className="text-[11px] text-slate-400">
                Across all critical & recommended gaps
              </p>
            </div>
            <div className="h-14 w-14 rounded-2xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center justify-center">
              <Clock className="h-6 w-6" />
            </div>
          </div>

          {/* Timeline in Weeks */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Readiness Timeline</span>
              <div className="text-2xl lg:text-3xl font-bold text-emerald-400 font-mono">
                {report.estimated_weeks} wks
              </div>
              <p className="text-[11px] text-slate-400">
                At steady pace of {weeklyHours} hrs/week
              </p>
            </div>
            <div className="h-14 w-14 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center justify-center">
              <Zap className="h-6 w-6" />
            </div>
          </div>

          {/* Gap Breakdown */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Actionable Deficits</span>
              <div className="text-xl font-bold text-white flex items-center gap-2">
                <span className="text-rose-400 font-mono">{report.missing_critical_count} Missing</span>
                <span className="text-slate-600">•</span>
                <span className="text-amber-400 font-mono">{report.proficiency_gap_count} Upgrades</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Sorted by topological DAG order
              </p>
            </div>
            <div className="h-14 w-14 rounded-2xl bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center justify-center">
              <Layers className="h-6 w-6" />
            </div>
          </div>
        </div>
      )}

      {/* Main Analysis View Tabs */}
      <div className="space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("matrix")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === "matrix"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60"
              }`}
            >
              ROI Priority Matrix (4 Quadrants)
            </button>
            <button
              onClick={() => setActiveTab("pathway")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === "pathway"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60"
              }`}
            >
              Optimal Step-by-Step Learning Order
            </button>
            <button
              onClick={() => setActiveTab("dag")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === "dag"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60"
              }`}
            >
              Prerequisite DAG Dependency Chain
            </button>
          </div>

          <Link
            href="/learning"
            className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/30 transition-all"
          >
            <GraduationCap className="h-4 w-4" />
            <span>Generate Adaptive Learning Roadmap (Phase 7)</span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        {loading ? (
          <div className="py-20 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
            <span>Computing deterministic prerequisite graph and gap matrix...</span>
          </div>
        ) : !report ? (
          <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
            <GitCompare className="h-10 w-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-white">No Gap Analysis Generated Yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Select a target role or job above and click "Re-Calculate Skill Gaps" to execute the analysis.
            </p>
          </div>
        ) : activeTab === "matrix" ? (
          /* 4-Quadrant Priority Matrix */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Quick Wins */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-emerald-500/40 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-emerald-500/20 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-300">
                    <Zap className="h-4 w-4" />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-white">1. Quick Wins (High ROI / Fast Effort)</h3>
                    <p className="text-[10px] text-emerald-400 font-medium">Low effort (≤15h), immediate career impact</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30">
                  {report.priority_matrix.quick_wins.length} Skills
                </span>
              </div>

              <div className="space-y-2.5">
                {report.priority_matrix.quick_wins.map((item) => (
                  <div key={item.slug} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{item.skill_name}</span>
                        <span className="text-[10px] px-2 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-xs font-mono font-bold text-cyan-400">{item.estimated_hours}h</span>
                    </div>
                    <div className="text-[11px] text-slate-400">{item.recommended_action}</div>
                  </div>
                ))}
                {report.priority_matrix.quick_wins.length === 0 && (
                  <div className="text-xs text-slate-500 italic py-4 text-center">No quick wins required at this time.</div>
                )}
              </div>
            </div>

            {/* Major Milestones */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-indigo-500/40 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-300">
                    <Target className="h-4 w-4" />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-white">2. Major Milestones (Core Competencies)</h3>
                    <p className="text-[10px] text-indigo-300 font-medium">Critical required skills needing deep mastery (&gt;15h)</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-indigo-300 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30">
                  {report.priority_matrix.major_milestones.length} Skills
                </span>
              </div>

              <div className="space-y-2.5">
                {report.priority_matrix.major_milestones.map((item) => (
                  <div key={item.slug} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{item.skill_name}</span>
                        <span className="text-[10px] px-2 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-xs font-mono font-bold text-indigo-300">{item.estimated_hours}h</span>
                    </div>
                    <div className="text-[11px] text-slate-400">{item.recommended_action}</div>
                  </div>
                ))}
                {report.priority_matrix.major_milestones.length === 0 && (
                  <div className="text-xs text-slate-500 italic py-4 text-center">All major milestone requirements satisfied! 🎉</div>
                )}
              </div>
            </div>

            {/* Deep Dives */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-purple-500/30 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-purple-500/20 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-purple-500/20 text-purple-300">
                    <Layers className="h-4 w-4" />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-white">3. Deep Dives (Advanced Specializations)</h3>
                    <p className="text-[10px] text-purple-400 font-medium">Recommended architectural skills (&gt;15h)</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-purple-300 px-2 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/30">
                  {report.priority_matrix.deep_dives.length} Skills
                </span>
              </div>

              <div className="space-y-2.5">
                {report.priority_matrix.deep_dives.map((item) => (
                  <div key={item.slug} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{item.skill_name}</span>
                      <span className="text-xs font-mono text-purple-300">{item.estimated_hours}h</span>
                    </div>
                    <div className="text-[11px] text-slate-400">{item.recommended_action}</div>
                  </div>
                ))}
                {report.priority_matrix.deep_dives.length === 0 && (
                  <div className="text-xs text-slate-500 italic py-4 text-center">No deep dive gaps.</div>
                )}
              </div>
            </div>

            {/* Electives & Polish */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-700/60 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-slate-800 text-slate-300">
                    <SlidersHorizontal className="h-4 w-4" />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-white">4. Electives & Polish</h3>
                    <p className="text-[10px] text-slate-400 font-medium">Secondary skills & preferred bonus tooling (≤15h)</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-slate-400 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                  {report.priority_matrix.electives.length} Skills
                </span>
              </div>

              <div className="space-y-2.5">
                {report.priority_matrix.electives.map((item) => (
                  <div key={item.slug} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{item.skill_name}</span>
                      <span className="text-xs font-mono text-slate-400">{item.estimated_hours}h</span>
                    </div>
                    <div className="text-[11px] text-slate-400">{item.recommended_action}</div>
                  </div>
                ))}
                {report.priority_matrix.electives.length === 0 && (
                  <div className="text-xs text-slate-500 italic py-4 text-center">No electives remaining.</div>
                )}
              </div>
            </div>
          </div>
        ) : activeTab === "pathway" ? (
          /* Step-by-Step Topological Pathway Table */
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-bold text-white">Topological Step-by-Step Learning Sequence</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Derived using Directed Acyclic Graph (DAG) sorting. No skill will be attempted before its upstream prerequisites are satisfied.
                </p>
              </div>
            </div>

            <div className="divide-y divide-slate-800/80">
              {report.learning_pathway.map((step) => (
                <div key={step.slug} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-3.5 flex-1">
                    <div className="h-8 w-8 rounded-xl bg-indigo-600/30 border border-indigo-500/50 text-indigo-300 font-bold font-mono text-xs flex items-center justify-center shrink-0">
                      #{step.order}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{step.skill_name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                          step.unlock_status === "UNLOCKED"
                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                        }`}>
                          {step.unlock_status === "UNLOCKED" ? "Ready to Learn" : "Prerequisites Needed"}
                        </span>
                        <span className="text-[10px] text-slate-500">({step.category})</span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">{step.recommended_action}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 shrink-0 text-xs">
                    <div className="text-right">
                      <span className="text-[10px] text-slate-500 uppercase block">Est. Time</span>
                      <span className="font-mono font-bold text-cyan-300 text-sm">{step.estimated_hours} hrs</span>
                    </div>
                    <Link
                      href="/learning"
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white transition-all"
                    >
                      <span>Study</span>
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Prerequisite DAG Visualizer */
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
            <div>
              <h3 className="text-base font-bold text-white">Prerequisite DAG Graph Nodes & States</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Nodes are tagged into: <strong className="text-emerald-400">Acquired</strong> (verified in Career Twin), <strong className="text-cyan-400">Unlocked</strong> (prerequisites satisfied, ready to study), and <strong className="text-amber-400">Locked</strong> (waiting on foundational skills).
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {report.prerequisite_graph.nodes.map((node) => (
                <div
                  key={node.id}
                  className={`p-4 rounded-xl border transition-all ${
                    node.unlock_status === "ACQUIRED"
                      ? "bg-emerald-950/20 border-emerald-500/30"
                      : node.unlock_status === "UNLOCKED"
                      ? "bg-indigo-950/30 border-cyan-500/40 shadow-sm shadow-cyan-500/10"
                      : "bg-slate-950/60 border-slate-800 opacity-80"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-white">{node.name}</span>
                    {node.unlock_status === "ACQUIRED" ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    ) : node.unlock_status === "UNLOCKED" ? (
                      <Unlock className="h-4 w-4 text-cyan-400" />
                    ) : (
                      <Lock className="h-4 w-4 text-amber-400" />
                    )}
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Proficiency:</span>
                      <span className="font-mono font-bold text-white">
                        {Math.round(node.current_proficiency * 100)}% / {Math.round(node.required_proficiency * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          node.unlock_status === "ACQUIRED"
                            ? "bg-emerald-400"
                            : "bg-cyan-400"
                        }`}
                        style={{ width: `${Math.min(100, (node.current_proficiency / node.required_proficiency) * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
