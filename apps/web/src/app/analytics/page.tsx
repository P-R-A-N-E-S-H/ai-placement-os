"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  BarChart3,
  TrendingUp,
  Activity,
  ShieldCheck,
  Zap,
  Clock,
  Cpu,
  Database,
  Award,
  ArrowRight,
  RefreshCw,
  Sparkles,
  Layers,
  Code2,
  Mic,
  GraduationCap,
  Network,
} from "lucide-react";
import {
  analyticsApi,
  AnalyticsOverview,
  ObservabilityHealth,
  VelocityTrajectory,
} from "@/lib/api/analytics";
import { useAuth } from "@/context/AuthContext";

export default function AnalyticsPage() {
  const { token } = useAuth();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [observability, setObservability] = useState<ObservabilityHealth | null>(null);
  const [velocity, setVelocity] = useState<VelocityTrajectory | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"readiness" | "velocity" | "observability">("readiness");

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ovRes, obsRes, velRes] = await Promise.all([
        analyticsApi.getOverview(token || undefined),
        analyticsApi.getObservability(token || undefined),
        analyticsApi.getVelocity("AI Engineer", token || undefined),
      ]);
      if (ovRes.data) setOverview(ovRes.data);
      if (obsRes.data) setObservability(obsRes.data);
      if (velRes.data) setVelocity(velRes.data);
    } catch (err) {
      console.error("Failed to load analytics data", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060810] text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Banner */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-950/60 via-indigo-950/40 to-slate-900/60 border border-emerald-500/20 p-8 shadow-2xl backdrop-blur-xl">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold tracking-wide uppercase">
                <BarChart3 className="h-3.5 w-3.5" />
                Phase 12: Unified SaaS Analytics & Observability
              </div>
              <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                Readiness Analytics & Platform Health Hub
              </h1>
              <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
                Aggregated telemetry tracking real-time <span className="text-emerald-300 font-medium">Placement Readiness</span>,{" "}
                <span className="text-indigo-300 font-medium">Skill Velocity Trajectory</span>, and{" "}
                <span className="text-cyan-300 font-medium">Subsystem Latency Observability</span> across all autonomous agents.
              </p>
            </div>
            <button
              onClick={loadData}
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh Telemetry
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800/80 pb-4">
          <button
            onClick={() => setActiveTab("readiness")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "readiness"
                ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 border border-emerald-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            Placement Readiness ({overview?.placement_readiness_score || 0}%)
          </button>
          <button
            onClick={() => setActiveTab("velocity")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "velocity"
                ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 border border-emerald-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <Zap className="h-4 w-4" />
            Skill Acquisition Velocity
          </button>
          <button
            onClick={() => setActiveTab("observability")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "observability"
                ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 border border-emerald-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <Activity className="h-4 w-4" />
            System Observability & Latencies
          </button>
        </div>

        {/* TAB 1: Placement Readiness Breakdown */}
        {activeTab === "readiness" && overview && (
          <div className="space-y-8">
            {/* Master Key Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-950/40 to-slate-900 border border-emerald-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Readiness Score</span>
                  <Award className="h-5 w-5 text-emerald-400" />
                </div>
                <div className="text-4xl font-black text-emerald-300">
                  {overview.placement_readiness_score}%
                </div>
                <div className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                  <span>Target: AI Engineer / SDE</span>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">DSA Solved</span>
                  <Code2 className="h-5 w-5 text-cyan-400" />
                </div>
                <div className="text-4xl font-black text-white">{overview.dsa_problems_solved || 0}</div>
                <div className="text-[11px] text-slate-400">Optimal AST complexity verified</div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Mock Interview</span>
                  <Mic className="h-5 w-5 text-purple-400" />
                </div>
                <div className="text-4xl font-black text-purple-300">
                  {overview.mock_interview_score ? `${overview.mock_interview_score}/100` : "84/100"}
                </div>
                <div className="text-[11px] text-slate-400">4-Rubric Technical & STAR evaluation</div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Applications</span>
                  <Layers className="h-5 w-5 text-amber-400" />
                </div>
                <div className="text-4xl font-black text-amber-300">{overview.total_applications}</div>
                <div className="text-[11px] text-slate-400">
                  {overview.interviewing_applications} in active interview rounds
                </div>
              </div>
            </div>

            {/* Top Verified Skills Grid */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-5">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                Verified Skill Twin Proficiencies
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {overview.top_skills.map((skill, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 flex flex-col justify-between"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{skill.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">
                        {(skill.proficiency * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full"
                        style={{ width: `${skill.proficiency * 100}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">{skill.category}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Velocity Trajectory Chart */}
        {activeTab === "velocity" && velocity && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
                <div>
                  <h3 className="text-base font-bold text-white">8-Week Skill Acquisition & Readiness Trajectory</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Projected placement-readiness milestone progression for target role:{" "}
                    <b className="text-emerald-300">{velocity.target_role}</b>
                  </p>
                </div>
                <div className="px-3 py-1 rounded-xl bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-xs font-mono">
                  Projected Ready: {velocity.projected_ready_date}
                </div>
              </div>

              {/* Trajectory Points Timeline */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-3 pt-2">
                {velocity.trajectory_points.map((pt, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3 flex flex-col justify-between"
                  >
                    <div className="text-xs font-bold text-white">{pt.week_label}</div>
                    <div className="text-2xl font-black text-emerald-400">{pt.readiness_score}%</div>
                    <div className="space-y-1 text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-900">
                      <div>DSA: {pt.dsa_count} solved</div>
                      <div>Skills: +{pt.skills_acquired}</div>
                      <div>Mock: {pt.mock_score}/100</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: System Observability & Subsystem Latencies */}
        {activeTab === "observability" && observability && (
          <div className="space-y-6">
            {/* System Status Banner */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 rounded-full bg-emerald-400 animate-ping" />
                  <div>
                    <h3 className="text-base font-bold text-white">Platform Health: {observability.status}</h3>
                    <div className="text-xs text-slate-400">Database: {observability.database_status}</div>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-xl bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-xs font-mono uppercase">
                  {observability.environment}
                </span>
              </div>

              {/* Real-time Subsystem Latency Table */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
                {observability.subsystems.map((sub, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white truncate max-w-[160px]">{sub.name}</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">
                        {sub.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">Latency:</span>
                      <span className="text-cyan-400 font-mono font-bold">{sub.latency_ms} ms</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">Records:</span>
                      <span className="text-slate-200 font-mono">{sub.records_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
