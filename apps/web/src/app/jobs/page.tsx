"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  jobsApi,
  JobSummary,
  JobDetail,
  JobSourceStatus,
} from "@/lib/api/jobs";
import { matchesApi, JobMatch } from "@/lib/api/matches";
import {
  Briefcase,
  Search,
  MapPin,
  Building2,
  DollarSign,
  Sparkles,
  RefreshCw,
  ExternalLink,
  SlidersHorizontal,
  CheckCircle2,
  AlertCircle,
  BrainCircuit,
  ArrowRight,
  Layers,
  Clock,
  ShieldCheck,
  ChevronRight,
  X,
  Zap,
} from "lucide-react";

const POPULAR_SKILL_FILTERS = [
  "Python",
  "PyTorch",
  "LangGraph",
  "LangChain",
  "FastAPI",
  "React",
  "Next.js",
  "TypeScript",
  "Go",
  "PostgreSQL",
  "Docker",
  "Kubernetes",
  "DSA",
];

export default function JobDiscoveryPage() {
  const { user, token } = useAuth();

  // Job Listing State
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [totalJobs, setTotalJobs] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [locationType, setLocationType] = useState<string>("");
  const [employmentType, setEmploymentType] = useState<string>("");
  const [selectedSkill, setSelectedSkill] = useState<string>("");
  const [minSalary, setMinSalary] = useState<number | undefined>(undefined);

  // Selected Detail Modal
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [jobDetail, setJobDetail] = useState<JobDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  // Match Engine State (Phase 5)
  const [activeMatch, setActiveMatch] = useState<JobMatch | null>(null);
  const [evaluatingMatch, setEvaluatingMatch] = useState<boolean>(false);
  const [matchError, setMatchError] = useState<string | null>(null);

  // Ingestion & Telemetry State
  const [ingesting, setIngesting] = useState<boolean>(false);
  const [sourceStatuses, setSourceStatuses] = useState<JobSourceStatus[]>([]);
  const [showTelemetryModal, setShowTelemetryModal] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    const res = await jobsApi.list({
      search: searchQuery || undefined,
      location_type: locationType || undefined,
      employment_type: employmentType || undefined,
      skill: selectedSkill || undefined,
      min_salary: minSalary,
      page: currentPage,
      page_size: 15,
    });

    if (res.data) {
      setJobs(res.data.items);
      setTotalJobs(res.data.total);
      setTotalPages(res.data.total_pages);
    }
    setLoading(false);
  }, [searchQuery, locationType, employmentType, selectedSkill, minSalary, currentPage]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    loadTelemetry();
  }, []);

  const loadTelemetry = async () => {
    const res = await jobsApi.getSourceStatus();
    if (res.data) {
      setSourceStatuses(res.data.sources);
    }
  };

  const handleSelectJob = async (jobId: string) => {
    setSelectedJobId(jobId);
    setDetailLoading(true);
    setActiveMatch(null);
    setMatchError(null);
    const res = await jobsApi.getById(jobId);
    if (res.data) {
      setJobDetail(res.data);
      // If user is authenticated, try fetching existing match
      if (token) {
        const matchRes = await matchesApi.get(jobId, token);
        if (matchRes.data) {
          setActiveMatch(matchRes.data);
        }
      }
    }
    setDetailLoading(false);
  };

  const handleEvaluateMatch = async (jobId: string) => {
    if (!token) {
      setToastMessage({ type: "error", text: "Please sign in to evaluate Career Twin match score." });
      return;
    }
    setEvaluatingMatch(true);
    setMatchError(null);
    const res = await matchesApi.calculate(jobId, token);
    if (res.data) {
      setActiveMatch(res.data);
      setToastMessage({ type: "success", text: `Match calculated: ${res.data.overall_score}% overall fit score!` });
    } else {
      setMatchError(res.error || "Failed to calculate match score");
    }
    setEvaluatingMatch(false);
  };

  const handleTriggerIngest = async () => {
    setIngesting(true);
    setToastMessage(null);
    const res = await jobsApi.triggerIngest(token || undefined);
    if (res.error) {
      setToastMessage({ type: "error", text: res.error });
    } else if (res.data) {
      setToastMessage({
        type: "success",
        text: `Ingestion complete! Fetched ${res.data.total_fetched}, Inserted ${res.data.total_inserted}, Deduplicated ${res.data.total_duplicated} in ${res.data.duration_ms}ms.`,
      });
      await fetchJobs();
      await loadTelemetry();
    }
    setIngesting(false);
  };

  const formatSalary = (min?: number, max?: number, curr = "INR") => {
    if (!min && !max) return "Competitive Compensation";
    if (curr === "INR") {
      const minLakh = min ? (min / 100000).toFixed(1) : "";
      const maxLakh = max ? (max / 100000).toFixed(1) : "";
      if (minLakh && maxLakh) return `₹${minLakh}L - ₹${maxLakh}L / yr`;
      if (minLakh) return `From ₹${minLakh}L / yr`;
      return `Up to ₹${maxLakh}L / yr`;
    }
    return `${curr} ${min ? min.toLocaleString() : ""} - ${max ? max.toLocaleString() : ""}`;
  };

  return (
    <div className="min-h-screen bg-[#060a12] text-slate-100 p-6 lg:p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Phase 4 Agent
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
              Deduplicated & Vector-Embedded
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Briefcase className="h-7 w-7 text-cyan-400" />
            Job Discovery & Multi-Source Ingestion Agent
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Explore live, deduplicated software and AI engineering opportunities normalized against our canonical skill taxonomy.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTelemetryModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80 transition-all"
          >
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
            <span>Source Status</span>
          </button>

          <button
            onClick={handleTriggerIngest}
            disabled={ingesting}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-md shadow-cyan-600/25 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${ingesting ? "animate-spin" : ""}`} />
            <span>{ingesting ? "Ingesting Feeds..." : "Sync Live Feeds"}</span>
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
          <button
            onClick={() => setToastMessage(null)}
            className="text-xs font-bold opacity-70 hover:opacity-100"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Search & Quick Skill Filter Bar */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Search by role title, company (Google, Uber, OpenAI), keywords..."
            className="w-full pl-12 pr-4 py-3 rounded-xl bg-slate-900/90 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all shadow-inner"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-4 top-3.5 text-xs text-slate-400 hover:text-white"
            >
              Clear
            </button>
          )}
        </div>

        {/* Canonical Skill Filter Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider shrink-0 mr-1 flex items-center gap-1">
            <SlidersHorizontal className="h-3 w-3" /> Skill:
          </span>
          <button
            onClick={() => {
              setSelectedSkill("");
              setCurrentPage(1);
            }}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-all shrink-0 ${
              selectedSkill === ""
                ? "bg-cyan-600 text-white font-bold shadow-sm shadow-cyan-600/30"
                : "bg-slate-900/80 hover:bg-slate-800 text-slate-400 border border-slate-800"
            }`}
          >
            All Skills
          </button>
          {POPULAR_SKILL_FILTERS.map((sk) => {
            const isSelected = selectedSkill === sk;
            return (
              <button
                key={sk}
                onClick={() => {
                  setSelectedSkill(isSelected ? "" : sk);
                  setCurrentPage(1);
                }}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all shrink-0 ${
                  isSelected
                    ? "bg-cyan-600 text-white font-bold shadow-sm shadow-cyan-600/30"
                    : "bg-slate-900/80 hover:bg-slate-800 text-slate-400 border border-slate-800"
                }`}
              >
                {sk}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Filter Sidebar (3 cols) */}
        <div className="lg:col-span-3 space-y-5">
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-xl backdrop-blur-md space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800/70 pb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <SlidersHorizontal className="h-3.5 w-3.5 text-cyan-400" />
                Faceted Filters
              </h3>
              {(locationType || employmentType || selectedSkill || minSalary) && (
                <button
                  onClick={() => {
                    setLocationType("");
                    setEmploymentType("");
                    setSelectedSkill("");
                    setMinSalary(undefined);
                    setCurrentPage(1);
                  }}
                  className="text-[11px] text-cyan-400 hover:underline font-semibold"
                >
                  Reset All
                </button>
              )}
            </div>

            {/* Location Type */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">Workplace Mode</label>
              <div className="grid grid-cols-3 gap-1.5">
                {[
                  { label: "All", val: "" },
                  { label: "Remote", val: "REMOTE" },
                  { label: "Hybrid", val: "HYBRID" },
                  { label: "Onsite", val: "ONSITE" },
                ].map((item) => (
                  <button
                    key={item.val}
                    onClick={() => {
                      setLocationType(item.val);
                      setCurrentPage(1);
                    }}
                    className={`py-1.5 px-2 rounded-lg text-xs font-medium transition-all ${
                      locationType === item.val
                        ? "bg-cyan-600/30 border border-cyan-500/50 text-cyan-300 font-bold"
                        : "bg-slate-950/40 border border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Employment Type */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">Employment Type</label>
              <div className="space-y-1.5">
                {[
                  { label: "All Types", val: "" },
                  { label: "Full-Time Roles", val: "FULL_TIME" },
                  { label: "Internships (Campus Ready)", val: "INTERNSHIP" },
                ].map((item) => (
                  <button
                    key={item.val}
                    onClick={() => {
                      setEmploymentType(item.val);
                      setCurrentPage(1);
                    }}
                    className={`w-full py-1.5 px-3 rounded-lg text-xs font-medium text-left transition-all ${
                      employmentType === item.val
                        ? "bg-indigo-600/30 border border-indigo-500/50 text-indigo-300 font-bold"
                        : "bg-slate-950/40 border border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Minimum CTC Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <label className="font-semibold text-slate-400">Min. Target CTC</label>
                <span className="text-emerald-400 font-mono font-bold">
                  {minSalary ? `₹${(minSalary / 100000).toFixed(0)}L+` : "Any"}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="3000000"
                step="200000"
                value={minSalary || 0}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  setMinSalary(val === 0 ? undefined : val);
                  setCurrentPage(1);
                }}
                className="w-full accent-emerald-400 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>0</span>
                <span>₹10L</span>
                <span>₹20L</span>
                <span>₹30L+</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Job Cards Grid (9 cols) */}
        <div className="lg:col-span-9 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>
              Showing <strong className="text-white">{jobs.length}</strong> of{" "}
              <strong className="text-white">{totalJobs}</strong> available opportunities
            </span>
            <span className="font-mono text-[11px]">
              Page {currentPage} of {totalPages}
            </span>
          </div>

          {loading ? (
            <div className="py-20 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-3">
              <RefreshCw className="h-6 w-6 animate-spin text-cyan-400" />
              <span>Querying normalized job index...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
              <Building2 className="h-10 w-10 text-slate-600 mx-auto" />
              <h3 className="text-sm font-bold text-white">No Matching Opportunities Found</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Try adjusting your search query, clearing filters, or click "Sync Live Feeds" to ingest new roles.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => handleSelectJob(job.id)}
                  className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 hover:border-slate-700 hover:bg-slate-900/90 transition-all shadow-md group cursor-pointer"
                >
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    {/* Role & Company Header */}
                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-cyan-400">{job.company}</span>
                        <span className="text-slate-600">•</span>
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {job.location}
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                            job.location_type === "REMOTE"
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : job.location_type === "HYBRID"
                              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                              : "bg-slate-800 text-slate-300 border border-slate-700"
                          }`}
                        >
                          {job.location_type}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                          {job.employment_type.replace("_", " ")}
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors">
                        {job.title}
                      </h3>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 pt-1">
                        <span className="font-semibold text-emerald-400 flex items-center gap-1 font-mono">
                          <DollarSign className="h-3.5 w-3.5" />
                          {formatSalary(job.min_salary, job.max_salary, job.salary_currency)}
                        </span>
                        <span>•</span>
                        <span>Experience: {job.min_experience_years || 0} - {job.max_experience_years || "3+"} yrs</span>
                        <span>•</span>
                        <span className="text-slate-500">Source: {job.source}</span>
                      </div>
                    </div>

                    {/* View CTA */}
                    <button className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 group-hover:bg-cyan-600 group-hover:text-white text-slate-300 transition-all shrink-0">
                      <span>View Details</span>
                      <ChevronRight className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {/* Canonical Skills Chips */}
                  {job.skills && job.skills.length > 0 && (
                    <div className="mt-4 pt-3.5 border-t border-slate-800/70 flex flex-wrap items-center gap-1.5">
                      <span className="text-[11px] text-slate-400 mr-1">Skills:</span>
                      {job.skills.slice(0, 8).map((sk) => (
                        <span
                          key={sk.id}
                          className={`px-2 py-0.5 rounded-md text-[11px] font-medium flex items-center gap-1 ${
                            sk.is_required
                              ? "bg-indigo-950/80 text-indigo-300 border border-indigo-500/40"
                              : "bg-slate-950/60 text-slate-400 border border-slate-800"
                          }`}
                        >
                          {sk.is_required && <CheckCircle2 className="h-2.5 w-2.5 text-cyan-400" />}
                          {sk.name}
                        </span>
                      ))}
                      {job.skills.length > 8 && (
                        <span className="text-[11px] text-slate-500">+{job.skills.length - 8} more</span>
                      )}
                    </div>
                  )}
                </div>
              ))}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <button
                    disabled={currentPage <= 1}
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40"
                  >
                    Previous Page
                  </button>
                  <span className="text-xs text-slate-400 font-mono">
                    Page {currentPage} / {totalPages}
                  </span>
                  <button
                    disabled={currentPage >= totalPages}
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40"
                  >
                    Next Page
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Selected Job Detail Modal Drawer */}
      {selectedJobId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#0b101b] border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[88vh] overflow-y-auto shadow-2xl p-6 lg:p-8 space-y-6 relative">
            <button
              onClick={() => {
                setSelectedJobId(null);
                setJobDetail(null);
              }}
              className="absolute top-5 right-5 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>

            {detailLoading || !jobDetail ? (
              <div className="py-20 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="h-5 w-5 animate-spin text-cyan-400" />
                Loading detailed job telemetry...
              </div>
            ) : (
              <>
                {/* Header */}
                <div className="space-y-2 border-b border-slate-800/80 pb-5 pr-8">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-cyan-400">{jobDetail.company}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-xs text-slate-400">{jobDetail.location}</span>
                  </div>
                  <h2 className="text-xl lg:text-2xl font-bold text-white">{jobDetail.title}</h2>
                  <div className="flex flex-wrap items-center gap-3 text-xs pt-1">
                    <span className="text-emerald-400 font-mono font-bold">
                      {formatSalary(jobDetail.min_salary, jobDetail.max_salary, jobDetail.salary_currency)}
                    </span>
                    <span>•</span>
                    <span className="text-slate-300">
                      Experience: {jobDetail.min_experience_years || 0} - {jobDetail.max_experience_years || "3+"} yrs
                    </span>
                    <span>•</span>
                    <span className="text-slate-400">
                      Posted: {new Date(jobDetail.posted_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Canonical Skills Matrix */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Layers className="h-4 w-4 text-cyan-400" />
                    Required & Preferred Canonical Skills
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {jobDetail.skills.map((sk) => (
                      <span
                        key={sk.id}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 ${
                          sk.is_required
                            ? "bg-indigo-950 text-indigo-300 border border-indigo-500/40 shadow-sm"
                            : "bg-slate-900 text-slate-400 border border-slate-800"
                        }`}
                      >
                        {sk.is_required ? (
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        ) : (
                          <span className="text-[10px] text-purple-400 font-mono">Preferred</span>
                        )}
                        <span>{sk.name}</span>
                        <span className="text-[10px] text-slate-500">({sk.category})</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Career Twin Hybrid Match Scorecard (Phase 5) */}
                <div className="p-5 rounded-2xl bg-[#0e1526] border border-indigo-500/30 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-indigo-400" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
                        Career Twin Hybrid Match Engine (Phase 5)
                      </h4>
                    </div>
                    <button
                      onClick={() => handleEvaluateMatch(jobDetail.id)}
                      disabled={evaluatingMatch}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
                    >
                      <RefreshCw className={`h-3.5 w-3.5 ${evaluatingMatch ? "animate-spin" : ""}`} />
                      <span>{evaluatingMatch ? "Evaluating 6 Factors..." : activeMatch ? "Recalculate Fit" : "Evaluate Fit with My Twin"}</span>
                    </button>
                  </div>

                  {matchError && (
                    <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                      {matchError}
                    </div>
                  )}

                  {activeMatch ? (
                    <div className="space-y-4">
                      {/* Score Header */}
                      <div className="flex flex-col sm:flex-row items-center gap-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                        <div className={`h-16 w-16 rounded-2xl flex flex-col items-center justify-center font-bold text-lg shrink-0 border ${
                          activeMatch.overall_score >= 80
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                            : activeMatch.overall_score >= 60
                            ? "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
                            : "bg-amber-500/20 text-amber-300 border-amber-500/40"
                        }`}>
                          <span>{activeMatch.overall_score}%</span>
                          <span className="text-[9px] uppercase tracking-wider opacity-80">Fit Score</span>
                        </div>

                        <div className="flex-1 w-full grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Skill Fit (30%)</div>
                            <div className="font-bold text-slate-200">{activeMatch.skill_score}%</div>
                          </div>
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Experience (20%)</div>
                            <div className="font-bold text-slate-200">{activeMatch.experience_score}%</div>
                          </div>
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Semantic Cosine (15%)</div>
                            <div className="font-bold text-cyan-300">{activeMatch.semantic_score}%</div>
                          </div>
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Evidence Verified (15%)</div>
                            <div className="font-bold text-purple-300">{activeMatch.evidence_score}%</div>
                          </div>
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Education (10%)</div>
                            <div className="font-bold text-slate-200">{activeMatch.education_score}%</div>
                          </div>
                          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                            <div className="text-[10px] text-slate-400">Preferences (10%)</div>
                            <div className="font-bold text-slate-200">{activeMatch.preference_score}%</div>
                          </div>
                        </div>
                      </div>

                      {/* Matched vs Missing Required Skills */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1.5">
                          <span className="font-bold text-emerald-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Matched Skills ({activeMatch.matched_required_skills.length})
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {activeMatch.matched_required_skills.map((s) => (
                              <span key={s} className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] font-medium">
                                {s}
                              </span>
                            ))}
                            {activeMatch.matched_required_skills.length === 0 && (
                              <span className="text-[11px] text-slate-400 italic">None matched yet</span>
                            )}
                          </div>
                        </div>

                        <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-1.5">
                          <span className="font-bold text-rose-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                            <AlertCircle className="h-3.5 w-3.5" />
                            Missing Skills ({activeMatch.missing_required_skills.length})
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {activeMatch.missing_required_skills.map((s) => (
                              <span key={s} className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[11px] font-medium">
                                {s}
                              </span>
                            ))}
                            {activeMatch.missing_required_skills.length === 0 && (
                              <span className="text-[11px] text-emerald-400 font-medium">All required skills present! 🎉</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Strengths & Recommendations */}
                      {activeMatch.explanation && (
                        <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2 text-xs">
                          {activeMatch.explanation.strengths.length > 0 && (
                            <div>
                              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Key Strengths:</span>
                              <ul className="list-disc list-inside text-slate-300 text-[11px] space-y-0.5 mt-0.5">
                                {activeMatch.explanation.strengths.map((st, i) => (
                                  <li key={i}>{st}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {activeMatch.explanation.recommendations.length > 0 && (
                            <div>
                              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">Action Plan (Feed to Phase 6):</span>
                              <ul className="list-disc list-inside text-slate-300 text-[11px] space-y-0.5 mt-0.5">
                                {activeMatch.explanation.recommendations.map((rec, i) => (
                                  <li key={i}>{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                      <span>Evaluate your profile, verified skills, and resume against this job using deterministic 6-factor matching.</span>
                      <button
                        onClick={() => handleEvaluateMatch(jobDetail.id)}
                        disabled={evaluatingMatch}
                        className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shrink-0 ml-3"
                      >
                        Calculate Match
                      </button>
                    </div>
                  )}
                </div>

                {/* Job Description */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Role Description & Requirements
                  </h4>
                  <div className="p-5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 whitespace-pre-line leading-relaxed">
                    {jobDetail.description}
                  </div>
                </div>

                {/* Bottom Actions */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
                  <div className="text-[11px] text-slate-500 font-mono truncate max-w-xs">
                    Fingerprint: {jobDetail.fingerprint.slice(0, 16)}...
                  </div>

                  <div className="flex items-center gap-3">
                    <Link
                      href="/matches"
                      className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 transition-all"
                    >
                      <Sparkles className="h-4 w-4" />
                      <span>View in Match Hub</span>
                    </Link>

                    <a
                      href={jobDetail.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-md shadow-cyan-600/30"
                    >
                      <span>Apply on Source Portal</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Telemetry & Source Status Modal */}
      {showTelemetryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#0b101b] border border-slate-800 rounded-2xl w-full max-w-xl p-6 space-y-5 shadow-2xl relative">
            <button
              onClick={() => setShowTelemetryModal(false)}
              className="absolute top-5 right-5 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>

            <div className="flex items-center gap-2.5">
              <ShieldCheck className="h-5 w-5 text-cyan-400" />
              <h3 className="text-base font-bold text-white">Job Ingestion Telemetry</h3>
            </div>

            <div className="space-y-3">
              {sourceStatuses.map((src) => (
                <div
                  key={src.source_name}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white uppercase font-mono">
                      {src.source_name.replace("_", " ")}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        src.status === "SUCCESS"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      }`}
                    >
                      {src.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs text-slate-400 pt-1">
                    <div>
                      <span className="text-slate-500">Fetched:</span> {src.jobs_fetched}
                    </div>
                    <div>
                      <span className="text-slate-500">Inserted:</span> {src.jobs_inserted}
                    </div>
                    <div>
                      <span className="text-slate-500">Deduplicated:</span> {src.jobs_duplicated}
                    </div>
                  </div>

                  <div className="text-[10px] text-slate-500 flex justify-between pt-1">
                    <span>Duration: {src.duration_ms}ms</span>
                    <span>Last Run: {new Date(src.last_run).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowTelemetryModal(false)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
