"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  User,
  GraduationCap,
  Target,
  Globe,
  Clock,
  Github,
  Linkedin,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Save,
  Plus,
  Trash2,
  BrainCircuit,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { profileApi, UserProfile, ProfileCompletionBreakdown } from "@/lib/api/profile";
import { UserSkill, skillsApi, Skill } from "@/lib/api/skills";

export default function ProfilePage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isLoading } = useAuth();

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [completion, setCompletion] = useState<ProfileCompletionBreakdown | null>(null);
  const [userSkills, setUserSkills] = useState<UserSkill[]>([]);
  const [canonicalSkills, setCanonicalSkills] = useState<Skill[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillProficiency, setNewSkillProficiency] = useState(0.8);
  const [newSkillEvidence, setNewSkillEvidence] = useState("");

  // Form State
  const [fullName, setFullName] = useState("");
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");
  const [college, setCollege] = useState("");
  const [degree, setDegree] = useState("");
  const [branch, setBranch] = useState("");
  const [gradYear, setGradYear] = useState<number | undefined>(2026);
  const [cgpa, setCgpa] = useState<number | undefined>(8.8);
  const [targetRoles, setTargetRoles] = useState<string[]>(["AI Engineer", "Software Engineer"]);
  const [locations, setLocations] = useState<string[]>(["Bengaluru", "Remote"]);
  const [careerGoal, setCareerGoal] = useState("");
  const [weeklyHours, setWeeklyHours] = useState(15);
  const [githubUrl, setGithubUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    if (token) {
      loadData();
    }
  }, [token, isAuthenticated, isLoading]);

  const loadData = async () => {
    if (!token) return;
    const [pRes, cRes, sRes, taxRes] = await Promise.all([
      profileApi.getProfile(token),
      profileApi.getCompletion(token),
      profileApi.getUserSkills(token),
      skillsApi.list(),
    ]);

    if (pRes.data) {
      const p = pRes.data;
      setProfile(p);
      setFullName(p.full_name || "");
      setHeadline(p.headline || "");
      setBio(p.bio || "");
      setCollege(p.college || "");
      setDegree(p.degree || "");
      setBranch(p.branch || "");
      setGradYear(p.graduation_year || 2026);
      setCgpa(p.cgpa || 8.5);
      setTargetRoles(p.target_roles?.length ? p.target_roles : ["AI Engineer"]);
      setLocations(p.preferred_locations?.length ? p.preferred_locations : ["Bengaluru"]);
      setCareerGoal(p.career_goal || "");
      setWeeklyHours(p.weekly_available_hours || 15);
      setGithubUrl(p.github_url || "");
      setLinkedinUrl(p.linkedin_url || "");
      setPortfolioUrl(p.portfolio_url || "");
    }

    if (cRes.data) setCompletion(cRes.data);
    if (sRes.data) setUserSkills(sRes.data);
    if (taxRes.data) setCanonicalSkills(taxRes.data);
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setSaveSuccess(false);

    const payload: Partial<UserProfile> = {
      full_name: fullName,
      headline,
      bio,
      college,
      degree,
      branch,
      graduation_year: gradYear,
      cgpa,
      target_roles: targetRoles,
      preferred_locations: locations,
      career_goal: careerGoal,
      weekly_available_hours: weeklyHours,
      github_url: githubUrl,
      linkedin_url: linkedinUrl,
      portfolio_url: portfolioUrl,
    };

    const { data } = await profileApi.updateProfile(token, payload);
    setSaving(false);
    if (data) {
      setProfile(data);
      setSaveSuccess(true);
      const cRes = await profileApi.getCompletion(token);
      if (cRes.data) setCompletion(cRes.data);
      setTimeout(() => setSaveSuccess(false), 3000);
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newSkillName.trim()) return;

    const { data } = await profileApi.addUserSkill(token, {
      skill_name: newSkillName.trim(),
      proficiency: newSkillProficiency,
      evidence_text: newSkillEvidence.trim() || undefined,
    });

    if (data) {
      setNewSkillName("");
      setNewSkillEvidence("");
      // Reload skills and completion
      const [sRes, cRes] = await Promise.all([
        profileApi.getUserSkills(token),
        profileApi.getCompletion(token),
      ]);
      if (sRes.data) setUserSkills(sRes.data);
      if (cRes.data) setCompletion(cRes.data);
    }
  };

  const handleDeleteSkill = async (skillId: string) => {
    if (!token) return;
    await profileApi.deleteUserSkill(token, skillId);
    const [sRes, cRes] = await Promise.all([
      profileApi.getUserSkills(token),
      profileApi.getCompletion(token),
    ]);
    if (sRes.data) setUserSkills(sRes.data);
    if (cRes.data) setCompletion(cRes.data);
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header & Completeness Card */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Career Digital Twin Root Profile</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            {fullName || "Candidate Profile"}
          </h1>
          <p className="text-xs text-slate-400">
            {headline || "Keep your Digital Twin updated to receive personalized job matches & learning tasks."}
          </p>
        </div>

        {/* Dynamic Completion Gauge */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-right min-w-[200px]">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
            Profile Completion
          </div>
          <div className="text-2xl font-bold text-white font-mono flex items-center justify-end gap-2">
            <span>{completion?.overall_completion || profile?.profile_completion || 15}%</span>
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${completion?.overall_completion || 15}%` }}
            />
          </div>
        </div>
      </div>

      {saveSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span>Career profile updated successfully! All agent parameters synced.</span>
        </div>
      )}

      {/* Main Profile Form */}
      <form onSubmit={handleSaveProfile} className="space-y-6">
        {/* Section 1: Basic Info */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
            <User className="h-4 w-4 text-indigo-400" />
            <h2 className="text-sm font-semibold text-white">Personal & Candidate Headline</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Headline</label>
              <input
                type="text"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                placeholder="e.g. AI / Machine Learning Undergraduate @ MIT"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="sm:col-span-2 space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Bio / Summary</label>
              <textarea
                rows={2}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Brief summary of your technical interests and engineering background..."
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Education */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
            <GraduationCap className="h-4 w-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">Education & Academics</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2 space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">College / University</label>
              <input
                type="text"
                value={college}
                onChange={(e) => setCollege(e.target.value)}
                placeholder="e.g. Indian Institute of Technology / Stanford"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Degree</label>
              <input
                type="text"
                value={degree}
                onChange={(e) => setDegree(e.target.value)}
                placeholder="e.g. B.Tech / B.E. / M.S."
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Branch / Major</label>
              <input
                type="text"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                placeholder="e.g. Computer Science & AI"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Graduation Year</label>
              <input
                type="number"
                value={gradYear || ""}
                onChange={(e) => setGradYear(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">CGPA / Grade (out of 10)</label>
              <input
                type="number"
                step="0.01"
                value={cgpa || ""}
                onChange={(e) => setCgpa(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Career Goals & Target Roles */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
            <Target className="h-4 w-4 text-amber-400" />
            <h2 className="text-sm font-semibold text-white">Career Goals & Placement Targets</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Target Engineering Roles</label>
              <input
                type="text"
                value={targetRoles.join(", ")}
                onChange={(e) =>
                  setTargetRoles(
                    e.target.value
                      .split(",")
                      .map((s) => s.trim())
                      .filter(Boolean)
                  )
                }
                placeholder="AI Engineer, Software Engineer, ML Engineer"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[10px] text-slate-500">Separate multiple target roles with commas</p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Preferred Locations</label>
              <input
                type="text"
                value={locations.join(", ")}
                onChange={(e) =>
                  setLocations(
                    e.target.value
                      .split(",")
                      .map((s) => s.trim())
                      .filter(Boolean)
                  )
                }
                placeholder="Bengaluru, Hyderabad, Remote"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="sm:col-span-2 space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Primary Career Goal</label>
              <input
                type="text"
                value={careerGoal}
                onChange={(e) => setCareerGoal(e.target.value)}
                placeholder="e.g. Secure a Tier-1 AI Systems Research or Software Engineering role"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium flex items-center justify-between">
                <span>Weekly Preparation Hours</span>
                <span className="text-indigo-400 font-mono font-semibold">{weeklyHours} hrs/wk</span>
              </label>
              <input
                type="range"
                min={2}
                max={40}
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Section 4: External Portfolios & Links */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
            <Globe className="h-4 w-4 text-emerald-400" />
            <h2 className="text-sm font-semibold text-white">External Profiles & Code Evidence</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium flex items-center gap-1.5">
                <Github className="h-3.5 w-3.5 text-slate-400" /> GitHub URL
              </label>
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/username"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium flex items-center gap-1.5">
                <Linkedin className="h-3.5 w-3.5 text-slate-400" /> LinkedIn URL
              </label>
              <input
                type="url"
                value={linkedinUrl}
                onChange={(e) => setLinkedinUrl(e.target.value)}
                placeholder="https://linkedin.com/in/username"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium flex items-center gap-1.5">
                <Globe className="h-3.5 w-3.5 text-slate-400" /> Portfolio Website
              </label>
              <input
                type="url"
                value={portfolioUrl}
                onChange={(e) => setPortfolioUrl(e.target.value)}
                placeholder="https://yourportfolio.dev"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? "Saving Profile..." : "Save Profile Changes"}</span>
          </button>
        </div>
      </form>

      {/* Section 5: Skills & Verifiable Evidence Manager */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <BrainCircuit className="h-4 w-4 text-indigo-400" />
            <div>
              <h2 className="text-sm font-semibold text-white">Skills & Evidence Knowledge Graph</h2>
              <p className="text-[11px] text-slate-400">
                Skills declared here feed your Career Digital Twin proficiency model
              </p>
            </div>
          </div>
          <span className="text-xs font-mono text-indigo-300 bg-indigo-950/40 px-2.5 py-1 rounded-md border border-indigo-500/30">
            {userSkills.length} Skills Registered
          </span>
        </div>

        {/* Add Skill Form */}
        <form
          onSubmit={handleAddSkill}
          className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 grid grid-cols-1 sm:grid-cols-4 gap-3 items-end"
        >
          <div className="space-y-1 sm:col-span-2">
            <label className="text-[11px] text-slate-300 font-medium">Skill Name</label>
            <input
              type="text"
              required
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              placeholder="e.g. PyTorch, FastAPI, React, SQL..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] text-slate-300 font-medium flex justify-between">
              <span>Proficiency</span>
              <span className="text-indigo-400 font-mono">{Math.round(newSkillProficiency * 100)}%</span>
            </label>
            <input
              type="range"
              min={0.1}
              max={1.0}
              step={0.05}
              value={newSkillProficiency}
              onChange={(e) => setNewSkillProficiency(Number(e.target.value))}
              className="w-full accent-indigo-500 mt-1"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all flex items-center justify-center gap-1.5"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Add Skill</span>
          </button>
        </form>

        {/* Registered Skills List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {userSkills.map((us) => (
            <div
              key={us.id}
              className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800 flex items-center justify-between gap-3 group hover:border-slate-700 transition-all"
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-200 truncate">
                    {us.skill?.name || "Skill"}
                  </span>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {us.skill?.category?.replace("_", " ")}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-400">
                  <span>Proficiency: {Math.round(us.proficiency * 100)}%</span>
                  <span>•</span>
                  <span className="text-emerald-400">{us.source}</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{ width: `${Math.round(us.proficiency * 100)}%` }}
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleDeleteSkill(us.skill_id)}
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/20 transition-colors"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          {userSkills.length === 0 && (
            <div className="sm:col-span-2 text-center py-6 text-xs text-slate-500">
              No skills registered yet. Add canonical skills above to start building your Career Twin.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
