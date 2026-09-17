from datetime import datetime, timezone
from typing import List

from app.models.job import EmploymentType, JobSourceType, LocationType
from app.services.job_sources.base import JobSourceProvider, RawJobData

CURATED_TECH_JOBS = [
    {
        "title": "Associate AI Engineer (Foundational Models & RAG)",
        "company": "OpenAI Partner Labs",
        "location": "Bengaluru, India",
        "location_type": LocationType.HYBRID.value,
        "employment_type": EmploymentType.FULL_TIME.value,
        "min_experience_years": 0.0,
        "max_experience_years": 2.0,
        "min_salary": 1800000.0,
        "max_salary": 2600000.0,
        "salary_currency": "INR",
        "source_url": "https://careers.openai.com/jobs/ai-eng-blr",
        "description": """We are seeking high-caliber Early Career AI Engineers to build next-generation agentic workflows and retrieval-augmented systems.
Key Responsibilities:
- Design and deploy autonomous multi-agent pipelines using LangGraph and LangChain.
- Implement vector search architectures with PostgreSQL pgvector and Redis caching.
- Optimize LLM inference latency and fine-tune models using PyTorch and HuggingFace.

Requirements & Qualifications:
- Must have: Strong foundation in Python, Data Structures & Algorithms, and PyTorch.
- Hands-on experience with Retrieval Augmented Generation (RAG), vector embeddings, and FastAPI.
- Familiarity with Docker, Linux environments, and CI/CD pipelines.
- Good understanding of System Design and relational databases (PostgreSQL).
- Preferred: Experience with LangGraph, Kubernetes, and AWS deployment.""",
        "raw_tags": ["Python", "PyTorch", "LangGraph", "LangChain", "PostgreSQL", "FastAPI", "Docker", "RAG"],
    },
    {
        "title": "Software Development Engineer I (Backend & Distributed Systems)",
        "company": "Uber Technologies",
        "location": "Hyderabad, India",
        "location_type": LocationType.HYBRID.value,
        "employment_type": EmploymentType.FULL_TIME.value,
        "min_experience_years": 0.0,
        "max_experience_years": 2.0,
        "min_salary": 2200000.0,
        "max_salary": 3200000.0,
        "salary_currency": "INR",
        "source_url": "https://uber.com/careers/sde1-hyd",
        "description": """Join Uber's Core Infrastructure team to architect high-throughput microservices powering millions of daily passenger trips.
Responsibilities:
- Build fault-tolerant distributed services handling 50,000+ QPS.
- Optimize database performance and query indexing in PostgreSQL and Redis.
- Write highly modular, clean code in Go / Python / Java.

Requirements:
- Must have: Proficiency in Java, Go, or Python with deep knowledge of Data Structures and Algorithms.
- Strong grasp of REST APIs, concurrency, and System Design fundamentals.
- Solid understanding of SQL, PostgreSQL, and cache invalidation strategies using Redis.
- Nice to have: Experience with Docker, Kubernetes, Kafka, and Linux kernel fundamentals.""",
        "raw_tags": ["Go", "Python", "Java", "PostgreSQL", "Redis", "Docker", "Kubernetes", "System Design", "DSA"],
    },
    {
        "title": "Junior Full-Stack AI Product Engineer",
        "company": "Swiggy NextGen Tech",
        "location": "Bengaluru, India",
        "location_type": LocationType.ONSITE.value,
        "employment_type": EmploymentType.FULL_TIME.value,
        "min_experience_years": 0.0,
        "max_experience_years": 1.5,
        "min_salary": 1400000.0,
        "max_salary": 2000000.0,
        "salary_currency": "INR",
        "source_url": "https://swiggy.com/careers/fullstack-ai-eng",
        "description": """Swiggy is engineering hyper-personalized consumer discovery powered by LLMs.
Responsibilities:
- Develop responsive, ultra-fast web interfaces using Next.js, React, and TypeScript.
- Integrate backend microservices with FastAPI and Node.js.
- Connect recommendation vector search embeddings into real-time frontends.

Qualifications:
- Must have: Strong proficiency in TypeScript, React, Next.js, Tailwind CSS, and Node.js.
- Good knowledge of Python, REST APIs, and PostgreSQL.
- Understanding of state management, responsive UI/UX, and component lifecycles.
- Nice to have: Experience with PyTorch, Redis, and LangChain.""",
        "raw_tags": ["TypeScript", "Next.js", "React", "Node.js", "Tailwind CSS", "FastAPI", "Python", "PostgreSQL"],
    },
    {
        "title": "Machine Learning Engineer — Campus Placement 2026",
        "company": "Microsoft Research & IDC",
        "location": "Noida / Hyderabad, India",
        "location_type": LocationType.HYBRID.value,
        "employment_type": EmploymentType.FULL_TIME.value,
        "min_experience_years": 0.0,
        "max_experience_years": 1.0,
        "min_salary": 2400000.0,
        "max_salary": 3600000.0,
        "salary_currency": "INR",
        "source_url": "https://careers.microsoft.com/jobs/mle-campus-idc",
        "description": """Microsoft India Development Center is hiring graduating students and early engineers for Copilot and Machine Learning research engineering.
Responsibilities:
- Train and evaluate transformer architectures, Natural Language Processing models, and Computer Vision pipelines.
- Build benchmark evaluation suites and quantitative performance testbeds.

Requirements:
- Must have: Python, PyTorch, Deep Learning, Natural Language Processing, and Linear Algebra.
- Solid understanding of Data Structures and Algorithms with clean C++ or Python coding.
- Experience with Git, Linux environments, and distributed training.
- Preferred: Experience with Azure, Docker, and Large Language Models.""",
        "raw_tags": ["Python", "PyTorch", "Deep Learning", "Natural Language Processing", "C++", "Large Language Models", "Git", "Linux"],
    },
    {
        "title": "Core Platform SDE Intern (6 Months)",
        "company": "Zerodha Tech",
        "location": "Bengaluru, India",
        "location_type": LocationType.ONSITE.value,
        "employment_type": EmploymentType.INTERNSHIP.value,
        "min_experience_years": 0.0,
        "max_experience_years": 0.5,
        "min_salary": 600000.0,
        "max_salary": 900000.0,
        "salary_currency": "INR",
        "source_url": "https://zerodha.tech/careers/sde-intern-platform",
        "description": """Zerodha's technology team is looking for passionate problem solvers who care about clean code, minimalism, and high-performance financial systems.
Responsibilities:
- Write fast, memory-safe backend services in Go and Python.
- Work on database query optimization in PostgreSQL.
- Contribute to open source libraries and developer tooling.

Requirements:
- Must have: Strong grasp of CS fundamentals (OS, Networks, Databases, DSA).
- Proficiency in Go or Python.
- Familiarity with PostgreSQL, Linux CLI, and Git.
- Bonus: Contributions to open-source software.""",
        "raw_tags": ["Go", "Python", "PostgreSQL", "Linux", "Git", "DSA"],
    },
    {
        "title": "Cloud Infrastructure & DevOps Engineer",
        "company": "Razorpay Payments",
        "location": "Remote, India",
        "location_type": LocationType.REMOTE.value,
        "employment_type": EmploymentType.FULL_TIME.value,
        "min_experience_years": 1.0,
        "max_experience_years": 3.0,
        "min_salary": 1600000.0,
        "max_salary": 2400000.0,
        "salary_currency": "INR",
        "source_url": "https://razorpay.com/careers/devops-cloud-eng",
        "description": """Build high-availability payments infrastructure handling billions of dollars in annual transaction volume.
Responsibilities:
- Manage Kubernetes clusters across multiple cloud availability zones.
- Build automated CI/CD deployment pipelines using GitHub Actions.
- Ensure 99.999% platform uptime with Prometheus and Grafana telemetry monitoring.

Requirements:
- Must have: Docker, Kubernetes, AWS, CI/CD, Linux, and Python or Go scripting.
- Understanding of Infrastructure as Code (Terraform) and networking security.
- Preferred: PostgreSQL database administration and Redis cluster management.""",
        "raw_tags": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Python", "PostgreSQL", "Redis"],
    },
]


class CuratedPlacementProvider(JobSourceProvider):
    """High-quality curated campus placement and early-career software/AI opportunities."""

    def __init__(self):
        super().__init__(name="curated_placement", source_type=JobSourceType.CURATED_PLACEMENT)

    async def health_check(self) -> bool:
        return True

    async def fetch_jobs(self, limit: int = 30) -> List[RawJobData]:
        raw_list: List[RawJobData] = []
        for item in CURATED_TECH_JOBS[:limit]:
            raw_list.append(
                RawJobData(
                    source_name=self.name,
                    source_job_id=item["source_url"].split("/")[-1],
                    source_url=item["source_url"],
                    title=item["title"],
                    company=item["company"],
                    location=item["location"],
                    location_type=item["location_type"],
                    employment_type=item["employment_type"],
                    min_experience_years=item["min_experience_years"],
                    max_experience_years=item["max_experience_years"],
                    min_salary=item["min_salary"],
                    max_salary=item["max_salary"],
                    salary_currency=item["salary_currency"],
                    description=item["description"],
                    raw_tags=item["raw_tags"],
                    posted_at=datetime.now(timezone.utc),
                )
            )
        return raw_list
