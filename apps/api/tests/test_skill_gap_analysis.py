import pytest
from app.schemas.skill_gap import GapImportanceEnum, GapTypeEnum, PriorityTierEnum
from app.services.skill_gap_service import SkillGapService


def test_compute_gap_item_satisfied():
    user_profs = {"python": 0.85}
    item = SkillGapService.compute_gap_item(
        skill_name="Python",
        skill_slug="python",
        category="Programming",
        importance=GapImportanceEnum.CRITICAL_REQUIRED.value,
        required_proficiency=0.8,
        user_proficiencies=user_profs,
    )
    assert item.gap_type == GapTypeEnum.SATISFIED.value
    assert item.current_proficiency == 0.85
    assert item.estimated_hours == 0.0
    assert item.unlock_status == "ACQUIRED"


def test_compute_gap_item_deficit():
    user_profs = {"python": 0.8, "pytorch": 0.4}
    item = SkillGapService.compute_gap_item(
        skill_name="PyTorch",
        skill_slug="pytorch",
        category="AI / ML",
        importance=GapImportanceEnum.CRITICAL_REQUIRED.value,
        required_proficiency=0.7,
        user_proficiencies=user_profs,
    )
    assert item.gap_type == GapTypeEnum.PROFICIENCY_DEFICIT.value
    assert item.current_proficiency == 0.4
    assert item.estimated_hours > 0.0
    assert item.unlock_status == "UNLOCKED"


def test_compute_gap_item_missing_locked():
    user_profs = {}
    item = SkillGapService.compute_gap_item(
        skill_name="LangGraph",
        skill_slug="langgraph",
        category="AI / ML",
        importance=GapImportanceEnum.CRITICAL_REQUIRED.value,
        required_proficiency=0.7,
        user_proficiencies=user_profs,
    )
    assert item.gap_type == GapTypeEnum.MISSING.value
    assert item.current_proficiency == 0.0
    assert item.unlock_status == "LOCKED"
    assert len(item.missing_prerequisites) > 0


def test_roi_and_quick_win_classification():
    user_profs = {"react": 0.5}
    # Fast deficit upgrade (0.5 to 0.7) in Tailwind or Next.js
    item = SkillGapService.compute_gap_item(
        skill_name="Tailwind CSS",
        skill_slug="tailwind-css",
        category="Frontend",
        importance=GapImportanceEnum.CRITICAL_REQUIRED.value,
        required_proficiency=0.6,
        user_proficiencies=user_profs,
    )
    assert item.estimated_hours <= 15.0
    assert item.priority_tier == PriorityTierEnum.P0_QUICK_WIN.value
    assert item.roi_score > 20.0
