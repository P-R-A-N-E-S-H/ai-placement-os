import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.dsa import (
    DsaProblem,
    DsaSubmission,
    DsaTestCase,
    ProblemCategory,
    ProblemDifficulty,
    SubmissionStatus,
    UserDsaProgress,
)
from app.models.skill import EvidenceSourceType, Skill, SkillEvidence, UserSkill
from app.schemas.dsa import (
    DsaProblemDetail,
    DsaProblemSummary,
    DsaRunRequest,
    DsaRunResponse,
    DsaStatsResponse,
    DsaSubmissionResponse,
    DsaSubmitRequest,
    DsaTestCaseResponse,
)
from app.services.dsa_sandbox_service import DsaSandboxService
from app.services.skill_service import SkillService, slugify


CANONICAL_DSA_PROBLEMS: List[Dict[str, Any]] = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": ProblemDifficulty.EASY.value,
        "category": ProblemCategory.ARRAYS_HASHING.value,
        "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.

### Example 1
```text
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

### Example 2
```text
Input: nums = [3,2,4], target = 6
Output: [1,2]
```""",
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists.",
        ],
        "hints": [
            "A brute force search takes O(N^2) time. Can you use a Hash Map to find complements in O(1) time?",
            "Store each number's index as you iterate through the array.",
        ],
        "starter_code": {
            "python": """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Write your optimal O(N) solution here
        pass
""",
            "javascript": """function twoSum(nums, target) {
    // Write your optimal O(N) solution here
}
""",
            "cpp": """#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Write your optimal O(N) solution here
    }
};
""",
            "java": """import java.util.HashMap;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your optimal O(N) solution here
        return new int[]{};
    }
}
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "acceptance_rate": 52.4,
        "order_index": 1,
        "test_cases": [
            {"input_data": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]", "is_hidden": False, "explanation": "2 + 7 = 9"},
            {"input_data": "[[3, 2, 4], 6]", "expected_output": "[1, 2]", "is_hidden": False, "explanation": "2 + 4 = 6"},
            {"input_data": "[[3, 3], 6]", "expected_output": "[0, 1]", "is_hidden": False, "explanation": "3 + 3 = 6"},
            {"input_data": "[[1, 5, 7, 11, 19], 20]", "expected_output": "[0, 4]", "is_hidden": True},
            {"input_data": "[[-1, -2, -3, -4, -5], -8]", "expected_output": "[2, 4]", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "difficulty": ProblemDifficulty.EASY.value,
        "category": ProblemCategory.ARRAYS_HASHING.value,
        "description": """Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

### Example 1
```text
Input: s = "anagram", t = "nagaram"
Output: true
```

### Example 2
```text
Input: s = "rat", t = "car"
Output: false
```""",
        "constraints": [
            "1 <= s.length, t.length <= 5 * 10^4",
            "s and t consist of lowercase English letters.",
        ],
        "hints": [
            "Count frequencies of each character in s and compare with t.",
            "Can you use an array of size 26 or a hash map?",
        ],
        "starter_code": {
            "python": """class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # Write your optimal O(N) solution here
        pass
""",
            "javascript": """function isAnagram(s, t) {
    // Write your optimal O(N) solution here
}
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "acceptance_rate": 64.2,
        "order_index": 2,
        "test_cases": [
            {"input_data": "[\"anagram\", \"nagaram\"]", "expected_output": "true", "is_hidden": False},
            {"input_data": "[\"rat\", \"car\"]", "expected_output": "false", "is_hidden": False},
            {"input_data": "[\"a\", \"ab\"]", "expected_output": "false", "is_hidden": True},
            {"input_data": "[\"listen\", \"silent\"]", "expected_output": "true", "is_hidden": True},
        ],
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "slug": "best-time-to-buy-and-sell-stock",
        "difficulty": ProblemDifficulty.EASY.value,
        "category": ProblemCategory.SLIDING_WINDOW.value,
        "description": """You are given an array `prices` where `prices[i]` is the price of a given stock on the `i-th` day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

### Example 1
```text
Input: prices = [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5.
```

### Example 2
```text
Input: prices = [7,6,4,3,1]
Output: 0
Explanation: In this case, no transactions are done and max profit = 0.
```""",
        "constraints": [
            "1 <= prices.length <= 10^5",
            "0 <= prices[i] <= 10^4",
        ],
        "hints": [
            "Keep track of the minimum price observed so far as you iterate through the list.",
            "Calculate profit if sold on day i: prices[i] - min_price.",
        ],
        "starter_code": {
            "python": """class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # Write your optimal O(N) solution here
        pass
""",
            "javascript": """function maxProfit(prices) {
    // Write your optimal O(N) solution here
}
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "acceptance_rate": 54.1,
        "order_index": 3,
        "test_cases": [
            {"input_data": "[[7, 1, 5, 3, 6, 4]]", "expected_output": "5", "is_hidden": False},
            {"input_data": "[[7, 6, 4, 3, 1]]", "expected_output": "0", "is_hidden": False},
            {"input_data": "[[2, 4, 1]]", "expected_output": "2", "is_hidden": True},
            {"input_data": "[[3, 2, 6, 5, 0, 3]]", "expected_output": "4", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": ProblemDifficulty.EASY.value,
        "category": ProblemCategory.STACK.value,
        "description": """Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

### Example 1
```text
Input: s = "()"
Output: true
```

### Example 2
```text
Input: s = "()[]{}"
Output: true
```

### Example 3
```text
Input: s = "(]"
Output: false
```""",
        "constraints": [
            "1 <= s.length <= 10^4",
            "s consists of parentheses only '()[]{}'.",
        ],
        "hints": [
            "Use a Last-In-First-Out (LIFO) Stack data structure.",
            "Push opening brackets onto the stack; when encountering a closing bracket, verify it matches the top element.",
        ],
        "starter_code": {
            "python": """class Solution:
    def isValid(self, s: str) -> bool:
        # Write your optimal O(N) stack solution here
        pass
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "acceptance_rate": 40.8,
        "order_index": 4,
        "test_cases": [
            {"input_data": "[\"()\"]", "expected_output": "true", "is_hidden": False},
            {"input_data": "[\"()[]{}\"]", "expected_output": "true", "is_hidden": False},
            {"input_data": "[\"(]\"]", "expected_output": "false", "is_hidden": False},
            {"input_data": "[\"([)]\"]", "expected_output": "false", "is_hidden": True},
            {"input_data": "[\"{[]}\"]", "expected_output": "true", "is_hidden": True},
        ],
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": ProblemDifficulty.EASY.value,
        "category": ProblemCategory.BINARY_SEARCH.value,
        "description": """Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return -1.

You must write an algorithm with `O(log n)` runtime complexity.

### Example 1
```text
Input: nums = [-1,0,3,5,9,12], target = 9
Output: 4
Explanation: 9 exists in nums and its index is 4
```

### Example 2
```text
Input: nums = [-1,0,3,5,9,12], target = 2
Output: -1
Explanation: 2 does not exist in nums so return -1
```""",
        "constraints": [
            "1 <= nums.length <= 10^4",
            "-10^4 < nums[i], target < 10^4",
            "All the integers in nums are unique.",
            "nums is sorted in ascending order.",
        ],
        "hints": [
            "Set left = 0 and right = len(nums) - 1.",
            "Compute mid = left + (right - left) // 2 to avoid integer overflow.",
        ],
        "starter_code": {
            "python": """class Solution:
    def search(self, nums: List[int], target: int) -> int:
        # Write your optimal O(log N) binary search here
        pass
""",
        },
        "expected_time_complexity": "O(log N)",
        "expected_space_complexity": "O(1)",
        "acceptance_rate": 57.2,
        "order_index": 5,
        "test_cases": [
            {"input_data": "[[-1, 0, 3, 5, 9, 12], 9]", "expected_output": "4", "is_hidden": False},
            {"input_data": "[[-1, 0, 3, 5, 9, 12], 2]", "expected_output": "-1", "is_hidden": False},
            {"input_data": "[[5], 5]", "expected_output": "0", "is_hidden": True},
            {"input_data": "[[2, 5], 0]", "expected_output": "-1", "is_hidden": True},
        ],
    },
    {
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "slug": "maximum-subarray",
        "difficulty": ProblemDifficulty.MEDIUM.value,
        "category": ProblemCategory.DYNAMIC_PROGRAMMING.value,
        "description": """Given an integer array `nums`, find the subarray with the largest sum, and return its sum.

### Example 1
```text
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: The subarray [4,-1,2,1] has the largest sum 6.
```

### Example 2
```text
Input: nums = [1]
Output: 1
```

### Example 3
```text
Input: nums = [5,4,-1,7,8]
Output: 23
```""",
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
        ],
        "hints": [
            "Kadane's algorithm maintains a running sum: current_sum = max(num, current_sum + num).",
            "Update max_sum at each step.",
        ],
        "starter_code": {
            "python": """class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        # Write your optimal O(N) Kadane's algorithm here
        pass
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "acceptance_rate": 50.3,
        "order_index": 6,
        "test_cases": [
            {"input_data": "[[-2, 1, -3, 4, -1, 2, 1, -5, 4]]", "expected_output": "6", "is_hidden": False},
            {"input_data": "[[1]]", "expected_output": "1", "is_hidden": False},
            {"input_data": "[[5, 4, -1, 7, 8]]", "expected_output": "23", "is_hidden": False},
            {"input_data": "[[-1, -2, -3]]", "expected_output": "-1", "is_hidden": True},
        ],
    },
    {
        "title": "Top K Frequent Elements",
        "slug": "top-k-frequent-elements",
        "difficulty": ProblemDifficulty.MEDIUM.value,
        "category": ProblemCategory.HEAP_PRIORITY_QUEUE.value,
        "description": """Given an integer array `nums` and an integer `k`, return the `k` most frequent elements. You may return the answer in any order.

### Example 1
```text
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
```

### Example 2
```text
Input: nums = [1], k = 1
Output: [1]
```""",
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
            "k is in the range [1, the number of unique elements in the array].",
            "It is guaranteed that the answer is unique.",
        ],
        "hints": [
            "You can use a Min-Heap of size k ($O(N \\log k)$) or Bucket Sort ($O(N)$).",
        ],
        "starter_code": {
            "python": """class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # Write your optimal O(N) or O(N log k) solution here
        pass
""",
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "acceptance_rate": 63.8,
        "order_index": 7,
        "test_cases": [
            {"input_data": "[[1, 1, 1, 2, 2, 3], 2]", "expected_output": "[1, 2]", "is_hidden": False},
            {"input_data": "[[1], 1]", "expected_output": "[1]", "is_hidden": False},
            {"input_data": "[[4, 1, -1, 2, -1, 2, 3], 2]", "expected_output": "[-1, 2]", "is_hidden": True},
        ],
    },
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "difficulty": ProblemDifficulty.MEDIUM.value,
        "category": ProblemCategory.DYNAMIC_PROGRAMMING.value,
        "description": """You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.

You may assume that you have an infinite number of each kind of coin.

### Example 1
```text
Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1
```

### Example 2
```text
Input: coins = [2], amount = 3
Output: -1
```

### Example 3
```text
Input: coins = [1], amount = 0
Output: 0
```""",
        "constraints": [
            "1 <= coins.length <= 12",
            "1 <= coins[i] <= 2^31 - 1",
            "0 <= amount <= 10^4",
        ],
        "hints": [
            "Bottom-up Dynamic Programming: dp[i] represents fewest coins to make amount i.",
            "Initialize dp array with infinity and dp[0] = 0.",
        ],
        "starter_code": {
            "python": """class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        # Write your optimal O(amount * len(coins)) DP solution here
        pass
""",
        },
        "expected_time_complexity": "O(amount * N)",
        "expected_space_complexity": "O(amount)",
        "acceptance_rate": 43.1,
        "order_index": 8,
        "test_cases": [
            {"input_data": "[[1, 2, 5], 11]", "expected_output": "3", "is_hidden": False},
            {"input_data": "[[2], 3]", "expected_output": "-1", "is_hidden": False},
            {"input_data": "[[1], 0]", "expected_output": "0", "is_hidden": False},
            {"input_data": "[[2, 5, 10, 1], 27]", "expected_output": "4", "is_hidden": True},
        ],
    },
]


class DsaService:
    """
    Core DSA Preparation Service.
    Manages problem catalog, handles code execution & submissions,
    updates candidate performance analytics, and synchronizes verifiable
    evidence with the Career Digital Twin.
    """

    @classmethod
    async def ensure_seeded_problems(cls, db: AsyncSession) -> None:
        """Seeds canonical placement DSA problems if not already present."""
        existing_count = (await db.execute(select(func.count(DsaProblem.id)))).scalar_one()
        if existing_count > 0:
            return

        for prob_data in CANONICAL_DSA_PROBLEMS:
            problem = DsaProblem(
                title=prob_data["title"],
                slug=prob_data["slug"],
                difficulty=prob_data["difficulty"],
                category=prob_data["category"],
                description=prob_data["description"],
                constraints=prob_data["constraints"],
                hints=prob_data["hints"],
                starter_code=prob_data["starter_code"],
                expected_time_complexity=prob_data["expected_time_complexity"],
                expected_space_complexity=prob_data["expected_space_complexity"],
                acceptance_rate=prob_data["acceptance_rate"],
                order_index=prob_data["order_index"],
                is_active=True,
            )
            db.add(problem)
            await db.flush()

            for idx, tc in enumerate(prob_data["test_cases"]):
                test_case = DsaTestCase(
                    problem_id=problem.id,
                    input_data=tc["input_data"],
                    expected_output=tc["expected_output"],
                    is_hidden=tc.get("is_hidden", False),
                    explanation=tc.get("explanation"),
                    order_index=idx + 1,
                )
                db.add(test_case)

        await db.commit()

    @classmethod
    async def list_problems(
        cls,
        db: AsyncSession,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[DsaProblemSummary], int]:
        """Lists DSA problems with search, filtering, and solved status for candidate."""
        await cls.ensure_seeded_problems(db)

        query = select(DsaProblem).where(DsaProblem.is_active.is_(True))

        if category:
            query = query.where(DsaProblem.category == category)
        if difficulty:
            query = query.where(DsaProblem.difficulty == difficulty.upper())
        if search:
            query = query.where(
                or_(
                    DsaProblem.title.ilike(f"%{search}%"),
                    DsaProblem.category.ilike(f"%{search}%"),
                    DsaProblem.slug.ilike(f"%{search}%"),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Fetch page
        query = query.order_by(DsaProblem.order_index.asc()).offset((page - 1) * page_size).limit(page_size)
        problems = (await db.execute(query)).scalars().all()

        # Fetch candidate progress if user_id present
        progress_map: Dict[str, UserDsaProgress] = {}
        if user_id:
            prog_res = await db.execute(
                select(UserDsaProgress).where(UserDsaProgress.user_id == user_id)
            )
            for p in prog_res.scalars().all():
                progress_map[p.problem_id] = p

        results = []
        for prob in problems:
            prog = progress_map.get(prob.id)
            results.append(
                DsaProblemSummary(
                    id=prob.id,
                    title=prob.title,
                    slug=prob.slug,
                    difficulty=prob.difficulty,
                    category=prob.category,
                    expected_time_complexity=prob.expected_time_complexity,
                    expected_space_complexity=prob.expected_space_complexity,
                    acceptance_rate=prob.acceptance_rate,
                    order_index=prob.order_index,
                    is_solved=prog.is_solved if prog else False,
                    attempts_count=prog.attempts_count if prog else 0,
                )
            )

        return results, total

    @classmethod
    async def get_problem_by_slug_or_id(
        cls,
        db: AsyncSession,
        identifier: str,
        user_id: Optional[str] = None,
    ) -> DsaProblemDetail:
        """Retrieves complete problem statement, visible test cases, and candidate's saved code."""
        await cls.ensure_seeded_problems(db)

        query = (
            select(DsaProblem)
            .options(selectinload(DsaProblem.test_cases))
            .where(
                or_(DsaProblem.id == identifier, DsaProblem.slug == identifier)
            )
        )
        problem = (await db.execute(query)).scalar_one_or_none()
        if not problem:
            raise EntityNotFoundError("DsaProblem", identifier)

        # Filter to visible test cases for problem detail
        visible_tcs = [
            DsaTestCaseResponse(
                id=tc.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=tc.is_hidden,
                explanation=tc.explanation,
                order_index=tc.order_index,
            )
            for tc in sorted(problem.test_cases, key=lambda x: x.order_index)
            if not tc.is_hidden
        ]

        is_solved = False
        last_code = None
        last_lang = None

        if user_id:
            prog = (
                await db.execute(
                    select(UserDsaProgress).where(
                        UserDsaProgress.user_id == user_id,
                        UserDsaProgress.problem_id == problem.id,
                    )
                )
            ).scalar_one_or_none()
            if prog:
                is_solved = prog.is_solved
                last_code = prog.last_submitted_code
                last_lang = prog.last_language

        return DsaProblemDetail(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            difficulty=problem.difficulty,
            category=problem.category,
            description=problem.description,
            constraints=problem.constraints,
            hints=problem.hints,
            starter_code=problem.starter_code,
            expected_time_complexity=problem.expected_time_complexity,
            expected_space_complexity=problem.expected_space_complexity,
            acceptance_rate=problem.acceptance_rate,
            order_index=problem.order_index,
            is_solved=is_solved,
            last_submitted_code=last_code,
            last_language=last_lang,
            test_cases=visible_tcs,
        )

    @classmethod
    async def run_code(
        cls,
        db: AsyncSession,
        identifier: str,
        payload: DsaRunRequest,
    ) -> DsaRunResponse:
        """
        Executes candidate code against visible sample test cases without recording submission.
        """
        await cls.ensure_seeded_problems(db)

        query = (
            select(DsaProblem)
            .options(selectinload(DsaProblem.test_cases))
            .where(
                or_(DsaProblem.id == identifier, DsaProblem.slug == identifier)
            )
        )
        problem = (await db.execute(query)).scalar_one_or_none()
        if not problem:
            raise EntityNotFoundError("DsaProblem", identifier)

        test_cases_to_run = []
        if payload.custom_input:
            test_cases_to_run = [{"input_data": payload.custom_input, "expected_output": ""}]
        else:
            test_cases_to_run = [
                {"input_data": tc.input_data, "expected_output": tc.expected_output}
                for tc in sorted(problem.test_cases, key=lambda x: x.order_index)
                if not tc.is_hidden
            ]

        return DsaSandboxService.run_or_submit(
            language=payload.language,
            code=payload.code,
            test_cases=test_cases_to_run,
            is_submission=False,
        )

    @classmethod
    async def submit_code(
        cls,
        db: AsyncSession,
        user_id: str,
        identifier: str,
        payload: DsaSubmitRequest,
    ) -> DsaSubmissionResponse:
        """
        Full evaluation against all visible and hidden test cases, persists submission,
        and automatically synchronizes verifiable SkillEvidence with Career Twin.
        """
        await cls.ensure_seeded_problems(db)

        query = (
            select(DsaProblem)
            .options(selectinload(DsaProblem.test_cases))
            .where(
                or_(DsaProblem.id == identifier, DsaProblem.slug == identifier)
            )
        )
        problem = (await db.execute(query)).scalar_one_or_none()
        if not problem:
            raise EntityNotFoundError("DsaProblem", identifier)

        all_test_cases = [
            {"input_data": tc.input_data, "expected_output": tc.expected_output, "is_hidden": tc.is_hidden}
            for tc in sorted(problem.test_cases, key=lambda x: x.order_index)
        ]

        # 1. Execute Sandbox
        eval_res = DsaSandboxService.run_or_submit(
            language=payload.language,
            code=payload.code,
            test_cases=all_test_cases,
            is_submission=True,
        )

        # 2. Analyze Complexity and Generate Placement Coach Feedback
        complexity_info = DsaSandboxService.analyze_python_ast_complexity(payload.code)
        ai_feedback = (
            f"Estimated Time Complexity: {complexity_info['time_complexity']} | "
            f"Space Complexity: {complexity_info['space_complexity']}.\n"
            f"Placement Coach Note: {complexity_info['feedback']}"
        )

        failed_input = None
        failed_expected = None
        failed_actual = None
        error_msg = eval_res.compile_error

        # Find first failing test case
        for r in eval_res.results:
            if not r.passed:
                failed_input = r.input_data
                failed_expected = r.expected_output
                failed_actual = r.actual_output
                if r.error_message:
                    error_msg = r.error_message
                break

        # 3. Create DsaSubmission Record
        submission = DsaSubmission(
            user_id=user_id,
            problem_id=problem.id,
            language=payload.language,
            code=payload.code,
            status=eval_res.status,
            runtime_ms=eval_res.runtime_ms,
            memory_mb=eval_res.memory_mb,
            passed_test_cases=eval_res.passed_count,
            total_test_cases=eval_res.total_count,
            error_message=error_msg,
            failed_test_case_input=failed_input,
            failed_test_case_expected=failed_expected,
            failed_test_case_actual=failed_actual,
            ai_feedback=ai_feedback,
        )
        db.add(submission)
        await db.flush()

        # 4. Update UserDsaProgress Record
        prog = (
            await db.execute(
                select(UserDsaProgress).where(
                    UserDsaProgress.user_id == user_id,
                    UserDsaProgress.problem_id == problem.id,
                )
            )
        ).scalar_one_or_none()

        is_accepted = eval_res.status == SubmissionStatus.ACCEPTED.value

        if not prog:
            prog = UserDsaProgress(
                user_id=user_id,
                problem_id=problem.id,
                is_solved=is_accepted,
                attempts_count=1,
                first_solved_at=datetime.now(timezone.utc) if is_accepted else None,
                best_runtime_ms=eval_res.runtime_ms if is_accepted else None,
                last_submitted_code=payload.code,
                last_language=payload.language,
            )
            db.add(prog)
        else:
            prog.attempts_count += 1
            prog.last_submitted_code = payload.code
            prog.last_language = payload.language
            if is_accepted:
                if not prog.is_solved:
                    prog.is_solved = True
                    prog.first_solved_at = datetime.now(timezone.utc)
                if prog.best_runtime_ms is None or eval_res.runtime_ms < prog.best_runtime_ms:
                    prog.best_runtime_ms = eval_res.runtime_ms

        # 5. Bidirectional Career Digital Twin Sync
        if is_accepted:
            # Find DSA canonical skill
            dsa_skill = (
                await db.execute(select(Skill).where(Skill.slug == "dsa"))
            ).scalar_one_or_none()
            if not dsa_skill:
                dsa_skill = (
                    await db.execute(select(Skill).where(Skill.slug.ilike("%algorithm%")))
                ).scalar_one_or_none()

            if dsa_skill:
                # Add SkillEvidence
                evidence = SkillEvidence(
                    user_id=user_id,
                    skill_id=dsa_skill.id,
                    source_type=EvidenceSourceType.DSA.value,
                    source_id=f"dsa:{problem.slug}",
                    evidence_text=f"Solved '{problem.title}' ({problem.difficulty}) with optimal {complexity_info['time_complexity']} complexity and {eval_res.runtime_ms:.1f}ms runtime.",
                    confidence=0.90,
                    verified=True,
                )
                db.add(evidence)

                # Update or create UserSkill
                user_skill = (
                    await db.execute(
                        select(UserSkill).where(
                            UserSkill.user_id == user_id,
                            UserSkill.skill_id == dsa_skill.id,
                        )
                    )
                ).scalar_one_or_none()

                if user_skill:
                    user_skill.proficiency = min(1.0, round(user_skill.proficiency + 0.05, 2))
                    user_skill.confidence = max(user_skill.confidence, 0.85)
                    user_skill.last_verified_at = datetime.now(timezone.utc)
                else:
                    user_skill = UserSkill(
                        user_id=user_id,
                        skill_id=dsa_skill.id,
                        proficiency=0.60,
                        confidence=0.85,
                        years_experience=1.0,
                        source=EvidenceSourceType.DSA.value,
                        last_verified_at=datetime.now(timezone.utc),
                    )
                    db.add(user_skill)

        await db.commit()
        await db.refresh(submission)

        return DsaSubmissionResponse(
            id=submission.id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            problem_title=problem.title,
            problem_slug=problem.slug,
            difficulty=problem.difficulty,
            language=submission.language,
            code=submission.code,
            status=submission.status,
            runtime_ms=submission.runtime_ms,
            memory_mb=submission.memory_mb,
            passed_test_cases=submission.passed_test_cases,
            total_test_cases=submission.total_test_cases,
            error_message=submission.error_message,
            failed_test_case_input=submission.failed_test_case_input,
            failed_test_case_expected=submission.failed_test_case_expected,
            failed_test_case_actual=submission.failed_test_case_actual,
            ai_feedback=submission.ai_feedback,
            created_at=submission.created_at,
        )

    @classmethod
    async def list_user_submissions(
        cls,
        db: AsyncSession,
        user_id: str,
        problem_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[DsaSubmissionResponse]:
        """Lists historical submissions for a candidate."""
        query = (
            select(DsaSubmission)
            .options(selectinload(DsaSubmission.problem))
            .where(DsaSubmission.user_id == user_id)
        )
        if problem_id:
            query = query.where(DsaSubmission.problem_id == problem_id)

        query = query.order_by(DsaSubmission.created_at.desc()).limit(limit)
        submissions = (await db.execute(query)).scalars().all()

        return [
            DsaSubmissionResponse(
                id=s.id,
                user_id=s.user_id,
                problem_id=s.problem_id,
                problem_title=s.problem.title if s.problem else None,
                problem_slug=s.problem.slug if s.problem else None,
                difficulty=s.problem.difficulty if s.problem else None,
                language=s.language,
                code=s.code,
                status=s.status,
                runtime_ms=s.runtime_ms,
                memory_mb=s.memory_mb,
                passed_test_cases=s.passed_test_cases,
                total_test_cases=s.total_test_cases,
                error_message=s.error_message,
                failed_test_case_input=s.failed_test_case_input,
                failed_test_case_expected=s.failed_test_case_expected,
                failed_test_case_actual=s.failed_test_case_actual,
                ai_feedback=s.ai_feedback,
                created_at=s.created_at,
            )
            for s in submissions
        ]

    @classmethod
    async def get_candidate_dsa_stats(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> DsaStatsResponse:
        """Calculates candidate DSA performance analytics."""
        await cls.ensure_seeded_problems(db)

        # Get all problems
        all_problems = (
            await db.execute(select(DsaProblem).where(DsaProblem.is_active.is_(True)))
        ).scalars().all()
        total_problems = len(all_problems)

        # Get solved records
        prog_records = (
            await db.execute(
                select(UserDsaProgress, DsaProblem)
                .join(DsaProblem, UserDsaProgress.problem_id == DsaProblem.id)
                .where(
                    UserDsaProgress.user_id == user_id,
                    UserDsaProgress.is_solved.is_(True),
                )
            )
        ).all()

        easy_solved = 0
        medium_solved = 0
        hard_solved = 0
        topic_breakdown: Dict[str, Dict[str, int]] = {}

        for _, prob in prog_records:
            if prob.difficulty == ProblemDifficulty.EASY.value:
                easy_solved += 1
            elif prob.difficulty == ProblemDifficulty.MEDIUM.value:
                medium_solved += 1
            elif prob.difficulty == ProblemDifficulty.HARD.value:
                hard_solved += 1

            cat = prob.category
            if cat not in topic_breakdown:
                topic_breakdown[cat] = {"solved": 0, "total": 0}
            topic_breakdown[cat]["solved"] += 1

        for prob in all_problems:
            cat = prob.category
            if cat not in topic_breakdown:
                topic_breakdown[cat] = {"solved": 0, "total": 0}
            topic_breakdown[cat]["total"] += 1

        # Total submissions count
        total_subs = (
            await db.execute(
                select(func.count(DsaSubmission.id)).where(DsaSubmission.user_id == user_id)
            )
        ).scalar_one()

        accepted_subs = (
            await db.execute(
                select(func.count(DsaSubmission.id)).where(
                    DsaSubmission.user_id == user_id,
                    DsaSubmission.status == SubmissionStatus.ACCEPTED.value,
                )
            )
        ).scalar_one()

        accuracy = (accepted_subs / max(1, total_subs)) * 100.0 if total_subs > 0 else 0.0

        return DsaStatsResponse(
            total_solved=len(prog_records),
            easy_solved=easy_solved,
            medium_solved=medium_solved,
            hard_solved=hard_solved,
            total_problems=total_problems,
            overall_accuracy_percentage=round(accuracy, 1),
            total_submissions=total_subs,
            topic_breakdown=topic_breakdown,
        )
