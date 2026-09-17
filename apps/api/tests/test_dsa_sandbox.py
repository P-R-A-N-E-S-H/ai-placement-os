import pytest
from app.models.dsa import SubmissionStatus
from app.services.dsa_sandbox_service import DsaSandboxService


def test_sandbox_two_sum_correct_python_solution():
    """Verify execution of optimal Two Sum solution in Python sandbox."""
    code = """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for idx, num in enumerate(nums):
            comp = target - num
            if comp in seen:
                return [seen[comp], idx]
            seen[num] = idx
        return []
"""
    test_cases = [
        {"input_data": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]"},
        {"input_data": "[[3, 2, 4], 6]", "expected_output": "[1, 2]"},
        {"input_data": "[[3, 3], 6]", "expected_output": "[0, 1]"},
    ]

    res = DsaSandboxService.execute_python_test_cases(code=code, test_cases=test_cases)
    assert res.status == SubmissionStatus.ACCEPTED.value
    assert res.passed_count == 3
    assert res.total_count == 3
    assert all(r.passed for r in res.results)
    assert res.runtime_ms >= 0


def test_sandbox_wrong_answer_detection():
    """Verify that incorrect solution is flagged as WRONG_ANSWER with diff."""
    code = """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        return [0, 0]
"""
    test_cases = [
        {"input_data": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]"},
    ]

    res = DsaSandboxService.execute_python_test_cases(code=code, test_cases=test_cases)
    assert res.status == SubmissionStatus.WRONG_ANSWER.value
    assert res.passed_count == 0
    assert res.results[0].passed is False
    assert res.results[0].actual_output == "[0, 0]"


def test_sandbox_syntax_error_handling():
    """Verify syntax error is caught during AST analysis without crashing."""
    code = """class Solution:
    def twoSum(self, nums, target)
        return []
"""
    test_cases = [{"input_data": "[[1, 2], 3]", "expected_output": "[0, 1]"}]
    res = DsaSandboxService.execute_python_test_cases(code=code, test_cases=test_cases)
    assert res.status == SubmissionStatus.SYNTAX_ERROR.value
    assert res.compile_error is not None
    assert "SyntaxError" in res.compile_error


def test_sandbox_ast_complexity_analyzer():
    """Verify static Big-O complexity analyzer detects O(N) hashmap and nested loops."""
    # O(N) hashmap code
    hash_code = """class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
"""
    comp1 = DsaSandboxService.analyze_python_ast_complexity(hash_code)
    assert comp1["time_complexity"] == "O(N)"
    assert comp1["space_complexity"] == "O(N)"

    # O(N^2) nested loop code
    nested_code = """class Solution:
    def bubbleSort(self, nums: list[int]):
        for i in range(len(nums)):
            for j in range(len(nums)):
                pass
"""
    comp2 = DsaSandboxService.analyze_python_ast_complexity(nested_code)
    assert comp2["time_complexity"] == "O(N^2)"
