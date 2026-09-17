"use client";

import React from "react";
import { AuthProvider } from "@/context/AuthContext";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="relative flex min-h-screen bg-[#090d16] text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
        {/* Subtle Atmospheric Ambient Glows */}
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-[120px]" />
          <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-cyan-600/8 blur-[130px]" />
          <div className="absolute -bottom-40 right-1/3 h-96 w-96 rounded-full bg-purple-600/8 blur-[140px]" />
        </div>

        {/* Persistent Layout */}
        <Sidebar />
        <div className="relative z-10 flex-1 flex flex-col min-w-0">
          <Header />
          <main className="flex-1 p-6 md:p-8 overflow-y-auto page-enter">
            {children}
          </main>
        </div>
      </div>
    </AuthProvider>
  );
}
