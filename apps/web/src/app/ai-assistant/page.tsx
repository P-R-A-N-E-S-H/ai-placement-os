"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Bot,
  Sparkles,
  Send,
  Zap,
  Activity,
  Layers,
  ArrowRight,
  CheckCircle2,
  Clock,
  Code2,
  Mic,
  Network,
  GitCompare,
  GraduationCap,
  RefreshCw,
  Sliders,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import {
  orchestratorApi,
  WorkflowSessionResponse,
  OrchestratorChatResponse,
  WorkflowStepDto,
} from "@/lib/api/orchestrator";
import { useAuth } from "@/context/AuthContext";

interface ChatMessage {
  sender: "user" | "copilot";
  text: string;
  workflowId?: string;
  telemetry?: Array<{ agent: string; action: string; status: string }>;
  suggestedActions?: Array<{ label: string; action_type: string; route: string }>;
  timestamp: string;
}

export default function AiAssistantPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: "copilot",
      text: "👋 Hello! I am your **Autonomous Multi-Agent Career Copilot**.\n\nI coordinate your Resume Intelligence, Skill Gap DAG, Learning Roadmap, DSA Sandbox, Mock Interview Simulator, and Hybrid RAG Knowledge Hub.\n\nTell me your placement goal, and I will autonomously execute a complete preparation plan.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      suggestedActions: [
        { label: "Target Google AI Engineer (60 Days)", action_type: "PROMPT", route: "" },
        { label: "Prepare for Amazon SDE II & Leadership Principles", action_type: "PROMPT", route: "" },
        { label: "Diagnose My Skill Gaps & Generate Roadmap", action_type: "PROMPT", route: "" },
      ],
    },
  ]);

  const [inputPrompt, setInputPrompt] = useState("");
  const [targetRole, setTargetRole] = useState("AI Engineer");
  const [targetCompany, setTargetCompany] = useState("Google");
  const [isLoading, setIsLoading] = useState(false);

  // Active Workflow Telemetry State
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowSessionResponse | null>(null);
  const [historicalWorkflows, setHistoricalWorkflows] = useState<WorkflowSessionResponse[]>([]);
  const [loadingWorkflow, setLoadingWorkflow] = useState(false);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      const res = await orchestratorApi.listWorkflows(token || undefined);
      if (res.data) {
        setHistoricalWorkflows(res.data);
      }
    } catch (err) {
      console.error("Failed to load workflows", err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputPrompt;
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt("");
    setIsLoading(true);

    try {
      const res = await orchestratorApi.chat(
        {
          message: query,
          target_role: targetRole || undefined,
          target_company: targetCompany || undefined,
        },
        token || undefined
      );

      if (res.data) {
        const copilotMsg: ChatMessage = {
          sender: "copilot",
          text: res.data.response_text,
          workflowId: res.data.workflow_session_id,
          telemetry: res.data.agent_invocations,
          suggestedActions: res.data.suggested_actions,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, copilotMsg]);

        if (res.data.workflow_session_id) {
          inspectWorkflow(res.data.workflow_session_id);
          loadWorkflows();
        }
      }
    } catch (err) {
      console.error("Copilot interaction failed", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "copilot",
          text: "⚠️ An error occurred while executing the multi-agent workflow. Please try again.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const inspectWorkflow = async (id: string) => {
    setLoadingWorkflow(true);
    try {
      const res = await orchestratorApi.getWorkflow(id, token || undefined);
      if (res.data) {
        setSelectedWorkflow(res.data);
      }
    } catch (err) {
      console.error("Failed to load workflow details", err);
    } finally {
      setLoadingWorkflow(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060810] text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Hero */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-950/60 via-indigo-950/40 to-slate-900/60 border border-purple-500/20 p-8 shadow-2xl backdrop-blur-xl">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold tracking-wide uppercase">
                <Bot className="h-3.5 w-3.5 text-purple-400" />
                Phase 11: LangGraph Multi-Agent Orchestrator
              </div>
              <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                AI Career Copilot & Agent Command Center
              </h1>
              <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
                Autonomous state-graph coordinator managing <span className="text-purple-300 font-medium">Skill Gaps</span>,{" "}
                <span className="text-indigo-300 font-medium">Hybrid RAG</span>,{" "}
                <span className="text-cyan-300 font-medium">Adaptive Roadmaps</span>,{" "}
                <span className="text-emerald-300 font-medium">DSA Sandboxes</span>, and{" "}
                <span className="text-amber-300 font-medium">Mock Interview Agents</span> into unified goal pipelines.
              </p>
            </div>
            {/* Status Pills */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                <span>6 Agents Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* 2-Column Command Center */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Conversational Multi-Agent Copilot */}
          <div className="lg:col-span-7 space-y-4 flex flex-col h-[740px]">
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 flex-1 flex flex-col overflow-hidden shadow-xl">
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-800/80 bg-slate-950/40 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Autonomous Copilot Stage</div>
                    <div className="text-[10px] text-slate-400">Master LangGraph Orchestrator</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 focus:outline-none"
                  >
                    <option value="AI Engineer">AI Engineer</option>
                    <option value="Backend Engineer">Backend SDE</option>
                    <option value="Full Stack Engineer">Full Stack SDE</option>
                  </select>
                  <select
                    value={targetCompany}
                    onChange={(e) => setTargetCompany(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 focus:outline-none"
                  >
                    <option value="Google">Google</option>
                    <option value="Amazon">Amazon</option>
                    <option value="Meta">Meta</option>
                    <option value="Microsoft">Microsoft</option>
                  </select>
                </div>
              </div>

              {/* Chat Message Scroll Area */}
              <div className="flex-1 p-5 overflow-y-auto space-y-4">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
                        msg.sender === "user"
                          ? "bg-indigo-600 text-white rounded-tr-none shadow-lg shadow-indigo-600/20"
                          : "bg-slate-950/80 border border-slate-800 text-slate-200 rounded-tl-none shadow-md"
                      }`}
                    >
                      <div className="whitespace-pre-line">{msg.text}</div>

                      {/* Agent Telemetry Badges */}
                      {msg.telemetry && msg.telemetry.length > 0 && (
                        <div className="pt-3 border-t border-slate-800/80 space-y-2">
                          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                            <Activity className="h-3 w-3 text-purple-400" />
                            Dispatched Sub-Agent Nodes
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.telemetry.map((t, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-300 text-[10px] font-mono flex items-center gap-1"
                              >
                                <CheckCircle2 className="h-2.5 w-2.5 text-emerald-400" />
                                {t.agent.replace("_AGENT", "")}: {t.action}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Suggested Action Buttons */}
                      {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                        <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-2">
                          {msg.suggestedActions.map((act, idx) => (
                            act.route ? (
                              <Link
                                key={idx}
                                href={act.route}
                                className="px-3 py-1.5 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-[10px] font-semibold flex items-center gap-1.5 transition-all"
                              >
                                <span>{act.label}</span>
                                <ArrowRight className="h-3 w-3" />
                              </Link>
                            ) : (
                              <button
                                key={idx}
                                onClick={() => handleSendMessage(act.label)}
                                className="px-3 py-1.5 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 text-[10px] font-semibold flex items-center gap-1.5 transition-all text-left"
                              >
                                <Sparkles className="h-3 w-3" />
                                <span>{act.label}</span>
                              </button>
                            )
                          ))}
                        </div>
                      )}

                      {/* Deep-link workflow inspection */}
                      {msg.workflowId && (
                        <div className="pt-1">
                          <button
                            onClick={() => inspectWorkflow(msg.workflowId!)}
                            className="text-[10px] text-indigo-400 hover:text-indigo-300 hover:underline flex items-center gap-1 font-mono"
                          >
                            <span>Inspect Execution Graph ({msg.workflowId.slice(0, 8)}...)</span>
                            <ChevronRight className="h-3 w-3" />
                          </button>
                        </div>
                      )}
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 px-1">{msg.timestamp}</span>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-center gap-2 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-400 max-w-sm">
                    <RefreshCw className="h-4 w-4 text-purple-400 animate-spin" />
                    <span>LangGraph Supervisor orchestrating agent plan...</span>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={inputPrompt}
                    onChange={(e) => setInputPrompt(e.target.value)}
                    placeholder="Ask Copilot or set high-level goals (e.g. Prepare for Amazon SDE II in 30 days)..."
                    className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputPrompt.trim()}
                    className="p-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition-all shadow-lg shadow-purple-600/25 disabled:opacity-50"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>

          {/* Right Column: Workflow Graph Inspector & Agent Telemetry */}
          <div className="lg:col-span-5 space-y-6">
            {/* Live Workflow Inspector */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-5 shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <Layers className="h-4 w-4 text-indigo-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    Agent Execution Telemetry
                  </h3>
                </div>
                {selectedWorkflow && (
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono">
                    {selectedWorkflow.status}
                  </span>
                )}
              </div>

              {loadingWorkflow ? (
                <div className="py-8 text-center text-xs text-slate-400">
                  <RefreshCw className="h-5 w-5 text-indigo-400 animate-spin mx-auto mb-2" />
                  Loading workflow graph...
                </div>
              ) : selectedWorkflow ? (
                <div className="space-y-4">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <div className="text-[10px] font-semibold text-slate-400 uppercase">Goal Plan</div>
                    <div className="text-xs font-bold text-white">{selectedWorkflow.goal}</div>
                  </div>

                  {/* Step Timeline */}
                  <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
                    {selectedWorkflow.steps.map((step, idx) => (
                      <div
                        key={step.id || idx}
                        className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="h-5 w-5 rounded-full bg-purple-500/20 text-purple-300 font-mono text-[10px] flex items-center justify-center font-bold">
                              #{step.step_index + 1}
                            </span>
                            <span className="text-xs font-bold text-white">{step.agent_type.replace("_AGENT", "")}</span>
                          </div>
                          <span className="text-[10px] font-mono text-cyan-400">{step.duration_ms} ms</span>
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono">Action: {step.action_name}</div>
                        {step.output_payload && Object.keys(step.output_payload).length > 0 && (
                          <div className="p-2 rounded bg-slate-900/90 text-[10px] font-mono text-slate-300 max-h-24 overflow-y-auto">
                            {JSON.stringify(step.output_payload, null, 2)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-xs text-slate-400 space-y-2 border border-dashed border-slate-800 rounded-xl">
                  <Activity className="h-6 w-6 text-slate-500 mx-auto" />
                  <p>Send a prompt in the Copilot stage to observe real-time multi-agent execution graphs.</p>
                </div>
              )}
            </div>

            {/* Quick Agent Launch Shortcuts */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-amber-400" />
                Specialized Agent Quick Links
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <Link
                  href="/learning"
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-indigo-500/40 text-xs font-medium text-slate-200 flex items-center gap-2 transition-all"
                >
                  <GraduationCap className="h-4 w-4 text-indigo-400" />
                  <span>Roadmaps</span>
                </Link>
                <Link
                  href="/dsa"
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-emerald-500/40 text-xs font-medium text-slate-200 flex items-center gap-2 transition-all"
                >
                  <Code2 className="h-4 w-4 text-emerald-400" />
                  <span>DSA Sandbox</span>
                </Link>
                <Link
                  href="/interview"
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-purple-500/40 text-xs font-medium text-slate-200 flex items-center gap-2 transition-all"
                >
                  <Mic className="h-4 w-4 text-purple-400" />
                  <span>Mock Interview</span>
                </Link>
                <Link
                  href="/knowledge"
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-cyan-500/40 text-xs font-medium text-slate-200 flex items-center gap-2 transition-all"
                >
                  <Network className="h-4 w-4 text-cyan-400" />
                  <span>Knowledge Hub</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
