"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BrainCircuit,
  User,
  FileText,
  Briefcase,
  GitCompare,
  GraduationCap,
  Code2,
  Mic,
  Network,
  FolderGit2,
  Github,
  KanbanSquare,
  Bot,
  BarChart3,
  Settings,
  Sparkles,
  Activity,
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Career Digital Twin", href: "/career-twin", icon: BrainCircuit, badge: "Live" },
  { name: "My Profile", href: "/profile", icon: User },
  { name: "Resume Intel", href: "/resume", icon: FileText, badge: "AI" },
  { name: "Job Discovery", href: "/jobs", icon: Briefcase },
  { name: "Job Matching", href: "/matches", icon: Sparkles, badge: "Fit 95%" },
  { name: "Skill Gap Analysis", href: "/skills", icon: GitCompare },
  { name: "Learning Roadmap", href: "/learning", icon: GraduationCap },
  { name: "DSA Preparation", href: "/dsa", icon: Code2 },
  { name: "Mock Interviews", href: "/interview", icon: Mic },
  { name: "Knowledge Hub", href: "/knowledge", icon: Network, badge: "GraphRAG" },
  { name: "Project Lab", href: "/projects", icon: FolderGit2 },
  { name: "GitHub Auditor", href: "/github", icon: Github },
  { name: "Applications", href: "/applications", icon: KanbanSquare },
  { name: "AI Career Copilot", href: "/ai-assistant", icon: Bot, badge: "Multi-Agent" },
  { name: "Readiness Analytics", href: "/analytics", icon: BarChart3 },
  { name: "System Benchmarks", href: "/benchmarks", icon: Activity, badge: "QA" },
];


export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#090d16]/95 backdrop-blur-md flex flex-col justify-between h-screen sticky top-0 z-40">
      <div>
        {/* Logo & Brand */}
        <div className="p-5 border-b border-slate-800/60 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-cyan-400 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                Placement<span className="text-indigo-400">OS</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase block">
                Multi-Agent Platform
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation Items */}
        <div className="py-4 px-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 ease-out active:scale-[0.98] group ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm shadow-indigo-500/10 translate-x-0.5"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 hover:translate-x-0.5"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={`h-4 w-4 transition-transform duration-200 group-hover:scale-110 ${
                      isActive ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold uppercase tracking-wider transition-transform duration-200 group-hover:scale-105 ${
                      item.badge === "Live"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>

            );
          })}
        </div>
      </div>

      {/* Footer Settings & Status */}
      <div className="p-3 border-t border-slate-800/60 bg-slate-900/30">
        <Link
          href="/settings"
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition-colors"
        >
          <Settings className="h-4 w-4 text-slate-400" />
          <span>System Settings</span>
        </Link>
        <div className="mt-2 px-3 py-1.5 rounded-md bg-slate-900/80 border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] text-slate-300">Agents Active</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">v0.1.0</span>
        </div>
      </div>
    </aside>
  );
}
