import hashlib
import math
import re
from typing import Dict, List, Optional, Set, Tuple

DOMAIN_CLUSTERS: Dict[str, Tuple[int, int, Set[str]]] = {
    "AI_ML": (
        0,
        24,
        {
            "python", "pytorch", "torch", "tensorflow", "keras", "machine", "learning",
            "deep", "neural", "vision", "nlp", "natural", "language", "processing",
            "llm", "llms", "gpt", "rag", "retrieval", "augmented", "generation",
            "langgraph", "langchain", "embeddings", "transformers", "huggingface",
            "agentic", "inference", "fine-tuning", "vector", "ai", "model", "models"
        },
    ),
    "BACKEND_DISTRIBUTED": (
        24,
        48,
        {
            "fastapi", "django", "flask", "node", "nodejs", "express", "go", "golang",
            "java", "rust", "backend", "api", "apis", "rest", "restful", "graphql",
            "microservices", "distributed", "systems", "concurrency", "qps", "rps",
            "redis", "postgresql", "postgres", "mysql", "mongodb", "sql", "database",
            "caching", "throughput", "latency"
        },
    ),
    "FRONTEND_WEB": (
        48,
        72,
        {
            "react", "reactjs", "next", "nextjs", "javascript", "js", "typescript",
            "ts", "tailwind", "css", "html", "frontend", "ui", "ux", "responsive",
            "components", "redux", "state", "client", "web", "browser", "dom"
        },
    ),
    "DEVOPS_CLOUD": (
        72,
        96,
        {
            "docker", "containers", "kubernetes", "k8s", "aws", "amazon", "cloud",
            "azure", "gcp", "devops", "ci", "cd", "pipelines", "actions", "linux",
            "unix", "bash", "shell", "terraform", "prometheus", "grafana", "git",
            "github", "infrastructure", "deployment"
        },
    ),
    "DSA_ALGORITHMS": (
        96,
        112,
        {
            "algorithms", "dsa", "structures", "data", "arrays", "strings", "trees",
            "bst", "graphs", "bfs", "dfs", "dynamic", "programming", "dp",
            "memoization", "complexity", "pointers", "sliding", "window", "sorting"
        },
    ),
}


class JobEmbeddingService:
    """Generates true domain-semantic dense vector embeddings and computes cosine similarity."""

    EMBEDDING_DIM = 128

    @classmethod
    def _project_tokens(cls, tokens: List[str]) -> List[float]:
        vector = [0.0] * cls.EMBEDDING_DIM
        if not tokens:
            return vector

        token_freq: Dict[str, int] = {}
        for t in tokens:
            token_freq[t] = token_freq.get(t, 0) + 1

        for token, count in token_freq.items():
            token_lower = token.lower()
            term_weight = math.log1p(count)

            # 1. Check Domain Clusters for subspace activation
            domain_matched = False
            for domain_name, (start_idx, end_idx, vocab_set) in DOMAIN_CLUSTERS.items():
                if token_lower in vocab_set:
                    domain_matched = True
                    subspace_len = end_idx - start_idx
                    h = int(hashlib.md5(token_lower.encode("utf-8")).hexdigest(), 16)
                    target_idx = start_idx + (h % subspace_len)
                    vector[target_idx] += 2.5 * term_weight
                    # Also boost neighboring coordinates in the cluster for smooth semantic continuity
                    vector[start_idx + ((h + 1) % subspace_len)] += 1.0 * term_weight

            # 2. General subspace projection (dims 112..127) for subwords / n-grams
            h_gen = int(hashlib.sha256(token_lower.encode("utf-8")).hexdigest(), 16)
            gen_idx = 112 + (h_gen % 16)
            sign = 1.0 if ((h_gen >> 5) % 2 == 0) else -1.0
            vector[gen_idx] += (1.0 if domain_matched else 1.8) * sign * term_weight

        # L2-normalize to unit length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0.0:
            vector = [round(x / norm, 6) for x in vector]

        return vector

    @classmethod
    def generate_job_embedding(
        cls,
        title: str,
        company: str,
        location: str,
        skills: List[str],
        description: str,
    ) -> List[float]:
        """Generate a dense normalized vector for a job posting."""
        text = f"{title} {company} {location} {' '.join(skills)} {description[:800]}".lower()
        tokens = re.findall(r"\w+", text)
        return cls._project_tokens(tokens)

    @classmethod
    def generate_candidate_embedding(
        cls,
        target_role: Optional[str],
        skills: List[str],
        projects_text: str,
        bio: Optional[str] = None,
    ) -> List[float]:
        """Generate a dense normalized vector for a candidate's Career Digital Twin."""
        text = f"{target_role or ''} {bio or ''} {' '.join(skills)} {projects_text[:800]}".lower()
        tokens = re.findall(r"\w+", text)
        return cls._project_tokens(tokens)

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """
        Compute cosine similarity between two unit vectors: dot_product(v1, v2).
        Returns value in range [0.0, 1.0].
        """
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))
