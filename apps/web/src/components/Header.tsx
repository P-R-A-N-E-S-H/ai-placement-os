"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Bell, ShieldCheck, ChevronDown, Sparkles, LogOut, User, LogIn } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export function Header() {
  const { user, profile, isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const displayName = profile?.full_name || (user ? user.email.split("@")[0] : "Alex Parker (Demo)");
  const displayRole = profile?.headline || (user ? `Role: ${user.role}` : "B.Tech CS / AI Candidate");
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-md sticky top-0 z-30 px-6 flex items-center justify-between">
      {/* Search Input */}
      <div className="flex items-center gap-3 w-72 md:w-96 transition-all duration-200">
        <div className="relative w-full">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 transition-colors group-focus-within:text-indigo-400" />
          <input
            type="text"
            placeholder="Search jobs, DSA patterns, skills, or ask copilot..."
            className="w-full bg-slate-900/90 border border-slate-800/80 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/50 transition-all duration-200"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 md:gap-4">
        {/* Target Role Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 text-xs font-medium shadow-sm shadow-indigo-500/10">
          <Sparkles className="h-3.5 w-3.5 text-indigo-400 animate-pulse" />
          <span>
            {profile?.target_roles?.[0]
              ? `Target: ${profile.target_roles[0]}`
              : "Target: AI & Software Engineer"}
          </span>
        </div>

        {/* System Health */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-950/30 border border-emerald-500/30 text-emerald-400 text-xs shadow-sm shadow-emerald-500/10">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="hidden sm:inline font-mono text-[11px]">API: Healthy</span>
        </div>

        {/* Notifications */}
        <button
          aria-label="Notifications"
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 active:scale-95 transition-all duration-150 relative cursor-pointer"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-500 animate-ping"></span>
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-500"></span>
        </button>

        {/* User Profile Menu */}
        {isAuthenticated ? (
          <div className="relative">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center gap-2.5 pl-2 border-l border-slate-800 text-left focus:outline-none active:scale-98 transition-all cursor-pointer"
            >
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center text-white font-semibold text-xs shadow-md shadow-indigo-500/25 ring-1 ring-white/10">
                {initials}
              </div>
              <div className="hidden lg:block text-left">
                <div className="text-xs font-medium text-slate-200 truncate max-w-[120px]">
                  {displayName}
                </div>
                <div className="text-[10px] text-slate-400 truncate max-w-[120px]">
                  {displayRole}
                </div>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-slate-500 hidden lg:block transition-transform duration-200" style={{ transform: menuOpen ? "rotate(180deg)" : "rotate(0deg)" }} />
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl bg-slate-900/95 backdrop-blur-xl border border-slate-800 shadow-2xl p-1.5 z-50 text-xs space-y-1 animate-in fade-in zoom-in-95 duration-150">
                <Link
                  href="/profile"
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all duration-150"
                >
                  <User className="h-3.5 w-3.5 text-indigo-400" />
                  <span>My Career Profile</span>
                </Link>
                <Link
                  href="/career-twin"
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all duration-150"
                >
                  <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Career Digital Twin</span>
                </Link>
                <button
                  onClick={async () => {
                    setMenuOpen(false);
                    await logout();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-rose-400 hover:bg-rose-950/30 transition-all duration-150 text-left cursor-pointer"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <Link
              href="/login"
              className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 active:scale-95 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-all duration-200 flex items-center gap-1.5 shadow-sm shadow-indigo-500/10"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span>Sign In</span>
            </Link>
          </div>
        )}
      </div>

    </header>
  );
}
