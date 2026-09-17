import asyncio
import os
import sys

# Add parent directory to path so script can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory, engine, Base
import app.models  # Registers all ORM models in Base.metadata
from app.models.skill import Skill, SkillAlias, SkillCategory
from app.services.skill_service import slugify


CANONICAL_SKILLS = [
    # Programming Languages
    {"name": "Python", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["python3", "py", "python-3"]},
    {"name": "C++", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["cpp", "cplusplus", "c/c++"]},
    {"name": "C", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["c-lang", "ansi-c"]},
    {"name": "Java", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["java8", "java17", "core-java"]},
    {"name": "JavaScript", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["js", "ecmascript", "es6", "vanilla-js"]},
    {"name": "TypeScript", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["ts", "typescript-lang"]},
    {"name": "Go", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["golang", "go-lang"]},
    {"name": "Rust", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["rust-lang", "rustlang"]},
    {"name": "SQL", "category": SkillCategory.PROGRAMMING_LANGUAGE.value, "aliases": ["structured-query-language", "ansi-sql"]},

    # AI / ML
    {"name": "PyTorch", "category": SkillCategory.AI_ML.value, "aliases": ["torch", "pytorch-lightning", "torchvision"]},
    {"name": "TensorFlow", "category": SkillCategory.AI_ML.value, "aliases": ["tf", "tensorflow-2", "keras"]},
    {"name": "Machine Learning", "category": SkillCategory.AI_ML.value, "aliases": ["ml", "classical-ml", "scikit-learn", "sklearn"]},
    {"name": "Deep Learning", "category": SkillCategory.AI_ML.value, "aliases": ["dl", "neural-networks", "ann", "cnn", "rnn"]},
    {"name": "Computer Vision", "category": SkillCategory.AI_ML.value, "aliases": ["cv", "opencv", "yolo", "image-processing"]},
    {"name": "Natural Language Processing", "category": SkillCategory.AI_ML.value, "aliases": ["nlp", "text-processing", "spacy", "nltk"]},
    {"name": "Large Language Models", "category": SkillCategory.AI_ML.value, "aliases": ["llm", "llms", "gpt", "transformers", "huggingface"]},
    {"name": "Retrieval Augmented Generation", "category": SkillCategory.AI_ML.value, "aliases": ["rag", "vector-search", "embeddings", "semantic-search"]},
    {"name": "LangGraph", "category": SkillCategory.AI_ML.value, "aliases": ["lang-graph", "multi-agent-orchestration"]},
    {"name": "LangChain", "category": SkillCategory.AI_ML.value, "aliases": ["lang-chain", "langsmith"]},

    # Frameworks & Web
    {"name": "FastAPI", "category": SkillCategory.FRAMEWORK.value, "aliases": ["fast-api", "starlette", "pydantic-api"]},
    {"name": "Django", "category": SkillCategory.FRAMEWORK.value, "aliases": ["django-rest-framework", "drf"]},
    {"name": "Flask", "category": SkillCategory.FRAMEWORK.value, "aliases": ["flask-api"]},
    {"name": "React", "category": SkillCategory.FRAMEWORK.value, "aliases": ["reactjs", "react.js", "react-native"]},
    {"name": "Next.js", "category": SkillCategory.FRAMEWORK.value, "aliases": ["nextjs", "next.js", "next-14"]},
    {"name": "Node.js", "category": SkillCategory.FRAMEWORK.value, "aliases": ["nodejs", "node", "express", "expressjs"]},
    {"name": "Tailwind CSS", "category": SkillCategory.WEB.value, "aliases": ["tailwind", "tailwindcss"]},
    {"name": "REST APIs", "category": SkillCategory.WEB.value, "aliases": ["restful", "rest-api", "api-design", "rest"]},
    {"name": "GraphQL", "category": SkillCategory.WEB.value, "aliases": ["gql", "apollo-graphql"]},

    # Databases
    {"name": "PostgreSQL", "category": SkillCategory.DATABASE.value, "aliases": ["postgres", "pgsql", "psql", "pgvector"]},
    {"name": "MySQL", "category": SkillCategory.DATABASE.value, "aliases": ["mariadb"]},
    {"name": "MongoDB", "category": SkillCategory.DATABASE.value, "aliases": ["mongo", "nosql"]},
    {"name": "Redis", "category": SkillCategory.DATABASE.value, "aliases": ["redis-cache", "in-memory-db"]},

    # Cloud & DevOps
    {"name": "Docker", "category": SkillCategory.DEVOPS.value, "aliases": ["containers", "docker-compose", "containerization"]},
    {"name": "Kubernetes", "category": SkillCategory.DEVOPS.value, "aliases": ["k8s", "kubectl", "helm"]},
    {"name": "CI/CD", "category": SkillCategory.DEVOPS.value, "aliases": ["github-actions", "gitlab-ci", "jenkins", "pipelines"]},
    {"name": "AWS", "category": SkillCategory.CLOUD.value, "aliases": ["amazon-web-services", "ec2", "s3", "lambda"]},
    {"name": "Git", "category": SkillCategory.DEVOPS.value, "aliases": ["github", "gitlab", "version-control"]},
    {"name": "Linux", "category": SkillCategory.DEVOPS.value, "aliases": ["unix", "bash", "shell-scripting", "ubuntu"]},

    # Algorithms & DSA
    {"name": "Arrays & Strings", "category": SkillCategory.DSA.value, "aliases": ["two-pointers", "sliding-window"]},
    {"name": "Linked Lists", "category": SkillCategory.DSA.value, "aliases": ["singly-linked-list", "doubly-linked-list"]},
    {"name": "Trees & Binary Search Trees", "category": SkillCategory.DSA.value, "aliases": ["bst", "binary-tree", "trie"]},
    {"name": "Graph Algorithms", "category": SkillCategory.DSA.value, "aliases": ["bfs", "dfs", "dijkstra", "topological-sort"]},
    {"name": "Dynamic Programming", "category": SkillCategory.DSA.value, "aliases": ["dp", "memoization", "tabulation"]},
    {"name": "System Design", "category": SkillCategory.SYSTEM_DESIGN.value, "aliases": ["hld", "lld", "microservices", "distributed-systems"]},
]


async def seed_skills():
    print("[+] Starting Canonical Skills & Taxonomy Seeding...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    existing_aliases = set()
    async with async_session_factory() as session:
        from sqlalchemy import select
        existing_res = await session.execute(select(SkillAlias.alias))
        for row in existing_res.scalars().all():
            existing_aliases.add(row)

        for item in CANONICAL_SKILLS:
            name = item["name"]
            slug = slugify(name)
            category = item["category"]
            aliases = item.get("aliases", [])

            # Check if skill exists by name or slug
            from sqlalchemy import or_
            res = await session.execute(select(Skill).where(or_(Skill.name == name, Skill.slug == slug)))
            skill = res.scalar_one_or_none()

            if not skill:
                skill = Skill(name=name, slug=slug, category=category)
                session.add(skill)
                await session.flush()
                print(f"  + Added Skill: {name} ({category})")


            # Add self alias & unique aliases
            all_aliases = [name.lower(), slug] + [a.lower() for a in aliases]
            for a in all_aliases:
                if a and a not in existing_aliases:
                    alias_obj = SkillAlias(alias=a, canonical_skill_id=skill.id)
                    session.add(alias_obj)
                    existing_aliases.add(a)

        await session.commit()
    print("[SUCCESS] Canonical Skills taxonomy successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed_skills())
