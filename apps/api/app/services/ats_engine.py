import re
from typing import Dict, List, Tuple
from app.schemas.resume import ATSScorecard, ParsedResumeData

ACTION_VERBS = {
    "architected", "developed", "engineered", "implemented", "deployed",
    "optimized", "trained", "fine-tuned", "designed", "benchmarked",
    "automated", "scaled", "built", "accelerated", "integrated",
    "configured", "orchestrated", "spearheaded", "authored", "solved",
    "created", "transformed", "established", "reduced", "increased"
}

WEAK_PHRASES = [
    "worked on", "helped with", "responsible for", "participated in",
    "assisted in", "handled", "duties included"
]

METRIC_PATTERNS = [
    r"\b\d+(\.\d+)?%\b",  # percentages: 95%, 4.5%
    r"\b\d+\+?\s*(users|clients|requests|ms|seconds|fps|models|parameters|queries|qps|stars|repos)\b",
    r"\b(reduced|increased|improved|boosted|optimized|scaled|accelerated)\b[^\.\n]*\b\d+",
    r"\b\d+x\b",  # 2x, 10x speedup
    r"\b\$?\d+[kKmMbB]?\b",
]


class ATSEngine:
    """Deterministic ATS Scorecard and Feedback Generator."""

    @staticmethod
    def evaluate_resume(
        parsed_data: ParsedResumeData,
        raw_text: str,
        canonical_skills: List[str],
    ) -> ATSScorecard:
        sub_scores: Dict[str, float] = {}
        strengths: List[str] = []
        improvements: List[str] = []
        missing_sections: List[str] = []

        # 1. Section Completeness (25%)
        completeness_pts = 0.0
        # Contact
        if parsed_data.contact_info.email and (parsed_data.contact_info.phone or parsed_data.contact_info.github_url):
            completeness_pts += 25.0
        else:
            missing_sections.append("Complete Contact Info (Email, Phone, GitHub/LinkedIn)")
            improvements.append("Add professional links (GitHub, LinkedIn) to your header.")

        # Education
        if len(parsed_data.education) > 0:
            completeness_pts += 25.0
            if any(e.cgpa for e in parsed_data.education):
                strengths.append("Academic credentials and CGPA clearly presented.")
        else:
            missing_sections.append("Education Section")
            improvements.append("Include your degree, institution, graduation year, and CGPA.")

        # Skills
        if len(parsed_data.skills) >= 5 or len(canonical_skills) >= 5:
            completeness_pts += 25.0
            strengths.append(f"Strong technical skill variety ({len(canonical_skills)} canonical skills recognized).")
        else:
            completeness_pts += 10.0
            improvements.append("Expand technical skills section with programming languages, frameworks, and databases.")

        # Experience or Projects
        if len(parsed_data.projects) > 0 or len(parsed_data.experience) > 0:
            completeness_pts += 25.0
            strengths.append("Project and engineering experience documented with specific deliverables.")
        else:
            missing_sections.append("Projects or Work Experience")
            improvements.append("Add at least 2-3 technical engineering projects with architecture details.")

        sub_scores["section_completeness"] = round(completeness_pts, 1)

        # 2. Quantification Coverage (25%)
        all_bullets: List[str] = []
        for exp in parsed_data.experience:
            all_bullets.extend(exp.bullet_points)
        for proj in parsed_data.projects:
            all_bullets.extend(proj.bullet_points)

        quantified_bullets = 0
        for b in all_bullets:
            if any(re.search(pat, b, re.IGNORECASE) for pat in METRIC_PATTERNS):
                quantified_bullets += 1

        total_bullets = max(len(all_bullets), 1)
        quant_ratio = quantified_bullets / total_bullets
        quant_score = min(100.0, round(quant_ratio * 125, 1))  # 80%+ ratio gives full 100
        sub_scores["quantification_coverage"] = quant_score

        if quant_ratio >= 0.4:
            strengths.append(f"Good quantification coverage ({quantified_bullets}/{len(all_bullets)} bullets contain measurable impact).")
        else:
            improvements.append("Quantify your project outcomes (e.g. 'reduced latency by 35%', 'achieved 92% test accuracy', 'serving 1,000+ requests/sec').")

        # 3. Technical Skill Density & Alignment (30%)
        word_count = len(raw_text.split())
        skill_density_ratio = len(canonical_skills) / max(word_count, 1) * 100
        # Optimal skill density is 3% - 8% of total word count
        if len(canonical_skills) >= 12:
            skill_score = 100.0
        elif len(canonical_skills) >= 8:
            skill_score = 85.0
        elif len(canonical_skills) >= 4:
            skill_score = 65.0
        else:
            skill_score = 40.0
        sub_scores["skill_density"] = skill_score

        # 4. Action Verb & Bullet Quality (20%)
        action_verb_count = 0
        weak_count = 0
        for b in all_bullets:
            words = re.findall(r"\b[a-zA-Z-]+\b", b.lower())
            if words and words[0] in ACTION_VERBS:
                action_verb_count += 1
            if any(w in b.lower() for w in WEAK_PHRASES):
                weak_count += 1

        verb_ratio = action_verb_count / total_bullets if all_bullets else 0.5
        quality_score = max(0.0, min(100.0, round((verb_ratio * 80) + (20 if weak_count == 0 else 0), 1)))
        sub_scores["bullet_quality"] = quality_score

        if weak_count > 0:
            improvements.append("Replace passive phrases ('worked on', 'responsible for') with impactful action verbs ('Architected', 'Engineered', 'Optimized').")

        # Calculate weighted overall score
        overall = round(
            (sub_scores["section_completeness"] * 0.25) +
            (sub_scores["quantification_coverage"] * 0.25) +
            (sub_scores["skill_density"] * 0.30) +
            (sub_scores["bullet_quality"] * 0.20),
            1,
        )

        return ATSScorecard(
            overall_score=overall,
            sub_scores=sub_scores,
            strengths=strengths,
            actionable_improvements=improvements,
            missing_sections=missing_sections,
            quantification_ratio=round(quant_ratio, 2),
            canonical_skills_matched_count=len(canonical_skills),
        )
