from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple


# Base hours required to learn a skill from scratch (0 -> 1.0 proficiency)
CANONICAL_SKILL_BASE_HOURS: Dict[str, float] = {
    # AI / ML & Agents
    "python": 30.0,
    "numpy": 15.0,
    "pandas": 20.0,
    "scikit-learn": 25.0,
    "pytorch": 40.0,
    "tensorflow": 35.0,
    "deep-learning": 35.0,
    "transformers": 45.0,
    "huggingface": 20.0,
    "prompt-engineering": 15.0,
    "vector-embeddings-rag": 30.0,
    "rag": 30.0,
    "langchain": 25.0,
    "langgraph": 35.0,
    "multi-agent-systems": 40.0,
    "mlops": 35.0,

    # Backend & Distributed Systems
    "java": 35.0,
    "go": 30.0,
    "c++": 40.0,
    "fastapi": 20.0,
    "flask": 15.0,
    "spring-boot": 35.0,
    "node-js": 25.0,
    "sql": 20.0,
    "postgresql": 20.0,
    "mongodb": 18.0,
    "redis": 15.0,
    "kafka": 30.0,
    "microservices": 35.0,
    "system-design": 45.0,
    "rest-apis": 15.0,
    "graphql": 20.0,
    "distributed-systems": 45.0,

    # Frontend & Web
    "html-css": 15.0,
    "javascript": 25.0,
    "typescript": 20.0,
    "react": 30.0,
    "next-js": 25.0,
    "vue-js": 25.0,
    "tailwind-css": 10.0,
    "state-management": 15.0,

    # DevOps & Cloud
    "linux": 20.0,
    "bash-scripting": 15.0,
    "git": 10.0,
    "docker": 20.0,
    "kubernetes": 35.0,
    "ci-cd": 18.0,
    "github-actions": 15.0,
    "aws": 40.0,
    "gcp": 35.0,
    "terraform": 25.0,

    # DSA & Problem Solving
    "dsa": 40.0,
    "arrays-strings": 18.0,
    "linked-lists-stacks": 18.0,
    "trees-graphs": 35.0,
    "dynamic-programming": 40.0,
    "algorithms": 35.0,
}

# Canonical Directed Edges (Prerequisite -> Dependent)
CANONICAL_PREREQUISITE_EDGES: List[Tuple[str, str]] = [
    # AI / ML Chain
    ("python", "numpy"),
    ("python", "pandas"),
    ("python", "fastapi"),
    ("python", "pytorch"),
    ("python", "scikit-learn"),
    ("numpy", "pandas"),
    ("pandas", "scikit-learn"),
    ("scikit-learn", "deep-learning"),
    ("pytorch", "deep-learning"),
    ("pytorch", "transformers"),
    ("pytorch", "rag"),
    ("transformers", "huggingface"),
    ("transformers", "vector-embeddings-rag"),
    ("transformers", "rag"),
    ("prompt-engineering", "langchain"),
    ("rag", "langchain"),
    ("vector-embeddings-rag", "langchain"),
    ("langchain", "langgraph"),
    ("langchain", "multi-agent-systems"),
    ("langgraph", "multi-agent-systems"),
    ("deep-learning", "mlops"),
    ("docker", "mlops"),

    # Backend & Distributed Systems Chain
    ("dsa", "algorithms"),
    ("arrays-strings", "linked-lists-stacks"),
    ("linked-lists-stacks", "trees-graphs"),
    ("trees-graphs", "dynamic-programming"),
    ("dynamic-programming", "algorithms"),
    ("python", "fastapi"),
    ("sql", "postgresql"),
    ("sql", "mongodb"),
    ("rest-apis", "fastapi"),
    ("rest-apis", "spring-boot"),
    ("fastapi", "microservices"),
    ("postgresql", "microservices"),
    ("redis", "microservices"),
    ("microservices", "distributed-systems"),
    ("kafka", "distributed-systems"),
    ("microservices", "system-design"),
    ("distributed-systems", "system-design"),

    # Frontend Chain
    ("html-css", "javascript"),
    ("javascript", "typescript"),
    ("javascript", "react"),
    ("typescript", "react"),
    ("react", "next-js"),
    ("react", "state-management"),
    ("html-css", "tailwind-css"),

    # DevOps Chain
    ("linux", "bash-scripting"),
    ("linux", "docker"),
    ("git", "ci-cd"),
    ("git", "github-actions"),
    ("docker", "kubernetes"),
    ("docker", "ci-cd"),
    ("ci-cd", "github-actions"),
    ("docker", "aws"),
    ("docker", "gcp"),
    ("aws", "terraform"),
    ("gcp", "terraform"),
    ("kubernetes", "terraform"),
]


class SkillGraphService:
    """
    Deterministic Directed Acyclic Graph (DAG) Engine for Prerequisite Resolution,
    Topological Sequence Ordering, Unlock State Classification, and Effort Estimation.
    """

    @staticmethod
    def normalize_slug(name: str) -> str:
        """Slugify skill names to canonical identifiers."""
        slug = name.lower().strip()
        slug = slug.replace("c++", "c++").replace("c#", "csharp").replace(".net", "dotnet")
        slug = slug.replace("next.js", "next-js").replace("vue.js", "vue-js").replace("node.js", "node-js")
        slug = slug.replace("langchain", "langchain").replace("langgraph", "langgraph")
        slug = slug.replace("rag & vector dbs", "vector-embeddings-rag").replace("rag", "rag")
        slug = slug.replace(" ", "-").replace("/", "-").replace("_", "-")
        return slug

    @classmethod
    def get_prerequisites_for_skill(cls, skill_slug: str) -> List[str]:
        """Returns direct prerequisites for a given skill slug."""
        normalized = cls.normalize_slug(skill_slug)
        prereqs = [src for (src, tgt) in CANONICAL_PREREQUISITE_EDGES if cls.normalize_slug(tgt) == normalized]
        return list(set(prereqs))

    @classmethod
    def get_all_ancestor_prerequisites(cls, skill_slug: str) -> Set[str]:
        """Returns all transitive upstream prerequisites for a given skill slug."""
        ancestors: Set[str] = set()
        queue = deque([cls.normalize_slug(skill_slug)])

        while queue:
            curr = queue.popleft()
            for src, tgt in CANONICAL_PREREQUISITE_EDGES:
                norm_tgt = cls.normalize_slug(tgt)
                norm_src = cls.normalize_slug(src)
                if norm_tgt == curr and norm_src not in ancestors:
                    ancestors.add(norm_src)
                    queue.append(norm_src)

        return ancestors

    @classmethod
    def get_base_hours(cls, skill_slug: str) -> float:
        """Returns base learning hours (default 25.0 if not explicitly mapped)."""
        normalized = cls.normalize_slug(skill_slug)
        return CANONICAL_SKILL_BASE_HOURS.get(normalized, 25.0)

    @classmethod
    def topological_sort(cls, skill_slugs: List[str]) -> List[str]:
        """
        Kahn's Algorithm with cycle-protection:
        Sorts the provided skill list strictly respecting upstream prerequisite dependencies.
        """
        normalized_set = {cls.normalize_slug(s) for s in skill_slugs}
        in_degree: Dict[str, int] = {s: 0 for s in normalized_set}
        adj_list: Dict[str, List[str]] = defaultdict(list)

        # Build induced subgraph for the requested skills
        for src, tgt in CANONICAL_PREREQUISITE_EDGES:
            norm_src = cls.normalize_slug(src)
            norm_tgt = cls.normalize_slug(tgt)
            if norm_src in normalized_set and norm_tgt in normalized_set:
                adj_list[norm_src].append(norm_tgt)
                in_degree[norm_tgt] += 1

        # Queue nodes with 0 in-degree
        queue = deque([s for s, deg in in_degree.items() if deg == 0])
        ordered: List[str] = []

        while queue:
            node = queue.popleft()
            ordered.append(node)
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Append any remaining disconnected/unresolved nodes if cycles exist
        for s in normalized_set:
            if s not in ordered:
                ordered.append(s)

        return ordered

    @classmethod
    def resolve_unlock_status(
        cls,
        skill_slug: str,
        current_proficiency: float,
        required_proficiency: float,
        user_proficiencies: Dict[str, float],
    ) -> Tuple[str, List[str]]:
        """
        Determines if a skill is ACQUIRED, UNLOCKED (ready to learn), or LOCKED.
        Also returns list of missing prerequisites.
        """
        norm_slug = cls.normalize_slug(skill_slug)

        if current_proficiency >= required_proficiency:
            return "ACQUIRED", []

        direct_prereqs = cls.get_prerequisites_for_skill(norm_slug)
        missing_prereqs = [
            p for p in direct_prereqs
            if user_proficiencies.get(cls.normalize_slug(p), 0.0) < 0.5
        ]

        if not missing_prereqs:
            return "UNLOCKED", []
        else:
            return "LOCKED", missing_prereqs
