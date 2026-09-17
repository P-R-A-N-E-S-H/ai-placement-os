"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  resumesApi,
  ResumeDetailResponse,
} from "@/lib/api/resumes";
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Trash2,
  Layers,
  Award,
  ExternalLink,
  Code2,
  Cpu,
  BarChart3,
  RefreshCw,
  FileCheck,
  Zap,
} from "lucide-react";

export default function ResumeIntelligencePage() {
  const { user, token } = useAuth();

  const [resumes, setResumes] = useState<ResumeDetailResponse[]>([]);
  const [selectedResume, setSelectedResume] = useState<ResumeDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (token) {
      loadResumes();
    }
  }, [token]);

  const loadResumes = async () => {
    if (!token) return;
    setLoading(true);
    setErrorMessage(null);
    const res = await resumesApi.list(token);
    if (res.error) {
      setErrorMessage(res.error);
    } else if (res.data) {
      setResumes(res.data);
      if (res.data.length > 0 && !selectedResume) {
        setSelectedResume(res.data[0]);
      }
    }
    setLoading(false);
  };

  const handleFileUpload = async (file: File) => {
    if (!token) {
      setErrorMessage("Please sign in or create an account to upload and analyze your resume.");
      return;
    }

    const validExts = [".pdf", ".docx", ".txt"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!validExts.includes(ext)) {
      setErrorMessage("Unsupported file format. Please upload a .pdf, .docx, or .txt document.");
      return;
    }

    setUploading(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    setUploadStep(1);

    // Progressive visual steps
    const stepInterval = setInterval(() => {
      setUploadStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 450);

    const res = await resumesApi.upload(file, token);
    clearInterval(stepInterval);

    if (res.error) {
      setErrorMessage(res.error);
      setUploading(false);
      setUploadStep(0);
    } else if (res.data) {
      setUploadStep(4);
      setTimeout(() => {
        setUploading(false);
        setUploadStep(0);
        setSelectedResume(res.data);
        setResumes((prev) => [res.data!, ...prev.filter((r) => r.id !== res.data!.id)]);
        setSuccessMessage(`Resume "${file.name}" successfully parsed, evaluated, and synced with Career Digital Twin!`);
      }, 500);
    }
  };

  const handleDeleteResume = async (resumeId: string) => {
    if (!token) return;
    if (!confirm("Are you sure you want to delete this resume?")) return;

    const res = await resumesApi.delete(resumeId, token);
    if (res.error) {
      setErrorMessage(res.error);
    } else {
      const updated = resumes.filter((r) => r.id !== resumeId);
      setResumes(updated);
      if (selectedResume?.id === resumeId) {
        setSelectedResume(updated.length > 0 ? updated[0] : null);
      }
      setSuccessMessage("Resume successfully deleted.");
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
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

  return (
    <div className="min-h-screen bg-[#060a12] text-slate-100 p-6 lg:p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Phase 3 Agent
            </span>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
              Zero-Mock Production Ready
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <FileText className="h-7 w-7 text-indigo-400" />
            Resume Intelligence & ATS Optimization Agent
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ingest candidate resumes (.pdf, .docx, .txt), extract canonical skills, compute deterministic ATS mathematical scorecards, and sync with your Career Digital Twin.
          </p>
        </div>

        {selectedResume && (
          <div className="flex items-center gap-3">
            <Link
              href="/career-twin"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30 transition-all shadow-sm shadow-emerald-500/10"
            >
              <BrainCircuit className="h-4 w-4" />
              <span>Inspect Career Twin</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        )}
      </div>

      {/* Notifications */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-rose-400 hover:text-rose-200 text-xs font-bold">
            Dismiss
          </button>
        </div>
      )}

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-emerald-400 hover:text-emerald-200 text-xs font-bold">
            Dismiss
          </button>
        </div>
      )}

      {!token && (
        <div className="p-5 rounded-xl bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 border border-indigo-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Candidate Authentication Required</h3>
              <p className="text-xs text-slate-400">
                Log in to link parsed resume skills, project evidence, and academic metrics directly into your live database.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/30"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all border border-slate-700"
            >
              Create Account
            </Link>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload & Resumes List (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Upload Dropzone Card */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Upload className="h-4 w-4 text-indigo-400" />
                Upload New Resume
              </h2>
              <span className="text-[10px] text-slate-400 font-mono">.pdf, .docx, .txt</span>
            </div>

            <div
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
                isDragOver
                  ? "border-indigo-400 bg-indigo-500/10 scale-[1.01]"
                  : "border-slate-700/80 hover:border-slate-600 bg-slate-950/40 hover:bg-slate-950/70"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />

              <div className="h-12 w-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-inner">
                {uploading ? (
                  <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
                ) : (
                  <Upload className="h-6 w-6" />
                )}
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-200">
                  {uploading ? "Analyzing Document..." : "Click or drag resume file here"}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Supported formats: PDF, Microsoft Word (.docx), Plain Text (.txt)
                </p>
              </div>

              <button
                type="button"
                disabled={uploading}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-medium transition-all shadow-sm shadow-indigo-600/30 mt-1"
              >
                Browse File
              </button>
            </div>

            {/* Stepper if uploading */}
            {uploading && (
              <div className="mt-4 p-3.5 rounded-xl bg-slate-950/80 border border-indigo-500/30 space-y-2.5 animate-fadeIn">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-indigo-300">Agent Processing Pipeline</span>
                  <span className="text-slate-400">{uploadStep}/4</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${(uploadStep / 4) * 100}%` }}
                  ></div>
                </div>
                <div className="space-y-1 text-[11px]">
                  <div className={`flex items-center gap-2 ${uploadStep >= 1 ? "text-emerald-400" : "text-slate-400"}`}>
                    <CheckCircle2 className="h-3 w-3" />
                    <span>1. Ingesting & Extracting Raw Document</span>
                  </div>
                  <div className={`flex items-center gap-2 ${uploadStep >= 2 ? "text-emerald-400" : "text-slate-400"}`}>
                    <CheckCircle2 className="h-3 w-3" />
                    <span>2. Canonical Skill Mapping & Alias Resolution</span>
                  </div>
                  <div className={`flex items-center gap-2 ${uploadStep >= 3 ? "text-emerald-400" : "text-slate-400"}`}>
                    <CheckCircle2 className="h-3 w-3" />
                    <span>3. Deterministic 4-Factor ATS Evaluation</span>
                  </div>
                  <div className={`flex items-center gap-2 ${uploadStep >= 4 ? "text-emerald-400" : "text-slate-400"}`}>
                    <CheckCircle2 className="h-3 w-3" />
                    <span>4. Synchronizing with Career Digital Twin</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Upload History List */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-cyan-400" />
                Uploaded Resumes
              </h2>
              <span className="text-xs text-slate-400 font-medium">{resumes.length} total</span>
            </div>

            {loading ? (
              <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin text-indigo-400" />
                Loading candidate resumes...
              </div>
            ) : resumes.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-400 border border-dashed border-slate-800 rounded-xl">
                No resumes uploaded yet. Upload your first resume above.
              </div>
            ) : (
              <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                {resumes.map((r) => {
                  const isSelected = selectedResume?.id === r.id;
                  return (
                    <div
                      key={r.id}
                      onClick={() => setSelectedResume(r)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between group ${
                        isSelected
                          ? "bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10"
                          : "bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 overflow-hidden">
                        <div
                          className={`p-2 rounded-lg border shrink-0 ${
                            isSelected
                              ? "bg-indigo-600/20 border-indigo-500/40 text-indigo-300"
                              : "bg-slate-800/60 border-slate-700/60 text-slate-400"
                          }`}
                        >
                          <FileText className="h-4 w-4" />
                        </div>
                        <div className="truncate">
                          <p className="text-xs font-semibold text-slate-200 truncate">{r.file_name}</p>
                          <p className="text-[10px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                            <span>{r.file_type.toUpperCase()}</span>
                            <span>•</span>
                            <span>{(r.file_size_bytes / 1024).toFixed(1)} KB</span>
                            <span>•</span>
                            <span>{new Date(r.created_at).toLocaleDateString()}</span>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <div
                          className={`px-2 py-0.5 rounded-full text-[11px] font-bold border ${getScoreColor(
                            r.ats_score
                          )}`}
                        >
                          {r.ats_score.toFixed(0)}%
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteResume(r.id);
                          }}
                          className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors opacity-0 group-hover:opacity-100"
                          title="Delete resume"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Scorecard & Extracted Sections Explorer (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {selectedResume ? (
            <>
              {/* ATS Scorecard Overview Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-900/90 via-slate-900/60 to-slate-950/80 border border-slate-800/90 shadow-2xl backdrop-blur-md">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/70 pb-5">
                  <div>
                    <span className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase font-mono">
                      Active Resume Scorecard
                    </span>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2 mt-0.5">
                      {selectedResume.file_name}
                    </h2>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Evaluated via 4-Factor Deterministic Mathematical Scoring Engine
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Format:</span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {selectedResume.file_type.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400 ml-2">Synced:</span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Career Twin
                    </span>
                  </div>
                </div>

                {/* Score Dial & 4 Subscores */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mt-6 items-center">
                  {/* Big Overall Gauge */}
                  <div className="md:col-span-4 flex flex-col items-center justify-center p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <div className="relative flex items-center justify-center">
                      <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          className="stroke-slate-800"
                          strokeWidth="8"
                          fill="transparent"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="42"
                          className={`${getScoreRingColor(selectedResume.ats_score)} transition-all duration-1000`}
                          strokeWidth="8"
                          strokeDasharray={264}
                          strokeDashoffset={264 - (264 * selectedResume.ats_score) / 100}
                          strokeLinecap="round"
                          fill="transparent"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center justify-center text-center">
                        <span className="text-2xl font-black tracking-tight text-white">
                          {selectedResume.ats_score.toFixed(0)}
                          <span className="text-xs text-slate-400">/100</span>
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                          ATS Rating
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 text-center">
                      <span
                        className={`text-xs font-bold px-2.5 py-1 rounded-full border ${getScoreColor(
                          selectedResume.ats_score
                        )}`}
                      >
                        {selectedResume.ats_score >= 80
                          ? "Placement Ready (Top 10%)"
                          : selectedResume.ats_score >= 65
                          ? "Competitive (Target: 80+)"
                          : "Needs Optimization"}
                      </span>
                    </div>
                  </div>

                  {/* 4 Deterministic Subscore Bars */}
                  <div className="md:col-span-8 space-y-3">
                    {/* Completeness */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                          <Layers className="h-3.5 w-3.5 text-indigo-400" />
                          Section Completeness (25%)
                        </span>
                        <span className="font-mono text-indigo-300 font-bold">
                          {selectedResume.ats_feedback.sub_scores.section_completeness}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${selectedResume.ats_feedback.sub_scores.section_completeness}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Quantification */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                          <BarChart3 className="h-3.5 w-3.5 text-cyan-400" />
                          Quantification Coverage (25%)
                        </span>
                        <span className="font-mono text-cyan-300 font-bold">
                          {selectedResume.ats_feedback.sub_scores.quantification_coverage}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${selectedResume.ats_feedback.sub_scores.quantification_coverage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Skill Density */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                          <Cpu className="h-3.5 w-3.5 text-emerald-400" />
                          Canonical Skill Density (30%)
                        </span>
                        <span className="font-mono text-emerald-300 font-bold">
                          {selectedResume.ats_feedback.sub_scores.skill_density}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${selectedResume.ats_feedback.sub_scores.skill_density}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Action Verb Quality */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                          <Award className="h-3.5 w-3.5 text-purple-400" />
                          Action Verb & Impact Quality (20%)
                        </span>
                        <span className="font-mono text-purple-300 font-bold">
                          {selectedResume.ats_feedback.sub_scores.bullet_verb_quality}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-purple-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${selectedResume.ats_feedback.sub_scores.bullet_verb_quality}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Strengths & Actionable Improvements Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-5 border-t border-slate-800/80">
                  {/* Strengths */}
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                    <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" /> Detected Strengths
                    </h3>
                    <ul className="space-y-1.5">
                      {selectedResume.ats_feedback.strengths.map((str, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 shrink-0 mt-0.5">•</span>
                          <span>{str}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Improvements */}
                  <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                    <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                      <TrendingUp className="h-4 w-4" /> Actionable Improvements
                    </h3>
                    <ul className="space-y-1.5">
                      {selectedResume.ats_feedback.actionable_improvements.length > 0 ? (
                        selectedResume.ats_feedback.actionable_improvements.map((imp, idx) => (
                          <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                            <span className="text-amber-400 shrink-0 mt-0.5">•</span>
                            <span>{imp}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-xs text-emerald-300">
                          Excellent resume formulation! All key scoring thresholds met.
                        </li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Extracted Structured Sections */}
              <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-xl backdrop-blur-md space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800/70 pb-4">
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Code2 className="h-5 w-5 text-indigo-400" />
                    Extracted Candidate Twin Entities
                  </h2>
                  <span className="text-xs text-slate-400">Auto-populated into Database</span>
                </div>

                {/* Contact & Academic Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Contact Details */}
                  <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-2">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Contact Information
                    </h4>
                    <div className="space-y-1 text-xs">
                      <p className="text-slate-200">
                        <span className="text-slate-400">Name:</span>{" "}
                        {selectedResume.parsed_data.contact_info.name || "Candidate"}
                      </p>
                      <p className="text-slate-200">
                        <span className="text-slate-400">Email:</span>{" "}
                        {selectedResume.parsed_data.contact_info.email || "Not found"}
                      </p>
                      <p className="text-slate-200">
                        <span className="text-slate-400">Phone:</span>{" "}
                        {selectedResume.parsed_data.contact_info.phone || "Not found"}
                      </p>
                      {selectedResume.parsed_data.contact_info.github_url && (
                        <p className="text-indigo-300 flex items-center gap-1">
                          <span className="text-slate-400">GitHub:</span>
                          <a
                            href={selectedResume.parsed_data.contact_info.github_url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:underline flex items-center gap-0.5"
                          >
                            {selectedResume.parsed_data.contact_info.github_url}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Education Details */}
                  <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-2">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Education Credentials
                    </h4>
                    {selectedResume.parsed_data.education.length > 0 ? (
                      selectedResume.parsed_data.education.map((edu, idx) => (
                        <div key={idx} className="space-y-1 text-xs">
                          <p className="font-semibold text-slate-200">
                            {edu.degree} in {edu.branch}
                          </p>
                          <p className="text-slate-400">
                            {edu.institution || "University / College"} • Graduating {edu.graduation_year}
                          </p>
                          <p className="text-emerald-400 font-mono font-bold">
                            CGPA / Grade: {edu.cgpa ? edu.cgpa.toFixed(2) : "N/A"}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400">No education entries extracted.</p>
                    )}
                  </div>
                </div>

                {/* Canonical Skills Extracted */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Canonical Skills Extracted ({selectedResume.parsed_data.skills.length})
                    </h4>
                    <span className="text-[11px] text-emerald-400 font-mono">
                      Matched to PlacementOS Ontology
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedResume.parsed_data.skills.map((sk, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-950/60 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5 shadow-sm shadow-indigo-500/10"
                      >
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Projects & Engineering Bullets */}
                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Extracted Projects & Achievements
                  </h4>
                  <div className="space-y-3">
                    {selectedResume.parsed_data.projects.map((proj, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-2"
                      >
                        <h5 className="text-xs font-bold text-white flex items-center gap-2">
                          <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
                          {proj.title}
                        </h5>
                        <ul className="space-y-1.5 pl-2">
                          {proj.bullet_points.map((bullet, bIdx) => (
                            <li key={bIdx} className="text-xs text-slate-300 flex items-start gap-2">
                              <span className="text-slate-400 shrink-0 mt-0.5">›</span>
                              <span>{bullet}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* Empty State */
            <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800/80 text-center space-y-4">
              <div className="h-16 w-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
                <FileText className="h-8 w-8" />
              </div>
              <div className="space-y-1 max-w-md mx-auto">
                <h3 className="text-base font-bold text-white">No Resume Selected</h3>
                <p className="text-xs text-slate-400">
                  Upload candidate resume in PDF, DOCX, or TXT format on the left to trigger the Resume Intelligence Agent pipeline.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
