"use client";

import React, { useEffect, useState } from "react";
import {
  BookOpen,
  Search,
  Sparkles,
  Network,
  Layers,
  Database,
  ExternalLink,
  PlusCircle,
  CheckCircle2,
  Cpu,
  Share2,
  Building2,
  ArrowRight,
  HelpCircle,
  FileCode,
  Tag,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";
import {
  ragApi,
  DocumentResponse,
  RagSearchResultChunk,
  RagQueryResponse,
  GraphVisualizationResponse,
} from "@/lib/api/rag";
import { useAuth } from "@/context/AuthContext";

export default function KnowledgePage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<"assistant" | "search" | "graph" | "corpus" | "ingest">("assistant");

  // State: Documents Corpus
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);
  const [corpusCompanyFilter, setCorpusCompanyFilter] = useState<string>("ALL");
  const [corpusLoading, setCorpusLoading] = useState(false);

  // State: Hybrid Search
  const [searchQuery, setSearchQuery] = useState("Google L5 distributed systems consensus and dynamic programming");
  const [searchCompany, setSearchCompany] = useState<string>("");
  const [searchResults, setSearchResults] = useState<RagSearchResultChunk[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // State: GraphRAG Grounded Assistant
  const [assistantQuery, setAssistantQuery] = useState("How should I prepare for Amazon Leadership Principles and System Design?");
  const [assistantCompany, setAssistantCompany] = useState<string>("Amazon");
  const [assistantResponse, setAssistantResponse] = useState<RagQueryResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(false);

  // State: Knowledge Graph
  const [graphData, setGraphData] = useState<GraphVisualizationResponse | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);

  // State: Ingest Form
  const [ingestTitle, setIngestTitle] = useState("");
  const [ingestCompany, setIngestCompany] = useState("");
  const [ingestRole, setIngestRole] = useState("");
  const [ingestDifficulty, setIngestDifficulty] = useState("HARD");
  const [ingestSourceType, setIngestSourceType] = useState("COMPANY_ARCHIVE");
  const [ingestTags, setIngestTags] = useState("system-design, distributed-cache, scalability");
  const [ingestRawText, setIngestRawText] = useState("");
  const [ingestSuccess, setIngestSuccess] = useState(false);
  const [ingestLoading, setIngestLoading] = useState(false);

  // Initial fetch
  useEffect(() => {
    loadDocuments();
    loadGraph();
  }, []);

  const loadDocuments = async () => {
    setCorpusLoading(true);
    try {
      const res = await ragApi.listDocuments();
      if (res.data) {
        setDocuments(res.data);
        if (res.data.length > 0 && !selectedDoc) {
          setSelectedDoc(res.data[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setCorpusLoading(false);
    }
  };

  const loadGraph = async () => {
    setGraphLoading(true);
    try {
      const res = await ragApi.getKnowledgeGraph();
      if (res.data) {
        setGraphData(res.data);
      }
    } catch (err) {
      console.error("Failed to load graph", err);
    } finally {
      setGraphLoading(false);
    }
  };

  const handleRunSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const res = await ragApi.search({
        query: searchQuery,
        company: searchCompany || undefined,
        limit: 5,
        use_hybrid: true,
        use_reranking: true,
      });
      if (res.data) {
        setSearchResults(res.data.results);
      }
    } catch (err) {
      console.error("Search failed", err);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleRunAssistantQuery = async () => {
    if (!assistantQuery.trim()) return;
    setAssistantLoading(true);
    try {
      const res = await ragApi.queryGroundedAnswer({
        query: assistantQuery,
        company: assistantCompany || undefined,
        top_k: 4,
        include_graph_context: true,
      });
      if (res.data) {
        setAssistantResponse(res.data);
      }
    } catch (err) {
      console.error("Assistant query failed", err);
    } finally {
      setAssistantLoading(false);
    }
  };

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestTitle || !ingestRawText) return;
    setIngestLoading(true);
    setIngestSuccess(false);
    try {
      const tagsArray = ingestTags.split(",").map((t) => t.trim()).filter(Boolean);
      const res = await ragApi.ingestDocument(
        {
          title: ingestTitle,
          company: ingestCompany || undefined,
          role: ingestRole || undefined,
          difficulty: ingestDifficulty,
          source_type: ingestSourceType,
          tags: tagsArray,
          raw_text: ingestRawText,
        },
        token || undefined
      );
      if (res.data) {
        setIngestSuccess(true);
        setIngestTitle("");
        setIngestRawText("");
        loadDocuments();
      }
    } catch (err) {
      console.error("Document ingestion failed", err);
    } finally {
      setIngestLoading(false);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    if (corpusCompanyFilter === "ALL") return true;
    return doc.company?.toLowerCase() === corpusCompanyFilter.toLowerCase();
  });

  return (
    <div className="min-h-screen bg-[#060810] text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Header */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-950/60 via-indigo-950/40 to-slate-900/60 border border-blue-500/20 p-8 shadow-2xl backdrop-blur-xl">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold tracking-wide uppercase">
                <Network className="h-3.5 w-3.5" />
                Phase 10: Hybrid RAG & Knowledge Graph
              </div>
              <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                Placement Knowledge Hub & GraphRAG
              </h1>
              <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
                Multi-stage hybrid retrieval engine uniting <span className="text-indigo-300 font-medium">128-d dense semantic vectors</span>,{" "}
                <span className="text-cyan-300 font-medium">Okapi BM25 sparse keyword indices</span>,{" "}
                <span className="text-amber-300 font-medium">Reciprocal Rank Fusion (RRF)</span>, and a cross-encoder graph ontology of Tier-1 company archives.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => {
                  loadDocuments();
                  loadGraph();
                }}
                className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Sync Corpus
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800/80 pb-4">
          <button
            onClick={() => setActiveTab("assistant")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "assistant"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            GraphRAG Assistant
          </button>
          <button
            onClick={() => setActiveTab("search")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "search"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <Search className="h-4 w-4" />
            Hybrid Retrieval Inspector
          </button>
          <button
            onClick={() => setActiveTab("graph")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "graph"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <Network className="h-4 w-4" />
            Knowledge Graph Explorer
          </button>
          <button
            onClick={() => setActiveTab("corpus")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "corpus"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <BookOpen className="h-4 w-4" />
            Placement Corpus ({documents.length})
          </button>
          <button
            onClick={() => setActiveTab("ingest")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "ingest"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
            }`}
          >
            <PlusCircle className="h-4 w-4" />
            Ingest Document
          </button>
        </div>

        {/* TAB 1: GraphRAG Grounded Assistant */}
        {activeTab === "assistant" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-6">
              <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-5">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-indigo-400" />
                  Grounded Q&A Query
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-slate-400 font-medium block mb-1.5">Target Company Filter</label>
                    <select
                      value={assistantCompany}
                      onChange={(e) => setAssistantCompany(e.target.value)}
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      <option value="">All Tech Giants / Syllabus</option>
                      <option value="Google">Google</option>
                      <option value="Amazon">Amazon</option>
                      <option value="Meta">Meta</option>
                      <option value="Microsoft">Microsoft</option>
                      <option value="Academic Standard">Academic CS Standard</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 font-medium block mb-1.5">Your Technical / Behavioral Question</label>
                    <textarea
                      rows={4}
                      value={assistantQuery}
                      onChange={(e) => setAssistantQuery(e.target.value)}
                      placeholder="e.g. How does Google evaluate System Design in L5 rounds?"
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed resize-none"
                    />
                  </div>
                  <button
                    onClick={handleRunAssistantQuery}
                    disabled={assistantLoading || !assistantQuery.trim()}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {assistantLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Synthesizing Grounded Answer...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        Run GraphRAG Synthesis
                      </>
                    )}
                  </button>
                </div>

                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Example Queries</div>
                  <div className="space-y-1.5">
                    {[
                      "What are the most common Meta coding patterns and time limits?",
                      "How are Amazon Leadership Principles scored in engineering rounds?",
                      "Explain Operating Systems virtual memory and page replacement.",
                      "What are Google L4/L5 Transformer and KV-cache interview questions?",
                    ].map((sample, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          setAssistantQuery(sample);
                        }}
                        className="text-left text-[11px] text-indigo-400 hover:text-indigo-300 hover:underline block truncate w-full"
                      >
                        • {sample}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Answer Display */}
            <div className="lg:col-span-2 space-y-6">
              {assistantResponse ? (
                <div className="space-y-6">
                  {/* Synthesis Card */}
                  <div className="rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-indigo-500/30 p-6 lg:p-8 space-y-6 shadow-xl">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          <Cpu className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-sm font-bold text-white">Grounded GraphRAG Response</div>
                          <div className="text-[10px] text-slate-400">Verified against official placement corpus</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[10px] font-semibold">
                          {assistantResponse.citations.length} Citations Attached
                        </span>
                      </div>
                    </div>

                    <div className="prose prose-invert max-w-none text-xs leading-relaxed text-slate-200 whitespace-pre-line">
                      {assistantResponse.answer}
                    </div>

                    {/* Connected Knowledge Graph Badges */}
                    {assistantResponse.related_graph_entities.length > 0 && (
                      <div className="pt-4 border-t border-slate-800/80 space-y-3">
                        <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                          <Network className="h-3.5 w-3.5 text-cyan-400" />
                          Multi-Hop Graph Context
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {assistantResponse.related_graph_entities.map((ent, idx) => (
                            <div
                              key={idx}
                              className="px-3 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-[11px] flex items-center justify-between"
                            >
                              <span className="text-indigo-300 font-semibold">{ent.name}</span>
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-mono">
                                {ent.relation.replace("_", " ")}
                              </span>
                              <span className="text-slate-200 font-medium">{ent.target}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Explicit Citations Cards */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                      <ShieldCheck className="h-4 w-4 text-emerald-400" />
                      Verified Source Citations
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {assistantResponse.citations.map((c, i) => (
                        <div
                          key={i}
                          className="rounded-xl bg-slate-900/60 border border-slate-800 p-4 space-y-2 hover:border-slate-700 transition-all"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-white truncate max-w-[200px]">{c.document_title}</span>
                            <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 text-[9px] font-mono">
                              {c.company || c.source_type}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-3">"{c.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-800 p-12 text-center space-y-4 bg-slate-900/20">
                  <div className="mx-auto w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <Sparkles className="h-6 w-6" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-white">Ask Anything from Placement Archives</h3>
                    <p className="text-xs text-slate-400 max-w-sm mx-auto">
                      Submit a question on the left to trigger the multi-stage hybrid vector retriever and graph synthesizer.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: Hybrid Retrieval Inspector */}
        {activeTab === "search" && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Multi-Stage Hybrid Search (Dense Cosine + Sparse BM25 + RRF)
              </h3>
              <div className="flex flex-col md:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search keywords, system architecture, leadership principles..."
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <input
                  type="text"
                  value={searchCompany}
                  onChange={(e) => setSearchCompany(e.target.value)}
                  placeholder="Filter Company (e.g. Google)"
                  className="w-full md:w-48 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={handleRunSearch}
                  disabled={searchLoading || !searchQuery.trim()}
                  className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {searchLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  Execute Search
                </button>
              </div>
            </div>

            {/* Results Grid */}
            <div className="space-y-4">
              {searchResults.length > 0 ? (
                searchResults.map((res, i) => (
                  <div
                    key={res.chunk_id}
                    className="rounded-2xl bg-slate-900/70 border border-slate-800/80 p-5 space-y-4 hover:border-indigo-500/40 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/60 pb-3">
                      <div className="flex items-center gap-3">
                        <span className="h-6 w-6 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-xs flex items-center justify-center font-bold">
                          #{i + 1}
                        </span>
                        <div>
                          <div className="text-sm font-bold text-white">{res.document_title}</div>
                          <div className="text-[10px] text-slate-400">
                            {res.company || "General Curriculum"} • {res.source_type}
                          </div>
                        </div>
                      </div>
                      {/* Detailed Scoring Telemetry */}
                      <div className="flex items-center gap-2">
                        <div className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-cyan-400">
                          Dense: {res.dense_score}
                        </div>
                        <div className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-amber-400">
                          BM25: {res.sparse_score}
                        </div>
                        <div className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-emerald-400">
                          RRF: {res.rrf_score}
                        </div>
                        <div className="px-2.5 py-1 rounded bg-indigo-500/20 border border-indigo-500/30 text-[10px] font-bold text-indigo-300">
                          Score: {res.final_score}
                        </div>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-sans">{res.chunk_text}</p>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-800 p-8 text-center text-xs text-slate-400">
                  Execute a search query to inspect dense embeddings, sparse Okapi BM25 scores, and rank fusion.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: Knowledge Graph Explorer */}
        {activeTab === "graph" && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Network className="h-5 w-5 text-indigo-400" />
                    Placement Knowledge Graph Topology
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Structured relational ontology linking FAANG+ companies, core CS topics, and interview question patterns.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-xs font-mono">
                    {graphData?.total_nodes || 0} Nodes
                  </span>
                  <span className="px-3 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-mono">
                    {graphData?.total_edges || 0} Edges
                  </span>
                </div>
              </div>
            </div>

            {/* Visual Nodes & Edges Display */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {graphData?.nodes.map((node) => {
                const connectedEdges = graphData.edges.filter(
                  (e) => e.source_node_id === node.id || e.target_node_id === node.id
                );
                return (
                  <div
                    key={node.id}
                    className="rounded-2xl bg-slate-900/70 border border-slate-800 p-5 space-y-3 hover:border-indigo-500/50 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-white">{node.name}</span>
                      <span
                        className={`text-[9px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                          node.node_type === "COMPANY"
                            ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                            : node.node_type === "TOPIC"
                            ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                            : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        }`}
                      >
                        {node.node_type}
                      </span>
                    </div>
                    {node.description && <p className="text-[11px] text-slate-400 leading-relaxed">{node.description}</p>}
                    <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                      <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Connected Relations</div>
                      <div className="space-y-1 max-h-28 overflow-y-auto">
                        {connectedEdges.map((e) => (
                          <div key={e.id} className="text-[10px] flex items-center gap-1.5 text-slate-300">
                            <ArrowRight className="h-3 w-3 text-indigo-400 shrink-0" />
                            <span className="text-indigo-300 font-mono">{e.relation_type}</span>
                            <span className="text-slate-400">→</span>
                            <span className="font-semibold text-white truncate">
                              {e.source_name === node.name ? e.target_name : e.source_name}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 4: Placement Corpus Browser */}
        {activeTab === "corpus" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-4">
              <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Corpus Filter</h3>
                  <span className="text-xs text-indigo-400 font-mono">{filteredDocs.length} Docs</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {["ALL", "Google", "Amazon", "Meta", "Microsoft", "Academic Standard"].map((co) => (
                    <button
                      key={co}
                      onClick={() => setCorpusCompanyFilter(co)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        corpusCompanyFilter === co
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800"
                      }`}
                    >
                      {co}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
                {filteredDocs.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => setSelectedDoc(doc)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      selectedDoc?.id === doc.id
                        ? "bg-indigo-950/40 border-indigo-500/50 shadow-lg shadow-indigo-950/30"
                        : "bg-slate-900/50 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-white truncate max-w-[180px]">{doc.title}</span>
                      <span className="text-[9px] px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono uppercase">
                        {doc.difficulty || "MED"}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400 flex items-center gap-2">
                      <span>{doc.company || "Academic"}</span>
                      <span>•</span>
                      <span>{doc.chunk_count} Chunks</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Document Viewer */}
            <div className="lg:col-span-2">
              {selectedDoc ? (
                <div className="rounded-2xl bg-slate-900/70 border border-slate-800 p-6 lg:p-8 space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
                    <div>
                      <h2 className="text-lg font-bold text-white">{selectedDoc.title}</h2>
                      <div className="text-xs text-slate-400 mt-1 flex items-center gap-3">
                        <span>Company: <b className="text-slate-200">{selectedDoc.company || "Universal"}</b></span>
                        <span>Role: <b className="text-slate-200">{selectedDoc.role || "SDE"}</b></span>
                        <span>Chunks: <b className="text-slate-200">{selectedDoc.chunk_count}</b></span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedDoc.tags.map((tag, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Raw Ingested Text</div>
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 leading-relaxed whitespace-pre-line font-mono max-h-[450px] overflow-y-auto">
                      {selectedDoc.raw_text}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-800 p-12 text-center text-slate-400 text-xs">
                  Select a document from the corpus on the left.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 5: Ingest Custom Placement Guide */}
        {activeTab === "ingest" && (
          <div className="max-w-2xl mx-auto rounded-2xl bg-slate-900/70 border border-slate-800 p-6 lg:p-8 space-y-6">
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <PlusCircle className="h-5 w-5 text-indigo-400" />
                Ingest Custom Placement Archive
              </h3>
              <p className="text-xs text-slate-400">
                Documents are automatically partitioned into recursive semantic chunks with dense embeddings.
              </p>
            </div>

            {ingestSuccess && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                Document successfully ingested and indexed with semantic vector chunks!
              </div>
            )}

            <form onSubmit={handleIngestSubmit} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Document Title</label>
                <input
                  type="text"
                  required
                  value={ingestTitle}
                  onChange={(e) => setIngestTitle(e.target.value)}
                  placeholder="e.g. Uber Real-Time Geospatial Dispatch System Design"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Company</label>
                  <input
                    type="text"
                    value={ingestCompany}
                    onChange={(e) => setIngestCompany(e.target.value)}
                    placeholder="e.g. Uber"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Target Role</label>
                  <input
                    type="text"
                    value={ingestRole}
                    onChange={(e) => setIngestRole(e.target.value)}
                    placeholder="e.g. Backend SDE II"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Difficulty</label>
                  <select
                    value={ingestDifficulty}
                    onChange={(e) => setIngestDifficulty(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="EASY">Easy</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HARD">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Source Type</label>
                  <select
                    value={ingestSourceType}
                    onChange={(e) => setIngestSourceType(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="COMPANY_ARCHIVE">Company Archive</option>
                    <option value="SYLLABUS">Academic Syllabus</option>
                    <option value="INTERVIEW_TRANSCRIPT">Interview Transcript</option>
                    <option value="TECH_GUIDE">Technical Guide</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Comma-Separated Tags</label>
                <input
                  type="text"
                  value={ingestTags}
                  onChange={(e) => setIngestTags(e.target.value)}
                  placeholder="e.g. geospatial, h3-index, redis, kafka"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Raw Placement Guide / Transcript Content</label>
                <textarea
                  required
                  rows={6}
                  value={ingestRawText}
                  onChange={(e) => setIngestRawText(e.target.value)}
                  placeholder="Paste interview questions, architecture notes, or debrief takeaways..."
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={ingestLoading || !ingestTitle || !ingestRawText}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {ingestLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Chunking and Embedding...
                  </>
                ) : (
                  <>
                    <PlusCircle className="h-4 w-4" />
                    Ingest and Index Document
                  </>
                )}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
