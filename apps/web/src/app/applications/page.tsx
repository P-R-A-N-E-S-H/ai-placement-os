"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  KanbanSquare,
  PlusCircle,
  Building2,
  MapPin,
  Calendar,
  CheckCircle2,
  Clock,
  Briefcase,
  TrendingUp,
  Award,
  ChevronRight,
  ChevronLeft,
  Trash2,
  Filter,
  Search,
  Sparkles,
  DollarSign,
  Download,
  Mic,
  GitCompare,
  FileText,
  ExternalLink,
} from "lucide-react";
import {
  applicationsApi,
  ApplicationResponse,
  ApplicationStatsResponse,
  ApplicationCreateRequest,
} from "@/lib/api/applications";
import { useAuth } from "@/context/AuthContext";

const STAGES = [
  { key: "SAVED", label: "Saved", color: "border-slate-700 bg-slate-900/40 text-slate-300" },
  { key: "APPLIED", label: "Applied", color: "border-blue-500/30 bg-blue-950/20 text-blue-300" },
  { key: "OA_SCHEDULED", label: "OA / Test", color: "border-purple-500/30 bg-purple-950/20 text-purple-300" },
  { key: "TECHNICAL_ROUND", label: "Tech Rounds", color: "border-amber-500/30 bg-amber-950/20 text-amber-300" },
  { key: "HR_ROUND", label: "HR / Bar-Raiser", color: "border-cyan-500/30 bg-cyan-950/20 text-cyan-300" },
  { key: "OFFER_EXTENDED", label: "Offer Extended", color: "border-emerald-500/30 bg-emerald-950/20 text-emerald-300" },
  { key: "REJECTED", label: "Archived", color: "border-rose-500/30 bg-rose-950/20 text-rose-400" },
];

export default function ApplicationsPage() {
  const { token } = useAuth();
  const [applications, setApplications] = useState<ApplicationResponse[]>([]);
  const [stats, setStats] = useState<ApplicationStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"kanban" | "table">("kanban");
  const [searchFilter, setSearchFilter] = useState("");
  const [stageFilter, setStageFilter] = useState("ALL");

  // Create Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCompany, setNewCompany] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newSalary, setNewSalary] = useState("");
  const [newStage, setNewStage] = useState("APPLIED");
  const [newNotes, setNewNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [appsRes, statsRes] = await Promise.all([
        applicationsApi.list(undefined, token || undefined),
        applicationsApi.getStats(token || undefined),
      ]);
      if (appsRes.data) setApplications(appsRes.data);
      if (statsRes.data) setStats(statsRes.data);
    } catch (err) {
      console.error("Failed to load application data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCompany.trim() || !newTitle.trim()) return;
    setIsSubmitting(true);
    try {
      const res = await applicationsApi.create(
        {
          company_name: newCompany,
          job_title: newTitle,
          location: newLocation || undefined,
          salary_offered: newSalary || undefined,
          stage: newStage,
          notes: newNotes || undefined,
        },
        token || undefined
      );
      if (res.data) {
        setShowCreateModal(false);
        setNewCompany("");
        setNewTitle("");
        setNewLocation("");
        setNewSalary("");
        setNewNotes("");
        loadData();
      }
    } catch (err) {
      console.error("Failed to create application", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStageChange = async (appId: string, nextStage: string) => {
    try {
      await applicationsApi.update(appId, { stage: nextStage }, token || undefined);
      loadData();
    } catch (err) {
      console.error("Failed to update application stage", err);
    }
  };

  const handleStepStage = async (app: ApplicationResponse, direction: "next" | "prev") => {
    const currentIdx = STAGES.findIndex((s) => s.key === app.stage);
    if (currentIdx === -1) return;
    const targetIdx = direction === "next" ? currentIdx + 1 : currentIdx - 1;
    if (targetIdx >= 0 && targetIdx < STAGES.length) {
      await handleStageChange(app.id, STAGES[targetIdx].key);
    }
  };

  const handleDelete = async (appId: string) => {
    if (!confirm("Remove this application from tracking?")) return;
    try {
      await applicationsApi.delete(appId, token || undefined);
      loadData();
    } catch (err) {
      console.error("Failed to delete application", err);
    }
  };

  const exportCSV = () => {
    const headers = ["Company", "Job Title", "Stage", "Location", "Salary", "Applied At", "Notes"];
    const rows = applications.map((a) => [
      `"${a.company_name}"`,
      `"${a.job_title}"`,
      `"${a.stage}"`,
      `"${a.location || ""}"`,
      `"${a.salary_offered || ""}"`,
      `"${new Date(a.applied_at).toLocaleDateString()}"`,
      `"${(a.notes || "").replace(/"/g, '""')}"`,
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `placement_applications_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredApps = applications.filter((a) => {
    const matchesSearch =
      a.company_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      a.job_title.toLowerCase().includes(searchFilter.toLowerCase());
    const matchesStage = stageFilter === "ALL" || a.stage === stageFilter;
    return matchesSearch && matchesStage;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 text-slate-100 p-2 md:p-4">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-cyan-950/60 via-indigo-950/40 to-slate-900/70 border border-cyan-500/20 p-8 shadow-2xl backdrop-blur-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold uppercase tracking-wider">
              <KanbanSquare className="h-3.5 w-3.5" />
              Recruitment Kanban & Pipeline OS
            </div>
            <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
              Placement Pipeline & Offer Tracker
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              Track multi-stage job applications from initial application to online assessments, technical rounds, bar-raisers, and final compensation offers with instant mock interview prep shortcuts.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={exportCSV}
              className="px-4 py-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer"
            >
              <Download className="h-4 w-4" />
              Export CSV
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2 cursor-pointer active:scale-98"
            >
              <PlusCircle className="h-4 w-4" />
              Track New Application
            </button>
          </div>
        </div>
      </div>

      {/* Pipeline Velocity & Offer Metrics */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Total Pipeline</div>
            <div className="text-2xl font-black text-white font-mono">{stats.total_applications}</div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[10px] text-blue-400 font-semibold uppercase">Applied</div>
            <div className="text-2xl font-black text-blue-300 font-mono">{stats.applied_count}</div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[10px] text-purple-400 font-semibold uppercase">OA / Tests</div>
            <div className="text-2xl font-black text-purple-300 font-mono">{stats.oa_scheduled_count}</div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[10px] text-amber-400 font-semibold uppercase">Tech Rounds</div>
            <div className="text-2xl font-black text-amber-300 font-mono">{stats.technical_round_count}</div>
          </div>
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[10px] text-cyan-400 font-semibold uppercase">HR / Behavioral</div>
            <div className="text-2xl font-black text-cyan-300 font-mono">{stats.hr_round_count}</div>
          </div>
          <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 space-y-1">
            <div className="text-[10px] text-emerald-400 font-semibold uppercase">Offers Received</div>
            <div className="text-2xl font-black text-emerald-300 flex items-center gap-1.5 font-mono">
              <span>{stats.offers_count}</span>
              <Award className="h-4 w-4 text-emerald-400" />
            </div>
          </div>
        </div>
      )}

      {/* Filter & View Mode Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search company name or target role..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="ALL">All Stages</option>
            {STAGES.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setViewMode("kanban")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              viewMode === "kanban" ? "bg-cyan-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Kanban Board
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              viewMode === "table" ? "bg-cyan-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Table View
          </button>
        </div>
      </div>

      {/* KANBAN BOARD VIEW */}
      {viewMode === "kanban" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4 items-start overflow-x-auto pb-6">
          {STAGES.map((col, colIdx) => {
            const stageApps = filteredApps.filter((a) => a.stage === col.key);
            return (
              <div
                key={col.key}
                className="rounded-2xl bg-slate-900/40 border border-slate-800/80 p-3.5 space-y-3 min-w-[210px]"
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <span className="text-xs font-bold text-slate-300">{col.label}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                    {stageApps.length}
                  </span>
                </div>

                <div className="space-y-2.5 min-h-[160px]">
                  {stageApps.map((app) => (
                    <div
                      key={app.id}
                      className="rounded-xl bg-slate-950/80 border border-slate-800/90 p-3.5 space-y-3 hover:border-cyan-500/40 transition-all shadow-md group"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                            {app.company_name}
                          </div>
                          <div className="text-[11px] text-slate-400">{app.job_title}</div>
                        </div>
                        <button
                          onClick={() => handleDelete(app.id)}
                          className="text-slate-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity p-1 cursor-pointer"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>

                      {app.salary_offered && (
                        <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                          <DollarSign className="h-3 w-3" />
                          <span>{app.salary_offered}</span>
                        </div>
                      )}

                      {app.notes && (
                        <p className="text-[10px] text-slate-400 line-clamp-2 italic leading-relaxed">
                          "{app.notes}"
                        </p>
                      )}

                      {/* Role Preparation Quick Shortcuts */}
                      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between gap-1">
                        <Link
                          href={`/interview?role=${encodeURIComponent(app.job_title)}&company=${encodeURIComponent(app.company_name)}`}
                          className="text-[9px] px-2 py-1 rounded bg-indigo-950/50 hover:bg-indigo-900/70 text-indigo-300 border border-indigo-500/30 flex items-center gap-1 transition"
                          title="Practice Mock Interview for this company"
                        >
                          <Mic className="h-3 w-3" />
                          <span>Mock Prep</span>
                        </Link>
                        <Link
                          href="/skills"
                          className="text-[9px] px-2 py-1 rounded bg-cyan-950/50 hover:bg-cyan-900/70 text-cyan-300 border border-cyan-500/30 flex items-center gap-1 transition"
                          title="Check Skill Gaps"
                        >
                          <GitCompare className="h-3 w-3" />
                          <span>Gaps</span>
                        </Link>
                      </div>

                      {/* Stage Stepper Actions */}
                      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                        <button
                          onClick={() => handleStepStage(app, "prev")}
                          disabled={colIdx === 0}
                          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white disabled:opacity-20 cursor-pointer"
                          title="Move stage back"
                        >
                          <ChevronLeft className="h-3.5 w-3.5" />
                        </button>

                        <span className="text-[9px] text-slate-500 font-mono">
                          {new Date(app.applied_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                        </span>

                        <button
                          onClick={() => handleStepStage(app, "next")}
                          disabled={colIdx === STAGES.length - 1}
                          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white disabled:opacity-20 cursor-pointer"
                          title="Advance stage forward"
                        >
                          <ChevronRight className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* TABLE VIEW */
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="p-4">Company</th>
                <th className="p-4">Role</th>
                <th className="p-4">Stage</th>
                <th className="p-4">Location</th>
                <th className="p-4">Salary</th>
                <th className="p-4">Quick Prep</th>
                <th className="p-4">Applied Date</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredApps.map((app) => (
                <tr key={app.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-bold text-white">{app.company_name}</td>
                  <td className="p-4 text-slate-300">{app.job_title}</td>
                  <td className="p-4">
                    <select
                      value={app.stage}
                      onChange={(e) => handleStageChange(app.id, e.target.value)}
                      className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-cyan-300 focus:outline-none"
                    >
                      {STAGES.map((s) => (
                        <option key={s.key} value={s.key}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="p-4 text-slate-400">{app.location || "Remote / Hybrid"}</td>
                  <td className="p-4 text-emerald-400 font-mono">{app.salary_offered || "Negotiable"}</td>
                  <td className="p-4">
                    <Link
                      href={`/interview?role=${encodeURIComponent(app.job_title)}&company=${encodeURIComponent(app.company_name)}`}
                      className="px-2.5 py-1 rounded bg-indigo-950/40 text-indigo-300 border border-indigo-500/30 text-[10px] font-semibold hover:bg-indigo-900/60 inline-flex items-center gap-1"
                    >
                      <Mic className="h-3 w-3" />
                      Mock Prep
                    </Link>
                  </td>
                  <td className="p-4 text-slate-500 font-mono">
                    {new Date(app.applied_at).toLocaleDateString()}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => handleDelete(app.id)}
                      className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: Track Application */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-3xl bg-slate-900 border border-slate-800 p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Building2 className="h-5 w-5 text-cyan-400" />
                Track New Job Application
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white text-xs font-mono cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  placeholder="e.g. Google"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Job Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. AI / Machine Learning Engineer"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Location</label>
                  <input
                    type="text"
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    placeholder="e.g. San Francisco / Bengaluru"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Salary Range</label>
                  <input
                    type="text"
                    value={newSalary}
                    onChange={(e) => setNewSalary(e.target.value)}
                    placeholder="e.g. ₹28L - ₹36L / $165k"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Initial Stage</label>
                <select
                  value={newStage}
                  onChange={(e) => setNewStage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  {STAGES.map((s) => (
                    <option key={s.key} value={s.key}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Notes / Referral Info</label>
                <textarea
                  rows={3}
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  placeholder="Referral contact, recruiter note, timeline..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !newCompany.trim() || !newTitle.trim()}
                  className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all shadow-lg shadow-cyan-600/25 disabled:opacity-50 cursor-pointer"
                >
                  {isSubmitting ? "Tracking..." : "Save Application"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
