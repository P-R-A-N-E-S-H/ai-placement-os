"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  TrendingUp,
  BrainCircuit,
  FileText,
  Briefcase,
  Code2,
  Mic,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { analyticsApi, AnalyticsOverview } from "@/lib/api/analytics";

export default function DashboardPage() {
  const { user, profile, token, isAuthenticated } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardMetrics();
  }, [token, isAuthenticated]);

  const loadDashboardMetrics = async () => {
    setLoading(true);
    const { data } = await analyticsApi.getOverview(token || undefined, !isAuthenticated);
    if (data) {
      setAnalytics(data);
    }
    setLoading(false);
  };

  const displayName = profile?.full_name || (user ? user.email.split("@")[0] : "Alex Parker");
  const targetRole = profile?.target_roles?.[0] || "AI / Software Engineer";

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/60 via-slate-900/80 to-slate-950 p-6 md:p-8 backdrop-blur-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/3 w-64 h-64 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
              <Sparkles className="h-3.5 w-3.5" />
              <span>
                {analytics?.is_seeded_demo
                  ? "Demo Mode — Sign In to activate your Personal Digital Twin"
                  : "Personal Career Digital Twin Synced"}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Welcome back, <span className="text-gradient">{displayName}</span>
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              Your AI Career Team analyzed active engineering opportunities and personalized your placement preparation roadmap for target role: <strong className="text-slate-200 font-semibold">{targetRole}</strong>.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <Link
              href="/career-twin"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all transform hover:-translate-y-0.5"
            >
              <BrainCircuit className="h-4 w-4" />
              <span>Career Digital Twin</span>
            </Link>
            <Link
              href="/profile"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-medium text-xs transition-all"
            >
              <FileText className="h-4 w-4" />
              <span>Edit Profile</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 4 Core Placement Readiness Scorecards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Placement Readiness Score */}
        <div className="glass-card glass-card-hover rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Placement Readiness</span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">
              {analytics?.placement_readiness_score || 0}%
            </span>
            <span className="text-xs text-emerald-400 font-medium flex items-center">
              +6% this week
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${analytics?.placement_readiness_score || 0}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400">Targeting Top 5% Placement Tier</p>
        </div>

        {/* Skill Gap Coverage */}
        <div className="glass-card glass-card-hover rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Skill Match</span>
            <BrainCircuit className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">
              {analytics?.skill_match_percentage || 0}%
            </span>
            <span className="text-xs text-indigo-400 font-medium">
              {analytics?.total_skills_count || 0} skills registered
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${analytics?.skill_match_percentage || 0}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400">
            {analytics?.verified_skills_count || 0} verified with evidence
          </p>
        </div>

        {/* DSA Progress */}
        <div className="glass-card glass-card-hover rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">DSA Solved</span>
            <Code2 className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">
              {analytics?.dsa_problems_solved !== null ? analytics?.dsa_problems_solved : 0}
            </span>
            <span className="text-xs text-slate-400 font-medium">/ 180 curated</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full"
              style={{ width: `${Math.min(100, ((analytics?.dsa_problems_solved || 0) / 180) * 100)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400">Focus: Dynamic Programming & Graphs</p>
        </div>

        {/* Mock Interview Score */}
        <div className="glass-card glass-card-hover rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Interview Score</span>
            <Mic className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">
              {analytics?.mock_interview_score !== null ? `${analytics?.mock_interview_score}/100` : "Pending"}
            </span>
            <span className="text-xs text-amber-400 font-medium">Technical & HR</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-amber-500 to-emerald-400 h-full rounded-full"
              style={{ width: `${analytics?.mock_interview_score || 0}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400">Take a mock interview to calibrate score</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Agent Status & Registered Skills */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Agent Fleet Status */}
          <div className="glass-card rounded-xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <h3 className="text-sm font-semibold text-white">LangGraph Agent Fleet</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Digital Twin Checkpoints Synced</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">Resume Agent</span>
                  <span className="text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-500/20">Ready</span>
                </div>
                <p className="text-[11px] text-slate-400">Canonical taxonomy parser & ATS analyzer.</p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">Job Match Engine</span>
                  <span className="text-[10px] text-indigo-400 bg-indigo-950/40 px-1.5 py-0.5 rounded border border-indigo-500/20">6-Factor</span>
                </div>
                <p className="text-[11px] text-slate-400">Hybrid semantic + skill weight evaluator.</p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">Learning Planner</span>
                  <span className="text-[10px] text-cyan-400 bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-500/20">Adaptive</span>
                </div>
                <p className="text-[11px] text-slate-400">Dynamic curriculum driven by skill gaps.</p>
              </div>
            </div>
          </div>

          {/* Top Matched Jobs */}
          <div className="glass-card rounded-xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Top Matched Job Opportunities</h3>
                <p className="text-xs text-slate-400">Ranked by hybrid deterministic + semantic match score</p>
              </div>
              <Link href="/jobs" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium">
                View All <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              {[
                {
                  company: "DeepMind / Google",
                  role: "Associate AI Research Engineer",
                  location: "Bengaluru, India (Hybrid)",
                  match: 91,
                  tags: ["PyTorch", "Transformers", "Distributed Training"],
                },
                {
                  company: "Microsoft",
                  role: "Software Development Engineer - I",
                  location: "Hyderabad / Remote",
                  match: 87,
                  tags: ["C++", "System Design", "Cloud Architecture"],
                },
                {
                  company: "Amazon",
                  role: "Applied Scientist Intern",
                  location: "Bengaluru, India",
                  match: 84,
                  tags: ["Python", "Algorithms", "LLMs"],
                },
              ].map((job, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-200">{job.role}</span>
                      <span className="text-[11px] text-slate-400">• {job.company}</span>
                    </div>
                    <p className="text-xs text-slate-400">{job.location}</p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {job.tags.map((tag) => (
                        <span key={tag} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md border border-slate-700/60">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center sm:flex-col items-end justify-between sm:justify-center gap-2">
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 font-mono text-xs font-semibold">
                      <Zap className="h-3 w-3 text-indigo-400" />
                      <span>{job.match}% Match</span>
                    </div>
                    <Link
                      href="/jobs"
                      className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                    >
                      Inspect Fit <ArrowUpRight className="h-3 w-3" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Today's Action Plan & Application Tracker */}
        <div className="space-y-6">
          {/* Today's Adaptive Tasks */}
          <div className="glass-card rounded-xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Today's Placement Plan</h3>
              <span className="text-xs text-indigo-400 font-medium">Day 24 of 56</span>
            </div>

            <div className="space-y-2.5">
              {[
                { title: "Solve DP on Trees: Binary Tree Maximum Path Sum", time: "45 mins", type: "DSA", done: true },
                { title: "Review RAG Chunking Strategies for Mock Interview", time: "30 mins", type: "Concepts", done: false },
                { title: "Complete 15-min Technical Mock: LLM Fine-Tuning", time: "15 mins", type: "Interview", done: false },
              ].map((task, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border transition-all ${
                    task.done
                      ? "bg-emerald-950/20 border-emerald-500/20 text-slate-400"
                      : "bg-slate-900/60 border-slate-800 text-slate-200"
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    <CheckCircle2
                      className={`h-4 w-4 mt-0.5 shrink-0 ${
                        task.done ? "text-emerald-400" : "text-slate-600"
                      }`}
                    />
                    <div className="space-y-1">
                      <p className={`text-xs font-medium leading-snug ${task.done ? "line-through text-slate-400" : "text-slate-200"}`}>
                        {task.title}
                      </p>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400">
                        <Clock className="h-3 w-3" />
                        <span>{task.time}</span>
                        <span>•</span>
                        <span className="text-indigo-400">{task.type}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <Link
              href="/learning"
              className="w-full mt-2 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs font-medium text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>View Full Learning Roadmap</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          {/* Application Pipeline Summary */}
          <div className="glass-card rounded-xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Application Pipeline</h3>
              <Link href="/applications" className="text-xs text-indigo-400 hover:text-indigo-300">
                Kanban Board
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-2 text-center font-mono">
              <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-lg font-bold text-white">12</div>
                <div className="text-[10px] text-slate-400 uppercase font-sans">Applied</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-lg font-bold text-indigo-400">4</div>
                <div className="text-[10px] text-slate-400 uppercase font-sans">Online Test</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-lg font-bold text-amber-400">2</div>
                <div className="text-[10px] text-slate-400 uppercase font-sans">Interviewing</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-lg font-bold text-emerald-400">1</div>
                <div className="text-[10px] text-slate-400 uppercase font-sans">Offers</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
