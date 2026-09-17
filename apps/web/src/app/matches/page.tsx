"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { matchesApi, JobMatch } from "@/lib/api/matches";
import {
  BrainCircuit,
  Sparkles,
  RefreshCw,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Award,
  Layers,
  BarChart3,
  Building2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Target,
  Zap,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

export default function MatchesHubPage() {
  const { user, token } = useAuth();

  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [batchMatching, setBatchMatching] = useState<boolean>(false);
  const [minScoreFilter, setMinScoreFilter] = useState<number | undefined>(undefined);
  const [expandedMatchId, setExpandedMatchId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const loadMatches = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    const res = await matchesApi.list(token, minScoreFilter);
    if (res.data) {
      setMatches(res.data);
    }
    setLoading(false);
  }, [token, minScoreFilter]);

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  const handleRunBatchMatch = async () => {
    if (!token) return;
    setBatchMatching(true);
    setToastMessage(null);
    const res = await matchesApi.batch(token, 50);
    if (res.data) {
      setMatches(res.data.matches);
      setToastMessage(
        `Successfully evaluated ${res.data.total_evaluated} active opportunities against your Career Digital Twin!`
      );
    }
    setBatchMatching(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 65) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-rose-400 border-rose-500/30 bg-rose-500/10";
  };

  const getScoreRingColor = (score: number) => {
    if (score >= 80) return "stroke-emerald-400";
    if (score >= 65) return "stroke-amber-400";
    return "stroke-rose-400";
  };

  const readyMatchesCount = matches.filter((m) => m.overall_score >= 80).length;
  const topScore = matches.length > 0 ? Math.max(...matches.map((m) => m.overall_score)) : 0;

  return (
    <div className="min-h-screen bg-[#060a12] text-slate-100 p-6 lg:p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Phase 5 Engine
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
              6-Factor Deterministic Match
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <BrainCircuit className="h-7 w-7 text-indigo-400" />
            Hybrid Job–Resume Matching Hub
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Compare your Career Digital Twin against active opportunities across Skill Coverage, Experience, Academics, Semantic Similarity, and Evidence Strength.
          </p>
        </div>

        {/* Action Buttons */}
        {token && (
          <button
            onClick={handleRunBatchMatch}
            disabled={batchMatching}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/30 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${batchMatching ? "animate-spin" : ""}`} />
            <span>{batchMatching ? "Calculating Match Matrix..." : "Batch Match All Opportunities"}</span>
          </button>
        )}
      </div>

      {/* Notifications */}
      {toastMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-xs font-bold opacity-80 hover:opacity-100">
            Dismiss
          </button>
        </div>
      )}

      {!token ? (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 border border-indigo-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">Sign In to Compute Live Matching</h3>
            <p className="text-xs text-slate-400">
              Your candidate profile, uploaded resumes, and verified skill evidence will be compared against live jobs.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all border border-slate-700"
            >
              Register
            </Link>
          </div>
        </div>
      ) : (
        <>
          {/* Telemetry KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <Target className="h-5 w-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Top Match Score</span>
                <p className="text-xl font-bold text-white">{topScore.toFixed(1)}%</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Placement Ready (80%+)</span>
                <p className="text-xl font-bold text-emerald-400">{readyMatchesCount} Roles</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Zap className="h-5 w-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Evaluated Opportunities</span>
                <p className="text-xl font-bold text-cyan-400">{matches.length} Total</p>
              </div>
            </div>
          </div>

          {/* Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            <span className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider mr-1">
              Match Fit:
            </span>
            {[
              { label: "All Calculated", val: undefined },
              { label: "Placement Ready (80%+)", val: 80 },
              { label: "Moderate Fit (65-79%)", val: 65 },
            ].map((f) => {
              const isSelected = minScoreFilter === f.val;
              return (
                <button
                  key={f.label}
                  onClick={() => setMinScoreFilter(f.val)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    isSelected
                      ? "bg-indigo-600 text-white font-bold shadow-sm shadow-indigo-600/30"
                      : "bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800"
                  }`}
                >
                  {f.label}
                </button>
              );
            })}
          </div>

          {/* Matches List */}
          {loading ? (
            <div className="py-20 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-3">
              <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
              <span>Evaluating candidate digital twin matrix...</span>
            </div>
          ) : matches.length === 0 ? (
            <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
              <BrainCircuit className="h-10 w-10 text-slate-600 mx-auto" />
              <h3 className="text-sm font-bold text-white">No Match Scores Calculated Yet</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Click "Batch Match All Opportunities" above to evaluate your Career Digital Twin against all active job postings.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {matches.map((match) => {
                const isExpanded = expandedMatchId === match.id;
                return (
                  <div
                    key={match.id}
                    className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-lg space-y-4 hover:border-slate-700 transition-all"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      {/* Left: Score Gauge & Job Header */}
                      <div className="flex items-center gap-4">
                        {/* Radial Overall Score Gauge */}
                        <div className="relative flex items-center justify-center shrink-0">
                          <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 100 100">
                            <circle
                              cx="50"
                              cy="50"
                              r="40"
                              className="stroke-slate-800"
                              strokeWidth="8"
                              fill="transparent"
                            />
                            <circle
                              cx="50"
                              cy="50"
                              r="40"
                              className={`${getScoreRingColor(match.overall_score)} transition-all duration-700`}
                              strokeWidth="8"
                              strokeDasharray={251}
                              strokeDashoffset={251 - (251 * match.overall_score) / 100}
                              strokeLinecap="round"
                              fill="transparent"
                            />
                          </svg>
                          <div className="absolute flex flex-col items-center justify-center text-center">
                            <span className="text-sm font-black text-white">
                              {match.overall_score.toFixed(0)}%
                            </span>
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-cyan-400">
                              {match.job?.company || "Target Company"}
                            </span>
                            <span className="text-slate-600">•</span>
                            <span className="text-xs text-slate-400">
                              {match.job?.location || "Remote"}
                            </span>
                            <span
                              className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${getScoreColor(
                                match.overall_score
                              )}`}
                            >
                              {match.overall_score >= 80
                                ? "High Placement Fit"
                                : match.overall_score >= 65
                                ? "Moderate Fit"
                                : "Skill Gap Opportunity"}
                            </span>
                          </div>

                          <h3 className="text-base font-bold text-white mt-0.5">
                            {match.job?.title || "Software Engineering Role"}
                          </h3>

                          <p className="text-xs text-slate-400 mt-0.5">
                            Evaluated on {new Date(match.calculated_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      {/* Right CTA */}
                      <div className="flex items-center gap-2.5 shrink-0">
                        <button
                          onClick={() =>
                            setExpandedMatchId(isExpanded ? null : match.id)
                          }
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all border border-slate-700"
                        >
                          <span>{isExpanded ? "Hide Breakdown" : "View Breakdown"}</span>
                          {isExpanded ? (
                            <ChevronUp className="h-3.5 w-3.5" />
                          ) : (
                            <ChevronDown className="h-3.5 w-3.5" />
                          )}
                        </button>

                        <Link
                          href="/jobs"
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-sm"
                        >
                          <span>Job Portal</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </div>
                    </div>

                    {/* 6-Factor Mini Progress Meters */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-3 border-t border-slate-800/60">
                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Skills (30%)</span>
                          <span className="font-mono text-indigo-300 font-bold">{match.skill_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${match.skill_score}%` }}></div>
                        </div>
                      </div>

                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Exp (20%)</span>
                          <span className="font-mono text-cyan-300 font-bold">{match.experience_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${match.experience_score}%` }}></div>
                        </div>
                      </div>

                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Edu (10%)</span>
                          <span className="font-mono text-emerald-300 font-bold">{match.education_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${match.education_score}%` }}></div>
                        </div>
                      </div>

                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Semantic (15%)</span>
                          <span className="font-mono text-purple-300 font-bold">{match.semantic_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-purple-500 h-full rounded-full" style={{ width: `${match.semantic_score}%` }}></div>
                        </div>
                      </div>

                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Evidence (15%)</span>
                          <span className="font-mono text-amber-300 font-bold">{match.evidence_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-amber-500 h-full rounded-full" style={{ width: `${match.evidence_score}%` }}></div>
                        </div>
                      </div>

                      <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Pref (10%)</span>
                          <span className="font-mono text-blue-300 font-bold">{match.preference_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-blue-500 h-full rounded-full" style={{ width: `${match.preference_score}%` }}></div>
                        </div>
                      </div>
                    </div>

                    {/* Matched vs Missing Skills Quick Bar */}
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      {match.matched_required_skills.map((sk) => (
                        <span
                          key={sk}
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 flex items-center gap-1"
                        >
                          <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                          {sk}
                        </span>
                      ))}
                      {match.missing_required_skills.map((sk) => (
                        <span
                          key={sk}
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/80 text-rose-300 border border-rose-500/40 flex items-center gap-1"
                        >
                          <AlertCircle className="h-3 w-3 text-rose-400" />
                          Missing: {sk}
                        </span>
                      ))}
                    </div>

                    {/* Detailed Expander (Strengths, Gaps, Recommendations) */}
                    {isExpanded && (
                      <div className="pt-4 border-t border-slate-800/80 space-y-4 animate-fadeIn">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Strengths */}
                          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                              <CheckCircle2 className="h-4 w-4" /> Match Strengths
                            </h4>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {match.explanation.strengths.map((st, idx) => (
                                <li key={idx} className="flex items-start gap-1.5">
                                  <span className="text-emerald-400 shrink-0">•</span>
                                  <span>{st}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* Gaps & Recommendations */}
                          <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                            <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                              <TrendingUp className="h-4 w-4" /> Actionable Gaps (Phase 6 Ready)
                            </h4>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {match.explanation.gaps.map((gp, idx) => (
                                <li key={idx} className="flex items-start gap-1.5">
                                  <span className="text-amber-400 shrink-0">•</span>
                                  <span>{gp}</span>
                                </li>
                              ))}
                              {match.explanation.recommendations.map((rc, idx) => (
                                <li key={idx} className="flex items-start gap-1.5 text-cyan-300">
                                  <span className="text-cyan-400 shrink-0">→</span>
                                  <span>{rc}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
