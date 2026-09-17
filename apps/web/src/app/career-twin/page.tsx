"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  BrainCircuit,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  Target,
  GraduationCap,
  Briefcase,
  GitBranch,
  Layers,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { profileApi, UserProfile } from "@/lib/api/profile";
import { UserSkill } from "@/lib/api/skills";
import { analyticsApi, AnalyticsOverview } from "@/lib/api/analytics";

export default function CareerTwinPage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isLoading } = useAuth();

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    if (token) {
      loadTwinData();
    }
  }, [token, isAuthenticated, isLoading]);

  const loadTwinData = async () => {
    if (!token) return;
    setLoadingData(true);
    const [pRes, sRes, aRes] = await Promise.all([
      profileApi.getProfile(token),
      profileApi.getUserSkills(token),
      analyticsApi.getOverview(token),
    ]);

    if (pRes.data) setProfile(pRes.data);
    if (sRes.data) setSkills(sRes.data);
    if (aRes.data) setAnalytics(aRes.data);
    setLoadingData(false);
  };

  const getProficiencyLabel = (prof: number) => {
    if (prof >= 0.8) return { label: "Strong", color: "text-emerald-400 bg-emerald-950/40 border-emerald-500/30" };
    if (prof >= 0.6) return { label: "Advanced", color: "text-indigo-400 bg-indigo-950/40 border-indigo-500/30" };
    if (prof >= 0.4) return { label: "Intermediate", color: "text-cyan-400 bg-cyan-950/40 border-cyan-500/30" };
    return { label: "Basic", color: "text-amber-400 bg-amber-950/40 border-amber-500/30" };
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Top Banner: Digital Twin State */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/80 via-slate-900/90 to-slate-950 p-6 md:p-8 backdrop-blur-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-indigo-500/15 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Autonomous Career Digital Twin Active</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              {profile?.full_name || "Alex Parker"}'s Digital Twin
            </h1>
            <p className="text-slate-400 text-xs max-w-2xl leading-relaxed">
              Real-time persistent model synthesizing academic performance, skill proficiencies, verified evidence, and target role requirements.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/profile"
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Edit Profile Attributes
            </Link>
            <Link
              href="/ai-assistant"
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 text-white text-xs font-medium shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-1.5"
            >
              <BrainCircuit className="h-3.5 w-3.5" />
              <span>Consult Copilot</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 3 Core Twin Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-2">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Overall Readiness</span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white font-mono">
            {analytics?.placement_readiness_score || 0}%
          </div>
          <p className="text-[11px] text-slate-400">Calculated from verified profile & skill weights</p>
        </div>

        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-2">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Skills Registered</span>
            <Layers className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white font-mono">
            {skills.length}
          </div>
          <p className="text-[11px] text-slate-400">{skills.filter(s => s.evidence && s.evidence.length > 0).length} with verifiable evidence</p>
        </div>

        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-2">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Profile Completeness</span>
            <CheckCircle2 className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold text-white font-mono">
            {profile?.profile_completion || 15}%
          </div>
          <p className="text-[11px] text-slate-400">7-factor dynamic completion metric</p>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Verifiable Skill Graph */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-indigo-400" />
                <h3 className="text-sm font-semibold text-white">Skill Proficiency & Evidence Matrix</h3>
              </div>
              <span className="text-[11px] text-slate-400">Deterministic Scaled (0.0 - 1.0)</span>
            </div>

            <div className="space-y-4">
              {skills.map((s) => {
                const badge = getProficiencyLabel(s.proficiency);
                const percent = Math.round(s.proficiency * 100);
                return (
                  <div
                    key={s.id}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="text-xs font-bold text-slate-100">{s.skill.name}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                          {s.skill.category.replace("_", " ")}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${badge.color}`}>
                          {badge.label} ({percent}%)
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      />
                    </div>

                    {/* Evidence Tags */}
                    <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
                      <span className="text-slate-500">Evidence:</span>
                      {s.evidence && s.evidence.length > 0 ? (
                        s.evidence.map((ev) => (
                          <span
                            key={ev.id}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/80 text-[10px]"
                          >
                            <ShieldCheck className="h-3 w-3 text-emerald-400" />
                            <span>{ev.source_type}: {ev.evidence_text.slice(0, 30)}...</span>
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-slate-500 italic">User Declared (Awaiting Project/Interview Evidence)</span>
                      )}
                    </div>
                  </div>
                );
              })}

              {skills.length === 0 && (
                <div className="text-center py-8 space-y-2">
                  <p className="text-xs text-slate-400">No skills registered in your Digital Twin yet.</p>
                  <Link
                    href="/profile"
                    className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    <span>Add skills in your profile</span> <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Col: Academic & Target Role Fit */}
        <div className="space-y-6">
          {/* Target Roles Alignment */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800/80">
              <Target className="h-4 w-4 text-amber-400" />
              <h3 className="text-sm font-semibold text-white">Target Roles & Alignment</h3>
            </div>

            <div className="space-y-2">
              {(profile?.target_roles?.length ? profile.target_roles : ["AI Engineer", "Software Engineer"]).map(
                (role) => (
                  <div
                    key={role}
                    className="p-3 rounded-lg bg-slate-900/50 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <span className="font-medium text-slate-200">{role}</span>
                    <span className="text-[11px] font-mono text-indigo-300">Active Target</span>
                  </div>
                )
              )}
            </div>
          </div>

          {/* Academic Snapshot */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800/80">
              <GraduationCap className="h-4 w-4 text-cyan-400" />
              <h3 className="text-sm font-semibold text-white">Academic Baseline</h3>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Institution</span>
                <span className="text-slate-200 font-medium text-right">{profile?.college || "MIT / Tier 1"}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Degree & Branch</span>
                <span className="text-slate-200 font-medium">{profile?.degree || "B.Tech"} ({profile?.branch || "CS / AI"})</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Graduation Year</span>
                <span className="text-slate-200 font-medium font-mono">{profile?.graduation_year || 2026}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">CGPA</span>
                <span className="text-emerald-400 font-bold font-mono">{profile?.cgpa ? `${profile.cgpa}/10.0` : "8.8/10.0"}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
