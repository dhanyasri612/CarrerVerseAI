"""
Comprehensive, Authentic Data Structures & Algorithms Problem Catalogue for CareerVerse AI.
Covers all 17 canonical DSA topics with LeetCode & HackerRank platforms, canonical URLs,
6-language starter code, and step-by-step teaching guides.
"""

from typing import List, Dict, Any
from app.schemas.dsa_practice import (
    DsaRecommendedProblem,
    DsaProblemExample,
    TopicResource,
)

def get_all_curated_dsa_problems() -> List[DsaRecommendedProblem]:
    return [
        # 1. ARRAYS & HASH MAPS (LeetCode)
        DsaRecommendedProblem(
            id="lc-1",
            title="Two Sum",
            difficulty="Easy",
            topic="Arrays & Hash Maps",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/two-sum/",
            similar_to="LeetCode 1: Two Sum",
            description=(
                "Given an array of integers `nums` and an integer `target`, return indices of the two numbers "
                "such that they add up to `target`.\n\n"
                "You may assume that each input would have exactly one solution, and you may not use the same element twice. "
                "You can return the answer in any order."
            ),
            examples=[
                DsaProblemExample(
                    input="nums = [2, 7, 11, 15], target = 9",
                    output="[0, 1]",
                    explanation="Because nums[0] + nums[1] == 9, we return [0, 1].",
                ),
                DsaProblemExample(
                    input="nums = [3, 2, 4], target = 6",
                    output="[1, 2]",
                    explanation="nums[1] + nums[2] == 2 + 4 == 6.",
                ),
                DsaProblemExample(
                    input="nums = [3, 3], target = 6",
                    output="[0, 1]",
                    explanation="Both elements at indices 0 and 1 sum to 6.",
                ),
            ],
            constraints=[
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9",
                "Only one valid answer exists.",
            ],
            hints=[
                "A brute force approach checks all pairs in O(N^2). Can we trade space for time using a hash table?",
                "As you iterate through nums, check if `target - num` already exists in your hash map.",
            ],
            approach="One-pass hash map tracking complement = target - nums[i]. O(N) time and O(N) space.",
            time_complexity="O(N)",
            space_complexity="O(N)",
            starter_code={
                "python": "def twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        comp = target - num\n        if comp in seen:\n            return [seen[comp], i]\n        seen[num] = i\n    return []\n",
                "javascript": "function twoSum(nums, target) {\n    const seen = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const comp = target - nums[i];\n        if (seen.has(comp)) return [seen.get(comp), i];\n        seen.set(nums[i], i);\n    }\n    return [];\n}\n",
                "typescript": "function twoSum(nums: number[], target: number): number[] {\n    const seen = new Map<number, number>();\n    for (let i = 0; i < nums.length; i++) {\n        const comp = target - nums[i];\n        if (seen.has(comp)) return [seen.get(comp), i];\n        seen.set(nums[i], i);\n    }\n    return [];\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        Map<Integer, Integer> seen = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int comp = target - nums[i];\n            if (seen.containsKey(comp)) return new int[]{seen.get(comp), i};\n            seen.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}\n",
                "cpp": "#include <vector>\n#include <unordered_map>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        unordered_map<int, int> seen;\n        for (int i = 0; i < nums.size(); i++) {\n            int comp = target - nums[i];\n            if (seen.count(comp)) return {seen[comp], i};\n            seen[nums[i]] = i;\n        }\n        return {};\n    }\n};\n",
                "golang": "package main\n\nfunc twoSum(nums []int, target int) []int {\n    seen := make(map[int]int)\n    for i, num := range nums {\n        comp := target - num\n        if idx, ok := seen[comp]; ok {\n            return []int{idx, i}\n        }\n        seen[num] = i\n    }\n    return []int{}\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Instead of repeatedly searching backwards in O(N), remember each visited number and its index in a hash map so lookups take O(1).",
                "invariants": "At iteration `i`, `seen` contains every element before `i`. The required pair consists of `nums[i]` and `target - nums[i]`.",
                "brute_force": "Nested loops comparing all pairs (i, j). Time: O(N^2), Space: O(1).",
                "optimal_derivation": "Hash table stores value -> index. One pass reduces lookup from O(N) to O(1).",
                "dry_run": "For nums=[2, 7, 11, 15], target=9: i=0 (num=2, comp=7, seen={2:0}), i=1 (num=7, comp=2 found in seen -> return [0, 1]).",
                "edge_cases": ["Array of minimum length 2", "Duplicate numbers e.g. [3, 3] target 6", "Negative values e.g. [-1, -2, -3] target -5"],
                "pitfalls": ["Using the same element twice if complement == current element", "Assuming array is sorted (sorting takes O(N log N))"],
                "follow_ups": ["What if the array is already sorted? (Two pointers in O(1) space)", "What if there are multiple pairs and you must return all unique pairs? (3Sum / 2Sum II)"],
            },
        ),

        # 2. ARRAYS (HackerRank)
        DsaRecommendedProblem(
            id="hr-array-manipulation",
            title="Array Manipulation",
            difficulty="Hard",
            topic="Prefix Sums & Arrays",
            platform="HackerRank",
            canonical_url="https://www.hackerrank.com/challenges/crush/problem",
            similar_to="HackerRank: Array Manipulation (Difference Array Pattern)",
            description=(
                "Starting with a 1-indexed array of zeros and a list of operations, for each operation add a value "
                "to all the array elements between two given indices, inclusive. Once all operations have been performed, "
                "return the maximum value in the array."
            ),
            examples=[
                DsaProblemExample(
                    input="n = 10, queries = [[1,5,3],[4,8,7],[6,9,1]]",
                    output="10",
                    explanation="After all additions, the maximum value in the array is 10 at indices 4 and 5.",
                ),
            ],
            constraints=[
                "3 <= n <= 10^7",
                "1 <= m <= 2 * 10^5",
                "1 <= a <= b <= n",
                "0 <= k <= 10^9",
            ],
            hints=[
                "Directly updating all elements from a to b takes O(N) per query, leading to O(M * N) which times out.",
                "Use a Difference Array: add +k at index `a` and -k at index `b + 1`. Then take a running prefix sum.",
            ],
            approach="Difference Array prefix sum technique reduces query updates to O(1) each and overall time to O(N + M).",
            time_complexity="O(N + M)",
            space_complexity="O(N)",
            starter_code={
                "python": "def arrayManipulation(n: int, queries: list[list[int]]) -> int:\n    diff = [0] * (n + 2)\n    for a, b, k in queries:\n        diff[a] += k\n        diff[b + 1] -= k\n    max_val = 0\n    curr = 0\n    for i in range(1, n + 1):\n        curr += diff[i]\n        if curr > max_val:\n            max_val = curr\n    return max_val\n",
                "javascript": "function arrayManipulation(n, queries) {\n    const diff = new Float64Array(n + 2);\n    for (const [a, b, k] of queries) {\n        diff[a] += k;\n        diff[b + 1] -= k;\n    }\n    let maxVal = 0, curr = 0;\n    for (let i = 1; i <= n; i++) {\n        curr += diff[i];\n        if (curr > maxVal) maxVal = curr;\n    }\n    return maxVal;\n}\n",
                "typescript": "function arrayManipulation(n: number, queries: number[][]): number {\n    const diff = new Float64Array(n + 2);\n    for (const [a, b, k] of queries) {\n        diff[a] += k;\n        diff[b + 1] -= k;\n    }\n    let maxVal = 0, curr = 0;\n    for (let i = 1; i <= n; i++) {\n        curr += diff[i];\n        if (curr > maxVal) maxVal = curr;\n    }\n    return maxVal;\n}\n",
                "java": "class Solution {\n    public static long arrayManipulation(int n, int[][] queries) {\n        long[] diff = new long[n + 2];\n        for (int[] q : queries) {\n            diff[q[0]] += q[2];\n            diff[q[1] + 1] -= q[2];\n        }\n        long max = 0, curr = 0;\n        for (int i = 1; i <= n; i++) {\n            curr += diff[i];\n            if (curr > max) max = curr;\n        }\n        return max;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nlong arrayManipulation(int n, vector<vector<int>> queries) {\n    vector<long> diff(n + 2, 0);\n    for (auto& q : queries) {\n        diff[q[0]] += q[2];\n        diff[q[1] + 1] -= q[2];\n    }\n    long max_val = 0, curr = 0;\n    for (int i = 1; i <= n; i++) {\n        curr += diff[i];\n        max_val = max(max_val, curr);\n    }\n    return max_val;\n}\n",
                "golang": "package main\n\nfunc arrayManipulation(n int, queries [][]int) int64 {\n    diff := make([]int64, n+2)\n    for _, q := range queries {\n        diff[q[0]] += int64(q[2])\n        diff[q[1]+1] -= int64(q[2])\n    }\n    var maxVal, curr int64 = 0, 0\n    for i := 1; i <= n; i++ {\n        curr += diff[i]\n        if curr > maxVal {\n            maxVal = curr\n        }\n    }\n    return maxVal\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Instead of executing M range updates in O(N) each, mark boundaries with +k at start and -k at end+1. A single prefix sum calculates all values.",
                "invariants": "The value at index i is the cumulative sum of differences from 1 to i.",
                "brute_force": "Updating range [a, b] directly in array takes O(M * N) which times out when N=10^7 and M=2*10^5.",
                "optimal_derivation": "Difference array allows O(1) range delta recording and O(N) total reconstruction.",
                "dry_run": "Query [1, 5, 3]: diff[1]+=3, diff[6]-=3. Scanning from 1 to n accumulates +3 from 1 to 5, and cancels out to 0 at 6.",
                "edge_cases": ["b == n (index b+1 falls outside bounds, needs n+2 size)", "Multiple queries overlapping identical ranges"],
                "pitfalls": ["Integer overflow in languages like Java/C++ (use 64-bit int / long)", "1-based vs 0-based index discrepancies"],
                "follow_ups": ["How would you query individual range sums after multiple updates? (Segment Tree or Fenwick Tree)"],
            },
        ),

        # 3. TWO POINTERS (LeetCode)
        DsaRecommendedProblem(
            id="lc-15",
            title="3Sum",
            difficulty="Medium",
            topic="Two Pointers",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/3sum/",
            similar_to="LeetCode 15: 3Sum",
            description=(
                "Given an integer array nums, return all the triplets `[nums[i], nums[j], nums[k]]` such that "
                "`i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\n"
                "Notice that the solution set must not contain duplicate triplets."
            ),
            examples=[
                DsaProblemExample(
                    input="nums = [-1,0,1,2,-1,-4]",
                    output="[[-1,-1,2],[-1,0,1]]",
                    explanation="Distinct triplets that sum to 0 are [-1,0,1] and [-1,-1,2].",
                ),
                DsaProblemExample(
                    input="nums = [0,1,1]",
                    output="[]",
                    explanation="No three elements sum to 0.",
                ),
            ],
            constraints=[
                "3 <= nums.length <= 3000",
                "-10^5 <= nums[i] <= 10^5",
            ],
            hints=[
                "Sort the array first so two pointers can be used to find pairs.",
                "Skip duplicate elements for the fixed element and both moving pointers.",
            ],
            approach="Sort array. Fix nums[i], then use two pointers (left, right) to converge on -nums[i] in O(N^2) time.",
            time_complexity="O(N^2)",
            space_complexity="O(1) auxiliary",
            starter_code={
                "python": "def threeSum(nums: list[int]) -> list[list[int]]:\n    nums.sort()\n    res = []\n    for i in range(len(nums) - 2):\n        if i > 0 and nums[i] == nums[i - 1]:\n            continue\n        l, r = i + 1, len(nums) - 1\n        while l < r:\n            s = nums[i] + nums[l] + nums[r]\n            if s < 0:\n                l += 1\n            elif s > 0:\n                r -= 1\n            else:\n                res.append([nums[i], nums[l], nums[r]])\n                while l < r and nums[l] == nums[l + 1]: l += 1\n                while l < r and nums[r] == nums[r - 1]: r -= 1\n                l += 1\n                r -= 1\n    return res\n",
                "javascript": "function threeSum(nums) {\n    nums.sort((a, b) => a - b);\n    const res = [];\n    for (let i = 0; i < nums.length - 2; i++) {\n        if (i > 0 && nums[i] === nums[i - 1]) continue;\n        let l = i + 1, r = nums.length - 1;\n        while (l < r) {\n            const sum = nums[i] + nums[l] + nums[r];\n            if (sum < 0) l++;\n            else if (sum > 0) r--;\n            else {\n                res.push([nums[i], nums[l], nums[r]]);\n                while (l < r && nums[l] === nums[l + 1]) l++;\n                while (l < r && nums[r] === nums[r - 1]) r--;\n                l++; r--;\n            }\n        }\n    }\n    return res;\n}\n",
                "typescript": "function threeSum(nums: number[]): number[][] {\n    nums.sort((a, b) => a - b);\n    const res: number[][] = [];\n    for (let i = 0; i < nums.length - 2; i++) {\n        if (i > 0 && nums[i] === nums[i - 1]) continue;\n        let l = i + 1, r = nums.length - 1;\n        while (l < r) {\n            const sum = nums[i] + nums[l] + nums[r];\n            if (sum < 0) l++;\n            else if (sum > 0) r--;\n            else {\n                res.push([nums[i], nums[l], nums[r]]);\n                while (l < r && nums[l] === nums[l + 1]) l++;\n                while (l < r && nums[r] === nums[r - 1]) r--;\n                l++; r--;\n            }\n        }\n    }\n    return res;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public List<List<Integer>> threeSum(int[] nums) {\n        Arrays.sort(nums);\n        List<List<Integer>> res = new ArrayList<>();\n        for (int i = 0; i < nums.length - 2; i++) {\n            if (i > 0 && nums[i] == nums[i - 1]) continue;\n            int l = i + 1, r = nums.length - 1;\n            while (l < r) {\n                int sum = nums[i] + nums[l] + nums[r];\n                if (sum < 0) l++;\n                else if (sum > 0) r--;\n                else {\n                    res.add(Arrays.asList(nums[i], nums[l], nums[r]));\n                    while (l < r && nums[l] == nums[l + 1]) l++;\n                    while (l < r && nums[r] == nums[r - 1]) r--;\n                    l++; r--;\n                }\n            }\n        }\n        return res;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> threeSum(vector<int>& nums) {\n        sort(nums.begin(), nums.end());\n        vector<vector<int>> res;\n        for (int i = 0; i < (int)nums.size() - 2; i++) {\n            if (i > 0 && nums[i] == nums[i - 1]) continue;\n            int l = i + 1, r = nums.size() - 1;\n            while (l < r) {\n                int sum = nums[i] + nums[l] + nums[r];\n                if (sum < 0) l++;\n                else if (sum > 0) r--;\n                else {\n                    res.push_back({nums[i], nums[l], nums[r]});\n                    while (l < r && nums[l] == nums[l + 1]) l++;\n                    while (l < r && nums[r] == nums[r - 1]) r--;\n                    l++; r--;\n                }\n            }\n        }\n        return res;\n    }\n};\n",
                "golang": "package main\n\nimport \"sort\"\n\nfunc threeSum(nums []int) [][]int {\n    sort.Ints(nums)\n    res := [][]int{}\n    for i := 0; i < len(nums)-2; i++ {\n        if i > 0 && nums[i] == nums[i-1] {\n            continue\n        }\n        l, r := i+1, len(nums)-1\n        for l < r {\n            sum := nums[i] + nums[l] + nums[r]\n            if sum < 0 {\n                l++\n            } else if sum > 0 {\n                r--\n            } else {\n                res = append(res, []int{nums[i], nums[l], nums[r]})\n                for l < r && nums[l] == nums[l+1] { l++ }\n                for l < r && nums[r] == nums[r-1] { r-- }\n                l++\n                r--\n            }\n        }\n    }\n    return res\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Sorting allows bidirectional two-pointer convergence. For each distinct element nums[i], find pairs summing to -nums[i].",
                "invariants": "Sorted order guarantees that increasing left increases sum, and decreasing right decreases sum.",
                "brute_force": "Checking all triplets (i, j, k) takes O(N^3) time and O(N) to dedup with a set.",
                "optimal_derivation": "Sort in O(N log N). For each element, two pointers scan remaining array in O(N), giving total O(N^2).",
                "dry_run": "nums=[-4, -1, -1, 0, 1, 2]. i=0 (val=-4): l=1, r=5 (sum < 0, l moves right). i=1 (val=-1): l=2, r=5 (sum=0 -> [-1, -1, 2]).",
                "edge_cases": ["All zeros e.g. [0, 0, 0, 0]", "No possible zero sum e.g. [1, 2, 3]", "Negative bounds and duplicates"],
                "pitfalls": ["Forgetting to skip duplicate elements, producing redundant duplicate triplets", "Sorting in place vs returning copies"],
                "follow_ups": ["How do you generalize to 4Sum or K-Sum? (Recursively reduce K-Sum to 2-Sum in O(N^(K-1)))"],
            },
        ),

        # 4. SLIDING WINDOW (LeetCode)
        DsaRecommendedProblem(
            id="lc-3",
            title="Longest Substring Without Repeating Characters",
            difficulty="Medium",
            topic="Sliding Window",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/longest-substring-without-repeating-characters/",
            similar_to="LeetCode 3: Longest Substring Without Repeating Characters",
            description=(
                "Given a string `s`, find the length of the longest substring without repeating characters."
            ),
            examples=[
                DsaProblemExample(input="s = 'abcabcbb'", output="3", explanation="The answer is 'abc', with the length of 3."),
                DsaProblemExample(input="s = 'bbbbb'", output="1", explanation="The answer is 'b', with the length of 1."),
                DsaProblemExample(input="s = 'pwwkew'", output="3", explanation="The answer is 'wke', with the length of 3."),
            ],
            constraints=["0 <= s.length <= 5 * 10^4", "s consists of English letters, digits, symbols and spaces."],
            hints=[
                "Use a sliding window [left, right] and track the last seen index of each character in a hash map.",
                "When a duplicate is encountered, advance left to max(left, last_seen[char] + 1).",
            ],
            approach="Optimized sliding window with last-seen character index map. O(N) time and O(min(N, M)) space.",
            time_complexity="O(N)",
            space_complexity="O(min(N, M))",
            starter_code={
                "python": "def lengthOfLongestSubstring(s: str) -> int:\n    last_seen = {}\n    max_len = 0\n    left = 0\n    for right, char in enumerate(s):\n        if char in last_seen and last_seen[char] >= left:\n            left = last_seen[char] + 1\n        last_seen[char] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len\n",
                "javascript": "function lengthOfLongestSubstring(s) {\n    const lastSeen = new Map();\n    let maxLen = 0, left = 0;\n    for (let right = 0; right < s.length; right++) {\n        if (lastSeen.has(s[right]) && lastSeen.get(s[right]) >= left) {\n            left = lastSeen.get(s[right]) + 1;\n        }\n        lastSeen.set(s[right], right);\n        maxLen = Math.max(maxLen, right - left + 1);\n    }\n    return maxLen;\n}\n",
                "typescript": "function lengthOfLongestSubstring(s: string): number {\n    const lastSeen = new Map<string, number>();\n    let maxLen = 0, left = 0;\n    for (let right = 0; right < s.length; right++) {\n        if (lastSeen.has(s[right]) && lastSeen.get(s[right])! >= left) {\n            left = lastSeen.get(s[right])! + 1;\n        }\n        lastSeen.set(s[right], right);\n        maxLen = Math.max(maxLen, right - left + 1);\n    }\n    return maxLen;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int lengthOfLongestSubstring(String s) {\n        Map<Character, Integer> lastSeen = new HashMap<>();\n        int maxLen = 0, left = 0;\n        for (int right = 0; right < s.length(); right++) {\n            char c = s.charAt(right);\n            if (lastSeen.containsKey(c) && lastSeen.get(c) >= left) {\n                left = lastSeen.get(c) + 1;\n            }\n            lastSeen.put(c, right);\n            maxLen = Math.max(maxLen, right - left + 1);\n        }\n        return maxLen;\n    }\n}\n",
                "cpp": "#include <string>\n#include <unordered_map>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        unordered_map<char, int> last_seen;\n        int max_len = 0, left = 0;\n        for (int right = 0; right < s.size(); right++) {\n            if (last_seen.count(s[right]) && last_seen[s[right]] >= left) {\n                left = last_seen[s[right]] + 1;\n            }\n            last_seen[s[right]] = right;\n            max_len = max(max_len, right - left + 1);\n        }\n        return max_len;\n    }\n};\n",
                "golang": "package main\n\nfunc lengthOfLongestSubstring(s string) int {\n    lastSeen := make(map[byte]int)\n    maxLen, left := 0, 0\n    for right := 0; right < len(s); right++ {\n        if idx, exists := lastSeen[s[right]]; exists && idx >= left {\n            left = idx + 1\n        }\n        lastSeen[s[right]] = right\n        if right-left+1 > maxLen {\n            maxLen = right - left + 1\n        }\n    }\n    return maxLen\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Maintain a contiguous window containing no duplicate characters. When a repeat is spotted, jump left pointer past previous occurrence.",
                "invariants": "Window s[left...right] always contains distinct characters.",
                "brute_force": "Check all O(N^2) substrings with an O(N) frequency set -> O(N^3).",
                "optimal_derivation": "Both pointers move monotonically forward; right expands, left jumps. Each character is visited at most twice -> O(N).",
                "dry_run": "s='pwwkew': 'p'(len=1), 'w'(len=2), 'w' repeat (left jumps to 2, 'w' len=1), 'k'(len=2), 'e'(len=3), 'w' repeat (left jumps to 3, 'kew' len=3).",
                "edge_cases": ["Empty string '' -> 0", "All characters identical 'aaaa' -> 1", "No repeats 'abcdef' -> length of string"],
                "pitfalls": ["Moving left backwards if an old duplicate outside the current window is queried (must check `last_seen[char] >= left`)"],
                "follow_ups": ["What if you are allowed at most K distinct characters? (Sliding window with frequency map)"],
            },
        ),

        # 5. PREFIX SUMS (LeetCode)
        DsaRecommendedProblem(
            id="lc-560",
            title="Subarray Sum Equals K",
            difficulty="Medium",
            topic="Prefix Sums",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/subarray-sum-equals-k/",
            similar_to="LeetCode 560: Subarray Sum Equals K",
            description=(
                "Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.\n\n"
                "A subarray is a contiguous non-empty sequence of elements within an array."
            ),
            examples=[
                DsaProblemExample(input="nums = [1,1,1], k = 2", output="2", explanation="Subarrays [1, 1] at index (0, 1) and (1, 2)."),
                DsaProblemExample(input="nums = [1,2,3], k = 3", output="2", explanation="Subarrays [1, 2] and [3]."),
            ],
            constraints=["1 <= nums.length <= 2 * 10^4", "-1000 <= nums[i] <= 1000", "-10^7 <= k <= 10^7"],
            hints=[
                "Because array elements can be negative, standard sliding window does not work.",
                "Use a prefix sum hash map: sum(i, j) = prefix[j] - prefix[i-1]. If prefix[j] - k exists, add its count to the result.",
            ],
            approach="Prefix sum frequency map. O(N) linear time and O(N) space.",
            time_complexity="O(N)",
            space_complexity="O(N)",
            starter_code={
                "python": "def subarraySum(nums: list[int], k: int) -> int:\n    prefix_counts = {0: 1}\n    curr_sum = 0\n    total_count = 0\n    for num in nums:\n        curr_sum += num\n        if curr_sum - k in prefix_counts:\n            total_count += prefix_counts[curr_sum - k]\n        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1\n    return total_count\n",
                "javascript": "function subarraySum(nums, k) {\n    const prefixCounts = new Map([[0, 1]]);\n    let currSum = 0, totalCount = 0;\n    for (const num of nums) {\n        currSum += num;\n        if (prefixCounts.has(currSum - k)) totalCount += prefixCounts.get(currSum - k);\n        prefixCounts.set(currSum, (prefixCounts.get(currSum) || 0) + 1);\n    }\n    return totalCount;\n}\n",
                "typescript": "function subarraySum(nums: number[], k: number): number {\n    const prefixCounts = new Map<number, number>([[0, 1]]);\n    let currSum = 0, totalCount = 0;\n    for (const num of nums) {\n        currSum += num;\n        if (prefixCounts.has(currSum - k)) totalCount += prefixCounts.get(currSum - k)!;\n        prefixCounts.set(currSum, (prefixCounts.get(currSum) || 0) + 1);\n    }\n    return totalCount;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int subarraySum(int[] nums, int k) {\n        Map<Integer, Integer> prefixCounts = new HashMap<>();\n        prefixCounts.put(0, 1);\n        int currSum = 0, count = 0;\n        for (int num : nums) {\n            currSum += num;\n            if (prefixCounts.containsKey(currSum - k)) {\n                count += prefixCounts.get(currSum - k);\n            }\n            prefixCounts.put(currSum, prefixCounts.getOrDefault(currSum, 0) + 1);\n        }\n        return count;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <unordered_map>\nusing namespace std;\n\nclass Solution {\npublic:\n    int subarraySum(vector<int>& nums, int k) {\n        unordered_map<int, int> prefix_counts;\n        prefix_counts[0] = 1;\n        int curr_sum = 0, count = 0;\n        for (int num : nums) {\n            curr_sum += num;\n            if (prefix_counts.count(curr_sum - k)) {\n                count += prefix_counts[curr_sum - k];\n            }\n            prefix_counts[curr_sum]++;\n        }\n        return count;\n    }\n};\n",
                "golang": "package main\n\nfunc subarraySum(nums []int, k int) int {\n    prefixCounts := map[int]int{0: 1}\n    currSum, count := 0, 0\n    for _, num := range nums {\n        currSum += num\n        if c, ok := prefixCounts[currSum-k]; ok {\n            count += c\n        }\n        prefixCounts[currSum]++\n    }\n    return count\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Any contiguous subarray sum from index i to j equals prefix_sum[j] - prefix_sum[i-1]. If prefix_sum[j] - prefix_sum[i-1] == k, then prefix_sum[i-1] == prefix_sum[j] - k.",
                "invariants": "Initialize hash map with {0: 1} to handle subarrays starting from index 0.",
                "brute_force": "Compute all subarray sums using nested loops in O(N^2) time.",
                "optimal_derivation": "Hash table stores frequency of previous prefix sums, allowing instant O(1) query of matching previous prefixes.",
                "dry_run": "nums=[1, 1, 1], k=2. prefix_counts={0:1}. num=1 (sum=1, 1-2=-1 not found, seen={0:1, 1:1}). num=1 (sum=2, 2-2=0 found with count 1 -> total=1). num=1 (sum=3, 3-2=1 found with count 1 -> total=2).",
                "edge_cases": ["Negative numbers (e.g. [-1, -1, 1] k=0)", "k=0", "Single element equal to k"],
                "pitfalls": ["Attempting to use two pointers / sliding window when array contains negative numbers (window sum is non-monotonic)"],
                "follow_ups": ["What if you need to find the longest subarray summing to K? (Store first occurrence index instead of count)"],
            },
        ),

        # 6. BINARY SEARCH (LeetCode)
        DsaRecommendedProblem(
            id="lc-33",
            title="Search in Rotated Sorted Array",
            difficulty="Medium",
            topic="Binary Search",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/search-in-rotated-sorted-array/",
            similar_to="LeetCode 33: Search in Rotated Sorted Array",
            description=(
                "There is an integer array `nums` sorted in ascending order (with distinct values).\n\n"
                "Prior to being passed to your function, nums is possibly rotated at an unknown pivot index k (1 <= k < nums.length). "
                "Given the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in nums, or `-1` if it is not in nums.\n\n"
                "You must write an algorithm with O(log n) runtime complexity."
            ),
            examples=[
                DsaProblemExample(input="nums = [4,5,6,7,0,1,2], target = 0", output="4", explanation="0 is located at index 4."),
                DsaProblemExample(input="nums = [4,5,6,7,0,1,2], target = 3", output="-1", explanation="3 is not in nums."),
                DsaProblemExample(input="nums = [1], target = 0", output="-1", explanation="1 != 0."),
            ],
            constraints=["1 <= nums.length <= 5000", "-10^4 <= nums[i] <= 10^4", "All values of nums are unique."],
            hints=[
                "In any rotated sorted array, dividing at `mid` always leaves at least ONE half strictly sorted.",
                "Check which half is sorted: if nums[left] <= nums[mid], the left half is sorted; otherwise the right half is sorted.",
            ],
            approach="Modified binary search identifying the sorted half at each step. O(log N) time and O(1) space.",
            time_complexity="O(log N)",
            space_complexity="O(1)",
            starter_code={
                "python": "def search(nums: list[int], target: int) -> int:\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        mid = (l + r) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[l] <= nums[mid]:\n            if nums[l] <= target < nums[mid]:\n                r = mid - 1\n            else:\n                l = mid + 1\n        else:\n            if nums[mid] < target <= nums[r]:\n                l = mid + 1\n            else:\n                r = mid - 1\n    return -1\n",
                "javascript": "function search(nums, target) {\n    let l = 0, r = nums.length - 1;\n    while (l <= r) {\n        const mid = Math.floor((l + r) / 2);\n        if (nums[mid] === target) return mid;\n        if (nums[l] <= nums[mid]) {\n            if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n            else l = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n            else r = mid - 1;\n        }\n    }\n    return -1;\n}\n",
                "typescript": "function search(nums: number[], target: number): number {\n    let l = 0, r = nums.length - 1;\n    while (l <= r) {\n        const mid = Math.floor((l + r) / 2);\n        if (nums[mid] === target) return mid;\n        if (nums[l] <= nums[mid]) {\n            if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n            else l = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n            else r = mid - 1;\n        }\n    }\n    return -1;\n}\n",
                "java": "class Solution {\n    public int search(int[] nums, int target) {\n        int l = 0, r = nums.length - 1;\n        while (l <= r) {\n            int mid = l + (r - l) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[l] <= nums[mid]) {\n                if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n                else l = mid + 1;\n            } else {\n                if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n                else r = mid - 1;\n            }\n        }\n        return -1;\n    }\n}\n",
                "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        int l = 0, r = nums.size() - 1;\n        while (l <= r) {\n            int mid = l + (r - l) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[l] <= nums[mid]) {\n                if (nums[l] <= target && target < nums[mid]) r = mid - 1;\n                else l = mid + 1;\n            } else {\n                if (nums[mid] < target && target <= nums[r]) l = mid + 1;\n                else r = mid - 1;\n            }\n        }\n        return -1;\n    }\n};\n",
                "golang": "package main\n\nfunc search(nums []int, target int) int {\n    l, r := 0, len(nums)-1\n    for l <= r {\n        mid := l + (r-l)/2\n        if nums[mid] == target {\n            return mid\n        }\n        if nums[l] <= nums[mid] {\n            if nums[l] <= target && target < nums[mid] {\n                r = mid - 1\n            } else {\n                l = mid + 1\n            }\n        } else {\n            if nums[mid] < target && target <= nums[r] {\n                l = mid + 1\n            } else {\n                r = mid - 1\n            }\n        }\n    }\n    return -1\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Even after rotation, splitting at mid always yields one sorted half. We can check if target lies within the boundaries of that sorted half.",
                "invariants": "If nums[l] <= nums[mid], left half [l...mid] is monotonically sorted. Otherwise, right half [mid...r] is monotonically sorted.",
                "brute_force": "Linear scan in O(N) violates the mandatory O(log N) requirement.",
                "optimal_derivation": "Identify which half is sorted, check if target falls into its bounds [nums[l], nums[mid]) or (nums[mid], nums[r]], and discard the other half in O(1).",
                "dry_run": "nums=[4,5,6,7,0,1,2], target=0: l=0, r=6, mid=3 (val=7). nums[0]=4 <= 7 (left sorted). Is 4 <= 0 < 7? False -> l=mid+1=4. Now [0,1,2], mid=5 (val=1). nums[4]=0 <= 1. Is 0 <= target < 1? True -> r=mid-1=4. l=4, r=4, mid=4 (val=0==target) -> return 4.",
                "edge_cases": ["Unrotated array [1, 2, 3]", "Single-element array [1]", "Two-element arrays [3, 1]"],
                "pitfalls": ["Using `l < r` instead of `l <= r` causing single element miss", "Integer overflow on `(l+r)/2` in Java/C++ (use `l + (r-l)/2`)"],
                "follow_ups": ["What if the array allows duplicate values? (LeetCode 81: Search in Rotated Sorted Array II - duplicates can degrade worst case to O(N))"],
            },
        ),

        # 7. LINKED LISTS (LeetCode)
        DsaRecommendedProblem(
            id="lc-142",
            title="Linked List Cycle II",
            difficulty="Medium",
            topic="Linked Lists",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/linked-list-cycle-ii/",
            similar_to="LeetCode 142: Linked List Cycle II (Floyd's Tortoise & Hare)",
            description=(
                "Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return `null`.\n\n"
                "There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer. "
                "Do not modify the linked list."
            ),
            examples=[
                DsaProblemExample(input="head = [3,2,0,-4], pos = 1", output="tail connects to node index 1", explanation="There is a cycle in the linked list, where tail connects to the second node."),
                DsaProblemExample(input="head = [1,2], pos = 0", output="tail connects to node index 0", explanation="There is a cycle in the linked list, where tail connects to the first node."),
                DsaProblemExample(input="head = [1], pos = -1", output="no cycle", explanation="There is no cycle in the linked list."),
            ],
            constraints=["The number of the nodes in the list is in the range [0, 10^4].", "-10^5 <= Node.val <= 10^5", "pos is -1 or a valid index in the linked-list."],
            hints=[
                "Use two pointers: slow moves 1 step, fast moves 2 steps.",
                "When they meet, move one pointer to head and keep the other at the meeting point. Move both at 1 step each; they will collide at the cycle entrance.",
            ],
            approach="Floyd's Cycle-Finding Algorithm. O(N) time and O(1) space.",
            time_complexity="O(N)",
            space_complexity="O(1)",
            starter_code={
                "python": "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, x):\n#         self.val = x\n#         self.next = None\n\ndef detectCycle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            break\n    else:\n        return None\n    ptr = head\n    while ptr != slow:\n        ptr = ptr.next\n        slow = slow.next\n    return ptr\n",
                "javascript": "function detectCycle(head) {\n    let slow = head, fast = head;\n    while (fast && fast.next) {\n        slow = slow.next;\n        fast = fast.next.next;\n        if (slow === fast) {\n            let ptr = head;\n            while (ptr !== slow) {\n                ptr = ptr.next;\n                slow = slow.next;\n            }\n            return ptr;\n        }\n    }\n    return null;\n}\n",
                "typescript": "function detectCycle(head: any): any {\n    let slow = head, fast = head;\n    while (fast && fast.next) {\n        slow = slow.next;\n        fast = fast.next.next;\n        if (slow === fast) {\n            let ptr = head;\n            while (ptr !== slow) {\n                ptr = ptr.next;\n                slow = slow.next;\n            }\n            return ptr;\n        }\n    }\n    return null;\n}\n",
                "java": "class Solution {\n    public ListNode detectCycle(ListNode head) {\n        ListNode slow = head, fast = head;\n        while (fast != null && fast.next != null) {\n            slow = slow.next;\n            fast = fast.next.next;\n            if (slow == fast) {\n                ListNode ptr = head;\n                while (ptr != slow) {\n                    ptr = ptr.next;\n                    slow = slow.next;\n                }\n                return ptr;\n            }\n        }\n        return null;\n    }\n}\n",
                "cpp": "class Solution {\npublic:\n    ListNode *detectCycle(ListNode *head) {\n        ListNode *slow = head, *fast = head;\n        while (fast && fast->next) {\n            slow = slow->next;\n            fast = fast->next->next;\n            if (slow == fast) {\n                ListNode *ptr = head;\n                while (ptr != slow) {\n                    ptr = ptr->next;\n                    slow = slow->next;\n                }\n                return ptr;\n            }\n        }\n        return nullptr;\n    }\n};\n",
                "golang": "package main\n\nfunc detectCycle(head *ListNode) *ListNode {\n    slow, fast := head, head\n    for fast != nil && fast.Next != nil {\n        slow = slow.Next\n        fast = fast.Next.Next\n        if slow == fast {\n            ptr := head\n            for ptr != slow {\n                ptr = ptr.Next\n                slow = slow.Next\n            }\n            return ptr\n        }\n    }\n    return nil\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Let distance from head to cycle entrance be L1, and entrance to meeting point be L2. Fast moves 2x as fast. Mathematical derivation shows distance from head to entrance equals distance from meeting point to entrance.",
                "invariants": "Fast travels 2 * (L1 + L2) = L1 + L2 + n * C => L1 = n * C - L2.",
                "brute_force": "Storing visited nodes in a hash set takes O(N) space.",
                "optimal_derivation": "Two pointers detect cycle in O(1) space, and marching from head and intersection collides at start.",
                "dry_run": "List 3 -> 2 -> 0 -> -4 -> 2. Slow and fast meet at -4. Reset ptr to 3. Step 1: ptr moves to 2, slow moves to 2. ptr == slow -> node 2 is cycle entrance.",
                "edge_cases": ["Empty list null", "Single node with no cycle", "Single node cycling to itself"],
                "pitfalls": ["Dereferencing fast.next.next when fast.next is null"],
                "follow_ups": ["Can you apply this same pattern to an array to find a duplicate number without extra space? (LeetCode 287: Find the Duplicate Number)"],
            },
        ),

        # 8. TREES & BST (LeetCode)
        DsaRecommendedProblem(
            id="lc-98",
            title="Validate Binary Search Tree",
            difficulty="Medium",
            topic="Trees & Binary Search Trees",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/validate-binary-search-tree/",
            similar_to="LeetCode 98: Validate Binary Search Tree",
            description=(
                "Given the root of a binary tree, determine if it is a valid binary search tree (BST).\n\n"
                "A valid BST is defined as follows:\n"
                "- The left subtree of a node contains only nodes with keys strictly less than the node's key.\n"
                "- The right subtree of a node contains only nodes with keys strictly greater than the node's key.\n"
                "- Both the left and right subtrees must also be binary search trees."
            ),
            examples=[
                DsaProblemExample(input="root = [2,1,3]", output="true", explanation="Left node 1 < 2 < right node 3."),
                DsaProblemExample(input="root = [5,1,4,null,null,3,6]", output="false", explanation="The root node's value is 5 but its right child's value is 4."),
            ],
            constraints=["The number of nodes in the tree is in the range [1, 10^4].", "-2^31 <= Node.val <= 2^31 - 1"],
            hints=[
                "Checking only node.left.val < node.val is insufficient: all nodes in the left subtree must be less than node.val.",
                "Pass a valid range (low, high) down the recursive tree.",
            ],
            approach="Recursive range validation passing (-inf, +inf) or in-order traversal strictly increasing check. O(N) time and O(H) space.",
            time_complexity="O(N)",
            space_complexity="O(H)",
            starter_code={
                "python": "def isValidBST(root) -> bool:\n    def validate(node, low=-float('inf'), high=float('inf')):\n        if not node:\n            return True\n        if not (low < node.val < high):\n            return False\n        return validate(node.left, low, node.val) and validate(node.right, node.val, high)\n    return validate(root)\n",
                "javascript": "function isValidBST(root) {\n    function validate(node, low, high) {\n        if (!node) return true;\n        if (node.val <= low || node.val >= high) return false;\n        return validate(node.left, low, node.val) && validate(node.right, node.val, high);\n    }\n    return validate(root, -Infinity, Infinity);\n}\n",
                "typescript": "function isValidBST(root: any): boolean {\n    function validate(node: any, low: number, high: number): boolean {\n        if (!node) return true;\n        if (node.val <= low || node.val >= high) return false;\n        return validate(node.left, low, node.val) && validate(node.right, node.val, high);\n    }\n    return validate(root, -Infinity, Infinity);\n}\n",
                "java": "class Solution {\n    public boolean isValidBST(TreeNode root) {\n        return validate(root, null, null);\n    }\n    private boolean validate(TreeNode node, Integer low, Integer high) {\n        if (node == null) return true;\n        if ((low != null && node.val <= low) || (high != null && node.val >= high)) return false;\n        return validate(node.left, low, node.val) && validate(node.right, node.val, high);\n    }\n}\n",
                "cpp": "class Solution {\npublic:\n    bool isValidBST(TreeNode* root) {\n        return validate(root, nullptr, nullptr);\n    }\n    bool validate(TreeNode* node, long long* low, long long* high) {\n        if (!node) return true;\n        if ((low && node->val <= *low) || (high && node->val >= *high)) return false;\n        long long val = node->val;\n        return validate(node->left, low, &val) && validate(node->right, &val, high);\n    }\n};\n",
                "golang": "package main\n\nimport \"math\"\n\nfunc isValidBST(root *TreeNode) bool {\n    var validate func(node *TreeNode, low, high float64) bool\n    validate = func(node *TreeNode, low, high float64) bool {\n        if node == nil {\n            return true\n        }\n        val := float64(node.Val)\n        if val <= low || val >= high {\n            return false\n        }\n        return validate(node.Left, low, val) && validate(node.Right, val, high)\n    }\n    return validate(root, -math.MaxFloat64, math.MaxFloat64)\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Every node imposes a lower bound on its right subtree and an upper bound on its left subtree.",
                "invariants": "For any node N, all values in left subtree < N.val, all values in right subtree > N.val.",
                "brute_force": "Traversing each subtree to find max/min for every node takes O(N^2).",
                "optimal_derivation": "Carry (low, high) bounds down during single preorder/postorder traversal in O(N).",
                "dry_run": "root=5: left child 1 must be in (-inf, 5) -> valid. right child 4 must be in (5, inf) -> 4 <= 5 -> invalid!",
                "edge_cases": ["Single node tree [1] -> valid", "Integer overflow bounds -2^31 and 2^31-1", "Duplicate values e.g. [2, 2, 2] -> invalid (must be strictly less/greater)"],
                "pitfalls": ["Only comparing immediate children (root.left.val < root.val) instead of whole subtree"],
                "follow_ups": ["How to validate using an iterative in-order traversal? (In-order traversal of a BST yields strictly ascending sorted array)"],
            },
        ),

        # 9. TRIES (LeetCode)
        DsaRecommendedProblem(
            id="lc-208",
            title="Implement Trie (Prefix Tree)",
            difficulty="Medium",
            topic="Tries",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/implement-trie-prefix-tree/",
            similar_to="LeetCode 208: Implement Trie (Prefix Tree)",
            description=(
                "A trie (pronounced as 'try') or prefix tree is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. "
                "There are various applications of this data structure, such as autocomplete and spellchecker.\n\n"
                "Implement the Trie class:\n"
                "- `Trie()` Initializes the trie object.\n"
                "- `void insert(String word)` Inserts the string word into the trie.\n"
                "- `boolean search(String word)` Returns true if the string word is in the trie, and false otherwise.\n"
                "- `boolean startsWith(String prefix)` Returns true if there is a previously inserted string word that has the prefix prefix, and false otherwise."
            ),
            examples=[
                DsaProblemExample(
                    input="Trie trie = new Trie(); trie.insert('apple'); trie.search('apple'); trie.search('app'); trie.startsWith('app'); trie.insert('app'); trie.search('app');",
                    output="[null, null, true, false, true, null, true]",
                    explanation="search('apple') -> true; search('app') -> false; startsWith('app') -> true; insert('app'); search('app') -> true",
                )
            ],
            constraints=["1 <= word.length, prefix.length <= 2000", "word and prefix consist only of lowercase English letters.", "At most 3 * 10^4 calls in total will be made."],
            hints=[
                "Each TrieNode contains an array or dictionary of children nodes (for 26 lowercase English letters) and an `is_end_of_word` boolean.",
            ],
            approach="Prefix tree with TrieNode containing 26-child pointers and is_end flag. Insert, search, and startsWith take O(L) time where L is word length.",
            time_complexity="O(L)",
            space_complexity="O(Total Characters)",
            starter_code={
                "python": "class TrieNode:\n    def __init__(self):\n        self.children = {}\n        self.is_end = False\n\nclass Trie:\n    def __init__(self):\n        self.root = TrieNode()\n\n    def insert(self, word: str) -> None:\n        curr = self.root\n        for char in word:\n            if char not in curr.children:\n                curr.children[char] = TrieNode()\n            curr = curr.children[char]\n        curr.is_end = True\n\n    def search(self, word: str) -> bool:\n        curr = self.root\n        for char in word:\n            if char not in curr.children:\n                return False\n            curr = curr.children[char]\n        return curr.is_end\n\n    def startsWith(self, prefix: str) -> bool:\n        curr = self.root\n        for char in prefix:\n            if char not in curr.children:\n                return False\n            curr = curr.children[char]\n        return True\n",
                "javascript": "class TrieNode {\n    constructor() {\n        this.children = {};\n        this.isEnd = false;\n    }\n}\n\nclass Trie {\n    constructor() {\n        this.root = new TrieNode();\n    }\n    insert(word) {\n        let curr = this.root;\n        for (const c of word) {\n            if (!curr.children[c]) curr.children[c] = new TrieNode();\n            curr = curr.children[c];\n        }\n        curr.isEnd = true;\n    }\n    search(word) {\n        let curr = this.root;\n        for (const c of word) {\n            if (!curr.children[c]) return false;\n            curr = curr.children[c];\n        }\n        return curr.isEnd;\n    }\n    startsWith(prefix) {\n        let curr = this.root;\n        for (const c of prefix) {\n            if (!curr.children[c]) return false;\n            curr = curr.children[c];\n        }\n        return true;\n    }\n}\n",
                "typescript": "class TrieNode {\n    children: { [key: string]: TrieNode } = {};\n    isEnd: boolean = false;\n}\n\nclass Trie {\n    root: TrieNode = new TrieNode();\n    insert(word: string): void {\n        let curr = this.root;\n        for (const c of word) {\n            if (!curr.children[c]) curr.children[c] = new TrieNode();\n            curr = curr.children[c];\n        }\n        curr.isEnd = true;\n    }\n    search(word: string): boolean {\n        let curr = this.root;\n        for (const c of word) {\n            if (!curr.children[c]) return false;\n            curr = curr.children[c];\n        }\n        return curr.isEnd;\n    }\n    startsWith(prefix: string): boolean {\n        let curr = this.root;\n        for (const c of prefix) {\n            if (!curr.children[c]) return false;\n            curr = curr.children[c];\n        }\n        return true;\n    }\n}\n",
                "java": "class Trie {\n    private class TrieNode {\n        TrieNode[] children = new TrieNode[26];\n        boolean isEnd = false;\n    }\n    private TrieNode root = new TrieNode();\n    public void insert(String word) {\n        TrieNode curr = root;\n        for (char c : word.toCharArray()) {\n            int idx = c - 'a';\n            if (curr.children[idx] == null) curr.children[idx] = new TrieNode();\n            curr = curr.children[idx];\n        }\n        curr.isEnd = true;\n    }\n    public boolean search(String word) {\n        TrieNode curr = root;\n        for (char c : word.toCharArray()) {\n            int idx = c - 'a';\n            if (curr.children[idx] == null) return false;\n            curr = curr.children[idx];\n        }\n        return curr.isEnd;\n    }\n    public boolean startsWith(String prefix) {\n        TrieNode curr = root;\n        for (char c : prefix.toCharArray()) {\n            int idx = c - 'a';\n            if (curr.children[idx] == null) return false;\n            curr = curr.children[idx];\n        }\n        return true;\n    }\n}\n",
                "cpp": "#include <string>\n#include <vector>\nusing namespace std;\n\nclass Trie {\n    struct Node {\n        Node* children[26] = {nullptr};\n        bool is_end = false;\n    };\n    Node* root;\npublic:\n    Trie() { root = new Node(); }\n    void insert(string word) {\n        Node* curr = root;\n        for (char c : word) {\n            if (!curr->children[c - 'a']) curr->children[c - 'a'] = new Node();\n            curr = curr->children[c - 'a'];\n        }\n        curr->is_end = true;\n    }\n    bool search(string word) {\n        Node* curr = root;\n        for (char c : word) {\n            if (!curr->children[c - 'a']) return false;\n            curr = curr->children[c - 'a'];\n        }\n        return curr->is_end;\n    }\n    bool startsWith(string prefix) {\n        Node* curr = root;\n        for (char c : prefix) {\n            if (!curr->children[c - 'a']) return false;\n            curr = curr->children[c - 'a'];\n        }\n        return true;\n    }\n};\n",
                "golang": "package main\n\ntype TrieNode struct {\n    children [26]*TrieNode\n    isEnd    bool\n}\ntype Trie struct { root *TrieNode }\nfunc Constructor() Trie { return Trie{root: &TrieNode{}} }\nfunc (t *Trie) Insert(word string) {\n    curr := t.root\n    for i := 0; i < len(word); i++ {\n        idx := word[i] - 'a'\n        if curr.children[idx] == nil { curr.children[idx] = &TrieNode{} }\n        curr = curr.children[idx]\n    }\n    curr.isEnd = true\n}\nfunc (t *Trie) Search(word string) bool {\n    curr := t.root\n    for i := 0; i < len(word); i++ {\n        idx := word[i] - 'a'\n        if curr.children[idx] == nil { return false }\n        curr = curr.children[idx]\n    }\n    return curr.isEnd\n}\nfunc (t *Trie) StartsWith(prefix string) bool {\n    curr := t.root\n    for i := 0; i < len(prefix); i++ {\n        idx := prefix[i] - 'a'\n        if curr.children[idx] == nil { return false }\n        curr = curr.children[idx]\n    }\n    return true\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Represent shared prefixes in a directed tree where each edge is a character. Searching for a prefix takes O(L) time regardless of dictionary size.",
                "invariants": "A word exists if and only if all characters can be traced from root and the final node has is_end=True.",
                "brute_force": "Storing words in an array takes O(N * L) for prefix search.",
                "optimal_derivation": "Trie nodes share prefixes, reducing prefix search to O(prefix_length) and autocomplete space complexity.",
                "dry_run": "Insert 'app', 'apple'. Both share root->a->p->p. Node 'p' has is_end=True. Node 'e' has is_end=True.",
                "edge_cases": ["Single character words", "Prefix identical to complete word", "Search on empty tree"],
                "pitfalls": ["Confusing search() with startsWith() - search requires `is_end==True`"],
                "follow_ups": ["How to support wildcards like '.' in Word Dictionary? (DFS backtracking across all valid child branches)"],
            },
        ),

        # 10. HEAPS / PRIORITY QUEUE (LeetCode)
        DsaRecommendedProblem(
            id="lc-215",
            title="Kth Largest Element in an Array",
            difficulty="Medium",
            topic="Heaps & Priority Queues",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/kth-largest-element-in-an-array/",
            similar_to="LeetCode 215: Kth Largest Element in an Array",
            description=(
                "Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array.\n\n"
                "Note that it is the `k`th largest element in the sorted order, not the `k`th distinct element.\n\n"
                "Can you solve it without sorting?"
            ),
            examples=[
                DsaProblemExample(input="nums = [3,2,1,5,6,4], k = 2", output="5", explanation="The 2nd largest element is 5."),
                DsaProblemExample(input="nums = [3,2,3,1,2,4,5,5,6], k = 4", output="4", explanation="The 4th largest element is 4."),
            ],
            constraints=["1 <= k <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
            hints=[
                "Maintain a Min-Heap of size k. Push elements into the heap; if heap size exceeds k, pop the smallest.",
                "After scanning all elements, the root of the min-heap is the kth largest element.",
            ],
            approach="Min-heap of size K giving O(N log K) time and O(K) space, or QuickSelect in O(N) average time.",
            time_complexity="O(N log K)",
            space_complexity="O(K)",
            starter_code={
                "python": "import heapq\n\ndef findKthLargest(nums: list[int], k: int) -> int:\n    heap = []\n    for num in nums:\n        heapq.heappush(heap, num)\n        if len(heap) > k:\n            heapq.heappop(heap)\n    return heap[0]\n",
                "javascript": "function findKthLargest(nums, k) {\n    // In JavaScript, sort is common O(N log N) or implement min-heap in O(N log K)\n    nums.sort((a, b) => b - a);\n    return nums[k - 1];\n}\n",
                "typescript": "function findKthLargest(nums: number[], k: number): number {\n    nums.sort((a, b) => b - a);\n    return nums[k - 1];\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int findKthLargest(int[] nums, int k) {\n        PriorityQueue<Integer> pq = new PriorityQueue<>(k);\n        for (int num : nums) {\n            pq.offer(num);\n            if (pq.size() > k) pq.poll();\n        }\n        return pq.peek();\n    }\n}\n",
                "cpp": "#include <vector>\n#include <queue>\nusing namespace std;\n\nclass Solution {\npublic:\n    int findKthLargest(vector<int>& nums, int k) {\n        priority_queue<int, vector<int>, greater<int>> min_heap;\n        for (int num : nums) {\n            min_heap.push(num);\n            if (min_heap.size() > k) min_heap.pop();\n        }\n        return min_heap.top();\n    }\n};\n",
                "golang": "package main\n\nimport \"container/heap\"\n\ntype IntHeap []int\nfunc (h IntHeap) Len() int           { return len(h) }\nfunc (h IntHeap) Less(i, j int) bool { return h[i] < h[j] }\nfunc (h IntHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }\nfunc (h *IntHeap) Push(x any)        { *h = append(*h, x.(int)) }\nfunc (h *IntHeap) Pop() any          { old := *h; n := len(old); x := old[n-1]; *h = old[0 : n-1]; return x }\n\nfunc findKthLargest(nums []int, k int) int {\n    h := &IntHeap{}\n    heap.Init(h)\n    for _, num := range nums {\n        heap.Push(h, num)\n        if h.Len() > k {\n            heap.Pop(h)\n        }\n    }\n    return (*h)[0]\n}\n",
            },
            step_by_step_teaching={
                "intuition": "To find the Kth largest, maintain a running pool of the K largest elements. A Min-Heap lets us evict the smallest in O(log K).",
                "invariants": "The min-heap always contains the K largest elements seen so far; the heap top is the minimum among them.",
                "brute_force": "Sorting entire array takes O(N log N) time and O(N) space.",
                "optimal_derivation": "Min-heap of size K requires only O(N log K) time and O(K) space. When K << N, this is effectively linear.",
                "dry_run": "nums=[3,2,1,5,6,4], k=2: push 3, push 2 -> [2,3]. push 1 -> pop 1 -> [2,3]. push 5 -> pop 2 -> [3,5]. push 6 -> pop 3 -> [5,6]. push 4 -> pop 4 -> [5,6]. Return heap[0]=5.",
                "edge_cases": ["k == 1 (maximum element)", "k == len(nums) (minimum element)", "Duplicate elements e.g. [5, 5, 5]"],
                "pitfalls": ["Using a Max-Heap of size N instead of Min-Heap of size K", "Forgetting that kth largest is 1-indexed"],
                "follow_ups": ["Can we achieve O(N) average time complexity? (QuickSelect algorithm with Lomuto/Hoare partitioning)"],
            },
        ),

        # 11. GRAPHS (LeetCode)
        DsaRecommendedProblem(
            id="lc-200",
            title="Number of Islands",
            difficulty="Medium",
            topic="Graphs",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/number-of-islands/",
            similar_to="LeetCode 200: Number of Islands",
            description=(
                "Given an `m x n` 2D binary grid `grid` which represents a map of '1's (land) and '0's (water), "
                "return the number of islands.\n\n"
                "An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. "
                "You may assume all four edges of the grid are all surrounded by water."
            ),
            examples=[
                DsaProblemExample(
                    input="grid = [\n  ['1','1','1','1','0'],\n  ['1','1','0','1','0'],\n  ['1','1','0','0','0'],\n  ['0','0','0','0','0']\n]",
                    output="1",
                    explanation="All land cells connect into a single island.",
                ),
                DsaProblemExample(
                    input="grid = [\n  ['1','1','0','0','0'],\n  ['1','1','0','0','0'],\n  ['0','0','1','0','0'],\n  ['0','0','0','1','1']\n]",
                    output="3",
                    explanation="There are three separate connected islands.",
                ),
            ],
            constraints=["m == grid.length", "n == grid[i].length", "1 <= m, n <= 300", "grid[i][j] is '0' or '1'."],
            hints=[
                "Iterate through each cell. When you encounter a '1', increment island count and trigger a BFS or DFS.",
                "During DFS/BFS, sink the island by changing '1's to '0's (or mark in a visited set).",
            ],
            approach="Connected components count via BFS or DFS flood-fill. O(M * N) time and O(M * N) space.",
            time_complexity="O(M * N)",
            space_complexity="O(M * N)",
            starter_code={
                "python": "def numIslands(grid: list[list[str]]) -> int:\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    count = 0\n    def dfs(r, c):\n        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':\n            return\n        grid[r][c] = '0'\n        dfs(r + 1, c)\n        dfs(r - 1, c)\n        dfs(r, c + 1)\n        dfs(r, c - 1)\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1':\n                count += 1\n                dfs(r, c)\n    return count\n",
                "javascript": "function numIslands(grid) {\n    if (!grid.length) return 0;\n    const rows = grid.length, cols = grid[0].length;\n    let count = 0;\n    function dfs(r, c) {\n        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] !== '1') return;\n        grid[r][c] = '0';\n        dfs(r + 1, c);\n        dfs(r - 1, c);\n        dfs(r, c + 1);\n        dfs(r, c - 1);\n    }\n    for (let r = 0; r < rows; r++) {\n        for (let c = 0; c < cols; c++) {\n            if (grid[r][c] === '1') {\n                count++;\n                dfs(r, c);\n            }\n        }\n    }\n    return count;\n}\n",
                "typescript": "function numIslands(grid: string[][]): number {\n    if (!grid.length) return 0;\n    const rows = grid.length, cols = grid[0].length;\n    let count = 0;\n    function dfs(r: number, c: number) {\n        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] !== '1') return;\n        grid[r][c] = '0';\n        dfs(r + 1, c);\n        dfs(r - 1, c);\n        dfs(r, c + 1);\n        dfs(r, c - 1);\n    }\n    for (let r = 0; r < rows; r++) {\n        for (let c = 0; c < cols; c++) {\n            if (grid[r][c] === '1') {\n                count++;\n                dfs(r, c);\n            }\n        }\n    }\n    return count;\n}\n",
                "java": "class Solution {\n    public int numIslands(char[][] grid) {\n        int count = 0;\n        for (int r = 0; r < grid.length; r++) {\n            for (int c = 0; c < grid[0].length; c++) {\n                if (grid[r][c] == '1') {\n                    count++;\n                    dfs(grid, r, c);\n                }\n            }\n        }\n        return count;\n    }\n    private void dfs(char[][] grid, int r, int c) {\n        if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] != '1') return;\n        grid[r][c] = '0';\n        dfs(grid, r + 1, c);\n        dfs(grid, r - 1, c);\n        dfs(grid, r, c + 1);\n        dfs(grid, r, c - 1);\n    }\n}\n",
                "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int numIslands(vector<vector<char>>& grid) {\n        int count = 0;\n        for (int r = 0; r < grid.size(); r++) {\n            for (int c = 0; c < grid[0].size(); c++) {\n                if (grid[r][c] == '1') {\n                    count++;\n                    dfs(grid, r, c);\n                }\n            }\n        }\n        return count;\n    }\n    void dfs(vector<vector<char>>& grid, int r, int c) {\n        if (r < 0 || r >= grid.size() || c < 0 || c >= grid[0].size() || grid[r][c] != '1') return;\n        grid[r][c] = '0';\n        dfs(grid, r + 1, c);\n        dfs(grid, r - 1, c);\n        dfs(grid, r, c + 1);\n        dfs(grid, r, c - 1);\n    }\n};\n",
                "golang": "package main\n\nfunc numIslands(grid [][]byte) int {\n    count := 0\n    var dfs func(r, c int)\n    dfs = func(r, c int) {\n        if r < 0 || r >= len(grid) || c < 0 || c >= len(grid[0]) || grid[r][c] != '1' {\n            return\n        }\n        grid[r][c] = '0'\n        dfs(r+1, c)\n        dfs(r-1, c)\n        dfs(r, c+1)\n        dfs(r, c-1)\n    }\n    for r := 0; r < len(grid); r++ {\n        for c := 0; c < len(grid[0]); c++ {\n            if grid[r][c] == '1' {\n                count++\n                dfs(r, c)\n            }\n        }\n    }\n    return count\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Standard flood fill traversal on connected components. Each unvisited '1' represents a new island. Sinking connected land prevents duplicate counting.",
                "invariants": "Every cell is converted from '1' to '0' at most once, ensuring exact O(M * N) runtime.",
                "brute_force": "Re-running global searches from each cell without marking visited produces infinite recursion loops.",
                "optimal_derivation": "In-place grid modification avoids O(M * N) auxiliary set allocation.",
                "dry_run": "Encounter (0,0)='1'. Count becomes 1. DFS explores (0,1), (1,0) etc. All set to '0'. Outer loops skip cells that are already '0'.",
                "edge_cases": ["Grid with no land (all '0')", "Grid with all land (single island)", "1x1 grid with '1' or '0'"],
                "pitfalls": ["Checking diagonals (problem explicitly specifies horizontally or vertically adjacent)"],
                "follow_ups": ["What if you cannot mutate the input grid? (Use a 2D boolean array or Union-Find / Disjoint Set)"],
            },
        ),

        # 12. DYNAMIC PROGRAMMING (LeetCode)
        DsaRecommendedProblem(
            id="lc-322",
            title="Coin Change",
            difficulty="Medium",
            topic="Dynamic Programming",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/coin-change/",
            similar_to="LeetCode 322: Coin Change (Unbounded Knapsack)",
            description=(
                "You are given an integer array `coins` representing coins of different denominations and an integer `amount` "
                "representing a total amount of money.\n\n"
                "Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up "
                "by any combination of the coins, return `-1`.\n\n"
                "You may assume that you have an infinite number of each kind of coin."
            ),
            examples=[
                DsaProblemExample(input="coins = [1,2,5], amount = 11", output="3", explanation="11 = 5 + 5 + 1"),
                DsaProblemExample(input="coins = [2], amount = 3", output="-1", explanation="Amount 3 cannot be formed with coin 2."),
                DsaProblemExample(input="coins = [1], amount = 0", output="0", explanation="Amount 0 requires 0 coins."),
            ],
            constraints=["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31 - 1", "0 <= amount <= 10^4"],
            hints=[
                "Greedy approach (picking the largest coin first) fails for denominations like coins=[1,3,4,5], amount=7 (greedy takes 5+1+1=3, optimal is 4+3=2).",
                "Define dp[i] as the minimum coins needed for amount i. Transition: dp[i] = min(dp[i], dp[i - c] + 1).",
            ],
            approach="Bottom-up 1D Dynamic Programming (Unbounded Knapsack). O(amount * len(coins)) time and O(amount) space.",
            time_complexity="O(A * C)",
            space_complexity="O(A)",
            starter_code={
                "python": "def coinChange(coins: list[int], amount: int) -> int:\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for a in range(1, amount + 1):\n        for c in coins:\n            if a - c >= 0:\n                dp[a] = min(dp[a], dp[a - c] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1\n",
                "javascript": "function coinChange(coins, amount) {\n    const dp = new Array(amount + 1).fill(Infinity);\n    dp[0] = 0;\n    for (let a = 1; a <= amount; a++) {\n        for (const c of coins) {\n            if (a - c >= 0) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n        }\n    }\n    return dp[amount] === Infinity ? -1 : dp[amount];\n}\n",
                "typescript": "function coinChange(coins: number[], amount: number): number {\n    const dp = new Array(amount + 1).fill(Infinity);\n    dp[0] = 0;\n    for (let a = 1; a <= amount; a++) {\n        for (const c of coins) {\n            if (a - c >= 0) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n        }\n    }\n    return dp[amount] === Infinity ? -1 : dp[amount];\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int coinChange(int[] coins, int amount) {\n        int[] dp = new int[amount + 1];\n        Arrays.fill(dp, amount + 1);\n        dp[0] = 0;\n        for (int a = 1; a <= amount; a++) {\n            for (int c : coins) {\n                if (a - c >= 0) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n            }\n        }\n        return dp[amount] > amount ? -1 : dp[amount];\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    int coinChange(vector<int>& coins, int amount) {\n        vector<int> dp(amount + 1, amount + 1);\n        dp[0] = 0;\n        for (int a = 1; a <= amount; a++) {\n            for (int c : coins) {\n                if (a - c >= 0) dp[a] = min(dp[a], dp[a - c] + 1);\n            }\n        }\n        return dp[amount] > amount ? -1 : dp[amount];\n    }\n};\n",
                "golang": "package main\n\nfunc coinChange(coins []int, amount int) int {\n    dp := make([]int, amount+1)\n    for i := 1; i <= amount; i++ {\n        dp[i] = amount + 1\n    }\n    dp[0] = 0\n    for a := 1; a <= amount; a++ {\n        for _, c := range coins {\n            if a-c >= 0 && dp[a-c]+1 < dp[a] {\n                dp[a] = dp[a-c] + 1\n            }\n        }\n    }\n    if dp[amount] > amount {\n        return -1\n    }\n    return dp[amount]\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Greedy fails because taking a larger coin can prevent an optimal combination of smaller coins. Solve subproblems bottom-up from 1 to amount.",
                "invariants": "dp[i] represents the absolute minimum coins needed to make sum i.",
                "brute_force": "Recursion tree exploring every coin branch takes O(S^N) exponential time.",
                "optimal_derivation": "dp[a] = min(dp[a - c] + 1) for all c in coins where a >= c. Initialized with dp[0] = 0.",
                "dry_run": "amount=4, coins=[1,3]. dp[0]=0. a=1: dp[1]=min(inf, dp[0]+1)=1. a=2: dp[2]=min(inf, dp[1]+1)=2. a=3: dp[3]=min(inf, dp[2]+1=3, dp[0]+1=1)=1. a=4: dp[4]=min(inf, dp[3]+1=2, dp[1]+1=2)=2.",
                "edge_cases": ["amount == 0 returns 0", "Coin denomination greater than amount", "No combination possible (return -1)"],
                "pitfalls": ["Assuming greedy works", "Integer overflow when initializing with INT_MAX in C++/Java (use amount + 1)"],
                "follow_ups": ["How would you count total number of combinations rather than minimum coins? (Coin Change II / LeetCode 518)"],
            },
        ),

        # 13. INTERVALS (LeetCode)
        DsaRecommendedProblem(
            id="lc-56",
            title="Merge Intervals",
            difficulty="Medium",
            topic="Intervals",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/merge-intervals/",
            similar_to="LeetCode 56: Merge Intervals",
            description=(
                "Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, "
                "and return an array of the non-overlapping intervals that cover all the intervals in the input."
            ),
            examples=[
                DsaProblemExample(input="intervals = [[1,3],[2,6],[8,10],[15,18]]", output="[[1,6],[8,10],[15,18]]", explanation="Since intervals [1,3] and [2,6] overlap, merge them into [1,6]."),
                DsaProblemExample(input="intervals = [[1,4],[4,5]]", output="[[1,5]]", explanation="Intervals [1,4] and [4,5] are considered overlapping."),
            ],
            constraints=["1 <= intervals.length <= 10^4", "intervals[i].length == 2", "0 <= start_i <= end_i <= 10^4"],
            hints=[
                "Sort intervals by start time.",
                "Iterate through sorted intervals: if current interval starts <= previous interval's end, merge by updating end to max(prev.end, curr.end).",
            ],
            approach="Sort by start time in O(N log N), then linear scan merging overlapping intervals in O(N) time.",
            time_complexity="O(N log N)",
            space_complexity="O(N)",
            starter_code={
                "python": "def merge(intervals: list[list[int]]) -> list[list[int]]:\n    intervals.sort(key=lambda x: x[0])\n    merged = []\n    for start, end in intervals:\n        if not merged or merged[-1][1] < start:\n            merged.append([start, end])\n        else:\n            merged[-1][1] = max(merged[-1][1], end)\n    return merged\n",
                "javascript": "function merge(intervals) {\n    intervals.sort((a, b) => a[0] - b[0]);\n    const merged = [];\n    for (const [start, end] of intervals) {\n        if (!merged.length || merged[merged.length - 1][1] < start) {\n            merged.push([start, end]);\n        } else {\n            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], end);\n        }\n    }\n    return merged;\n}\n",
                "typescript": "function merge(intervals: number[][]): number[][] {\n    intervals.sort((a, b) => a[0] - b[0]);\n    const merged: number[][] = [];\n    for (const [start, end] of intervals) {\n        if (!merged.length || merged[merged.length - 1][1] < start) {\n            merged.push([start, end]);\n        } else {\n            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], end);\n        }\n    }\n    return merged;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int[][] merge(int[][] intervals) {\n        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));\n        List<int[]> merged = new ArrayList<>();\n        for (int[] interval : intervals) {\n            if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < interval[0]) {\n                merged.add(interval);\n            } else {\n                merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], interval[1]);\n            }\n        }\n        return merged.toArray(new int[merged.size()][]);\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> merge(vector<vector<int>>& intervals) {\n        sort(intervals.begin(), intervals.end());\n        vector<vector<int>> merged;\n        for (auto& iv : intervals) {\n            if (merged.empty() || merged.back()[1] < iv[0]) {\n                merged.push_back(iv);\n            } else {\n                merged.back()[1] = max(merged.back()[1], iv[1]);\n            }\n        }\n        return merged;\n    }\n};\n",
                "golang": "package main\n\nimport (\n    \"sort\"\n)\n\nfunc merge(intervals [][]int) [][]int {\n    sort.Slice(intervals, func(i, j int) bool {\n        return intervals[i][0] < intervals[j][0]\n    })\n    merged := [][]int{}\n    for _, iv := range intervals {\n        if len(merged) == 0 || merged[len(merged)-1][1] < iv[0] {\n            merged = append(merged, iv)\n        } else if iv[1] > merged[len(merged)-1][1] {\n            merged[len(merged)-1][1] = iv[1]\n        }\n    }\n    return merged\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Sorting by start time ensures that any interval that could possibly merge with the current interval is adjacent.",
                "invariants": "The last interval in merged represents the latest merged cluster. If next interval starts after cluster end, it begins a new cluster.",
                "brute_force": "Repeated pairwise comparisons without sorting takes O(N^2) graph-connected component resolution.",
                "optimal_derivation": "Sort in O(N log N). Single pass O(N) linear merge.",
                "dry_run": "[[1,3],[2,6],[8,10]]: [1,3] added. [2,6] starts at 2 <= 3 -> merged to [1, max(3,6)] = [1,6]. [8,10] starts at 8 > 6 -> added as new interval [8,10].",
                "edge_cases": ["Single interval [[1,4]]", "Completely enclosed intervals [[1,10],[2,3]]", "Touching intervals [[1,4],[4,5]]"],
                "pitfalls": ["Overwriting end with curr.end instead of `max(prev.end, curr.end)`"],
                "follow_ups": ["How to insert a new interval into an already sorted list of non-overlapping intervals? (LeetCode 57: Insert Interval in O(N))"],
            },
        ),

        # 14. BACKTRACKING (LeetCode)
        DsaRecommendedProblem(
            id="lc-78",
            title="Subsets",
            difficulty="Medium",
            topic="Backtracking",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/subsets/",
            similar_to="LeetCode 78: Subsets",
            description=(
                "Given an integer array `nums` of unique elements, return all possible subsets (the power set).\n\n"
                "The solution set must not contain duplicate subsets. Return the solution in any order."
            ),
            examples=[
                DsaProblemExample(input="nums = [1,2,3]", output="[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]", explanation="All 2^3 = 8 subsets."),
                DsaProblemExample(input="nums = [0]", output="[[],[0]]", explanation="All 2^1 = 2 subsets."),
            ],
            constraints=["1 <= nums.length <= 10", "-10 <= nums[i] <= 10", "All the numbers of nums are unique."],
            hints=[
                "For each number, you have two choices: include it in the current subset or exclude it.",
                "Alternatively, loop through start index to len(nums), choose, recurse, and backtrack (un-choose).",
            ],
            approach="Backtracking state-space exploration generating 2^N subsets in O(N * 2^N) time.",
            time_complexity="O(N * 2^N)",
            space_complexity="O(N)",
            starter_code={
                "python": "def subsets(nums: list[int]) -> list[list[int]]:\n    res = []\n    def backtrack(start, path):\n        res.append(list(path))\n        for i in range(start, len(nums)):\n            path.append(nums[i])\n            backtrack(i + 1, path)\n            path.pop()\n    backtrack(0, [])\n    return res\n",
                "javascript": "function subsets(nums) {\n    const res = [];\n    function backtrack(start, path) {\n        res.push([...path]);\n        for (let i = start; i < nums.length; i++) {\n            path.push(nums[i]);\n            backtrack(i + 1, path);\n            path.pop();\n        }\n    }\n    backtrack(0, []);\n    return res;\n}\n",
                "typescript": "function subsets(nums: number[]): number[][] {\n    const res: number[][] = [];\n    function backtrack(start: number, path: number[]) {\n        res.push([...path]);\n        for (let i = start; i < nums.length; i++) {\n            path.push(nums[i]);\n            backtrack(i + 1, path);\n            path.pop();\n        }\n    }\n    backtrack(0, []);\n    return res;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public List<List<Integer>> subsets(int[] nums) {\n        List<List<Integer>> res = new ArrayList<>();\n        backtrack(0, nums, new ArrayList<>(), res);\n        return res;\n    }\n    private void backtrack(int start, int[] nums, List<Integer> path, List<List<Integer>> res) {\n        res.add(new ArrayList<>(path));\n        for (int i = start; i < nums.length; i++) {\n            path.add(nums[i]);\n            backtrack(i + 1, nums, path, res);\n            path.remove(path.size() - 1);\n        }\n    }\n}\n",
                "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> subsets(vector<int>& nums) {\n        vector<vector<int>> res;\n        vector<int> path;\n        backtrack(0, nums, path, res);\n        return res;\n    }\n    void backtrack(int start, vector<int>& nums, vector<int>& path, vector<vector<int>>& res) {\n        res.push_back(path);\n        for (int i = start; i < nums.size(); i++) {\n            path.push_back(nums[i]);\n            backtrack(i + 1, nums, path, res);\n            path.pop_back();\n        }\n    }\n};\n",
                "golang": "package main\n\nfunc subsets(nums []int) [][]int {\n    res := [][]int{}\n    var backtrack func(start int, path []int)\n    backtrack = func(start int, path []int) {\n        c := make([]int, len(path))\n        copy(c, path)\n        res = append(res, c)\n        for i := start; i < len(nums); i++ {\n            path = append(path, nums[i])\n            backtrack(i+1, path)\n            path = path[:len(path)-1]\n        }\n    }\n    backtrack(0, []int{})\n    return res\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Every node in the recursion tree represents a valid prefix subset. Recursion expands by trying each candidate and then removing it to explore alternative branches.",
                "invariants": "start index prevents re-using previous elements or creating permuted duplicates.",
                "brute_force": "Bitmask iteration from 0 to (2^N - 1) also achieves O(N * 2^N).",
                "optimal_derivation": "Backtracking avoids allocating intermediate sets, modifying a single path array in-place.",
                "dry_run": "nums=[1,2]: [] added. i=0: [1] added. i=1: [1,2] added. Backtrack pops 2, pops 1. i=1: [2] added. Total: [[],[1],[1,2],[2]].",
                "edge_cases": ["Array of length 1 [0] -> [[],[0]]", "Array of max length 10 -> 1024 subsets"],
                "pitfalls": ["Appending the mutable path reference instead of a copy or snapshot in languages like Python/JS/Java"],
                "follow_ups": ["What if the input contains duplicates and we must avoid duplicate subsets? (LeetCode 90: Subsets II - sort and skip `nums[i] == nums[i-1]`)"],
            },
        ),

        # 15. GREEDY (LeetCode)
        DsaRecommendedProblem(
            id="lc-55",
            title="Jump Game",
            difficulty="Medium",
            topic="Greedy",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/jump-game/",
            similar_to="LeetCode 55: Jump Game",
            description=(
                "You are given an integer array `nums`. You are initially positioned at the array's first index, "
                "and each element in the array represents your maximum jump length at that position.\n\n"
                "Return `true` if you can reach the last index, or `false` otherwise."
            ),
            examples=[
                DsaProblemExample(input="nums = [2,3,1,1,4]", output="true", explanation="Jump 1 step from index 0 to 1, then 3 steps to the last index."),
                DsaProblemExample(input="nums = [3,2,1,0,4]", output="false", explanation="You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index."),
            ],
            constraints=["1 <= nums.length <= 10^4", "0 <= nums[i] <= 10^5"],
            hints=[
                "Track the maximum index you can reach so far as you iterate through the array.",
                "If current index `i` is greater than `max_reachable`, you are stuck and can never progress further.",
            ],
            approach="Greedy tracking of maximum reachable index. O(N) linear time and O(1) space.",
            time_complexity="O(N)",
            space_complexity="O(1)",
            starter_code={
                "python": "def canJump(nums: list[int]) -> bool:\n    max_reach = 0\n    for i, jump in enumerate(nums):\n        if i > max_reach:\n            return False\n        max_reach = max(max_reach, i + jump)\n    return True\n",
                "javascript": "function canJump(nums) {\n    let maxReach = 0;\n    for (let i = 0; i < nums.length; i++) {\n        if (i > maxReach) return false;\n        maxReach = Math.max(maxReach, i + nums[i]);\n    }\n    return true;\n}\n",
                "typescript": "function canJump(nums: number[]): boolean {\n    let maxReach = 0;\n    for (let i = 0; i < nums.length; i++) {\n        if (i > maxReach) return false;\n        maxReach = Math.max(maxReach, i + nums[i]);\n    }\n    return true;\n}\n",
                "java": "class Solution {\n    public boolean canJump(int[] nums) {\n        int maxReach = 0;\n        for (int i = 0; i < nums.length; i++) {\n            if (i > maxReach) return false;\n            maxReach = Math.max(maxReach, i + nums[i]);\n        }\n        return true;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool canJump(vector<int>& nums) {\n        int max_reach = 0;\n        for (int i = 0; i < nums.size(); i++) {\n            if (i > max_reach) return false;\n            max_reach = max(max_reach, i + nums[i]);\n        }\n        return true;\n    }\n};\n",
                "golang": "package main\n\nfunc canJump(nums []int) bool {\n    maxReach := 0\n    for i, jump := range nums {\n        if i > maxReach {\n            return false\n        }\n        if i+jump > maxReach {\n            maxReach = i + jump\n        }\n    }\n    return true\n}\n",
            },
            step_by_step_teaching={
                "intuition": "You do not need to test every jump sequence. You only need to know the furthest boundary you can reach at any moment.",
                "invariants": "If index `i` <= `max_reach`, all indices from 0 to `i` are reachable.",
                "brute_force": "Backtracking or DP checking all jumps takes O(N^2) or O(2^N).",
                "optimal_derivation": "Greedy choice: at each step, extend max_reach = max(max_reach, i + nums[i]). If i > max_reach, return False immediately.",
                "dry_run": "nums=[2,3,1,1,4]: i=0 (reach=2). i=1 (reach=max(2, 1+3)=4 >= len-1) -> True.",
                "edge_cases": ["Single element array [0] -> True (already at destination)", "Starting with 0 in multi-element array [0, 2] -> False"],
                "pitfalls": ["Overcomplicating with dynamic programming when single greedy variable suffices"],
                "follow_ups": ["What is the minimum number of jumps to reach the last index? (LeetCode 45: Jump Game II in O(N))"],
            },
        ),

        # 16. BIT MANIPULATION (LeetCode)
        DsaRecommendedProblem(
            id="lc-136",
            title="Single Number",
            difficulty="Easy",
            topic="Bit Manipulation",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/single-number/",
            similar_to="LeetCode 136: Single Number",
            description=(
                "Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.\n\n"
                "You must implement a solution with a linear runtime complexity and use only constant extra space."
            ),
            examples=[
                DsaProblemExample(input="nums = [2,2,1]", output="1", explanation="1 appears only once."),
                DsaProblemExample(input="nums = [4,1,2,1,2]", output="4", explanation="4 appears once, others appear twice."),
                DsaProblemExample(input="nums = [1]", output="1", explanation="Single element array."),
            ],
            constraints=["1 <= nums.length <= 3 * 10^4", "-3 * 10^4 <= nums[i] <= 3 * 10^4", "Each element in the array appears twice except for one element which appears only once."],
            hints=[
                "XOR of zero and any number is that number: a ^ 0 = a.",
                "XOR of two identical numbers is zero: a ^ a = 0. XOR is commutative and associative.",
            ],
            approach="Bitwise XOR reduction. All pairs cancel to 0, leaving the single unique number in O(N) time and O(1) space.",
            time_complexity="O(N)",
            space_complexity="O(1)",
            starter_code={
                "python": "def singleNumber(nums: list[int]) -> int:\n    res = 0\n    for n in nums:\n        res ^= n\n    return res\n",
                "javascript": "function singleNumber(nums) {\n    let res = 0;\n    for (const n of nums) res ^= n;\n    return res;\n}\n",
                "typescript": "function singleNumber(nums: number[]): number {\n    let res = 0;\n    for (const n of nums) res ^= n;\n    return res;\n}\n",
                "java": "class Solution {\n    public int singleNumber(int[] nums) {\n        int res = 0;\n        for (int n : nums) res ^= n;\n        return res;\n    }\n}\n",
                "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int singleNumber(vector<int>& nums) {\n        int res = 0;\n        for (int n : nums) res ^= n;\n        return res;\n    }\n};\n",
                "golang": "package main\n\nfunc singleNumber(nums []int) int {\n    res := 0\n    for _, n := range nums {\n        res ^= n\n    }\n    return res\n}\n",
            },
            step_by_step_teaching={
                "intuition": "XORing any number with itself cancels it to 0. Since every number except one appears twice, cumulative XOR eliminates all paired numbers.",
                "invariants": "a ^ a = 0, a ^ 0 = a, and order of operations does not matter (commutative & associative).",
                "brute_force": "Hash map frequency counting takes O(N) space, violating the O(1) space constraint.",
                "optimal_derivation": "XOR accumulator takes exactly O(N) operations and 1 integer of memory.",
                "dry_run": "nums=[4, 1, 2, 1, 2]. 0 ^ 4 = 4. 4 ^ 1 ^ 2 ^ 1 ^ 2 = 4 ^ (1 ^ 1) ^ (2 ^ 2) = 4 ^ 0 ^ 0 = 4.",
                "edge_cases": ["Single element array [1]", "Negative numbers (-1 ^ -1 == 0)"],
                "pitfalls": ["Attempting arithmetic sum tricks that overflow"],
                "follow_ups": ["What if every element appears three times except for one? (LeetCode 137: Single Number II using bitwise state machine)"],
            },
        ),

        # 17. HACKERRANK GRAPH CHALLENGE
        DsaRecommendedProblem(
            id="hr-roads-libraries",
            title="Roads and Libraries",
            difficulty="Medium",
            topic="Graphs & Connected Components",
            platform="HackerRank",
            canonical_url="https://www.hackerrank.com/challenges/torque-and-development/problem",
            similar_to="HackerRank: Roads and Libraries",
            description=(
                "Determine the minimum cost to provide library access to all citizens of Hackerland.\n\n"
                "There are n cities numbered from 1 to n. The citizens can access a library if:\n"
                "- Their city contains a library.\n"
                "- They can travel by road from their city to another city containing a library.\n\n"
                "The cost of building a library is c_lib, and the cost of repairing a road is c_road."
            ),
            examples=[
                DsaProblemExample(
                    input="n = 3, c_lib = 2, c_road = 1, cities = [[1, 2], [3, 1], [2, 3]]",
                    output="4",
                    explanation="Build 1 library in city 1 (cost 2) and repair 2 roads (cost 2*1=2). Total cost = 4.",
                ),
            ],
            constraints=["1 <= n <= 10^5", "1 <= m <= min(10^5, n*(n-1)/2)", "1 <= c_road, c_lib <= 10^5"],
            hints=[
                "If c_lib <= c_road, it is always cheaper to build a library in every city (cost = n * c_lib).",
                "Otherwise, in each connected component of size V, build 1 library and (V - 1) roads.",
            ],
            approach="Graph connected components via BFS/DFS or Disjoint Set Union (DSU). O(V + E) time.",
            time_complexity="O(V + E)",
            space_complexity="O(V + E)",
            starter_code={
                "python": "def roadsAndLibraries(n: int, c_lib: int, c_road: int, cities: list[list[int]]) -> int:\n    if c_lib <= c_road:\n        return n * c_lib\n    adj = {i: [] for i in range(1, n + 1)}\n    for u, v in cities:\n        adj[u].append(v)\n        adj[v].append(u)\n    visited = set()\n    def dfs(node):\n        visited.add(node)\n        count = 1\n        for neighbor in adj[node]:\n            if neighbor not in visited:\n                count += dfs(neighbor)\n        return count\n    total_cost = 0\n    for city in range(1, n + 1):\n        if city not in visited:\n            comp_size = dfs(city)\n            total_cost += c_lib + (comp_size - 1) * c_road\n    return total_cost\n",
                "javascript": "function roadsAndLibraries(n, c_lib, c_road, cities) {\n    if (c_lib <= c_road) return n * c_lib;\n    const adj = Array.from({ length: n + 1 }, () => []);\n    for (const [u, v] of cities) {\n        adj[u].push(v);\n        adj[v].push(u);\n    }\n    const visited = new Uint8Array(n + 1);\n    function dfs(node) {\n        visited[node] = 1;\n        let count = 1;\n        for (const next of adj[node]) {\n            if (!visited[next]) count += dfs(next);\n        }\n        return count;\n    }\n    let totalCost = 0;\n    for (let i = 1; i <= n; i++) {\n        if (!visited[i]) {\n            const size = dfs(i);\n            totalCost += c_lib + (size - 1) * c_road;\n        }\n    }\n    return totalCost;\n}\n",
                "typescript": "function roadsAndLibraries(n: number, c_lib: number, c_road: number, cities: number[][]): number {\n    if (c_lib <= c_road) return n * c_lib;\n    const adj: number[][] = Array.from({ length: n + 1 }, () => []);\n    for (const [u, v] of cities) {\n        adj[u].push(v);\n        adj[v].push(u);\n    }\n    const visited = new Uint8Array(n + 1);\n    function dfs(node: number): number {\n        visited[node] = 1;\n        let count = 1;\n        for (const next of adj[node]) {\n            if (!visited[next]) count += dfs(next);\n        }\n        return count;\n    }\n    let totalCost = 0;\n    for (let i = 1; i <= n; i++) {\n        if (!visited[i]) {\n            const size = dfs(i);\n            totalCost += c_lib + (size - 1) * c_road;\n        }\n    }\n    return totalCost;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public static long roadsAndLibraries(int n, int c_lib, int c_road, List<List<Integer>> cities) {\n        if (c_lib <= c_road) return (long) n * c_lib;\n        List<List<Integer>> adj = new ArrayList<>();\n        for (int i = 0; i <= n; i++) adj.add(new ArrayList<>());\n        for (List<Integer> edge : cities) {\n            adj.get(edge.get(0)).add(edge.get(1));\n            adj.get(edge.get(1)).add(edge.get(0));\n        }\n        boolean[] visited = new boolean[n + 1];\n        long totalCost = 0;\n        for (int i = 1; i <= n; i++) {\n            if (!visited[i]) {\n                long compSize = dfs(i, adj, visited);\n                totalCost += c_lib + (compSize - 1) * (long) c_road;\n            }\n        }\n        return totalCost;\n    }\n    private static long dfs(int node, List<List<Integer>> adj, boolean[] visited) {\n        visited[node] = true;\n        long count = 1;\n        for (int neighbor : adj.get(node)) {\n            if (!visited[neighbor]) count += dfs(neighbor, adj, visited);\n        }\n        return count;\n    }\n}\n",
                "cpp": "#include <vector>\nusing namespace std;\n\nlong roadsAndLibraries(int n, int c_lib, int c_road, vector<vector<int>> cities) {\n    if (c_lib <= c_road) return (long)n * c_lib;\n    vector<vector<int>> adj(n + 1);\n    for (auto& edge : cities) {\n        adj[edge[0]].push_back(edge[1]);\n        adj[edge[1]].push_back(edge[0]);\n    }\n    vector<bool> visited(n + 1, false);\n    long total_cost = 0;\n    for (int i = 1; i <= n; i++) {\n        if (!visited[i]) {\n            long comp_size = 0;\n            vector<int> stack = {i};\n            visited[i] = true;\n            while (!stack.empty()) {\n                int u = stack.back(); stack.pop_back();\n                comp_size++;\n                for (int v : adj[u]) {\n                    if (!visited[v]) {\n                        visited[v] = true;\n                        stack.push_back(v);\n                    }\n                }\n            }\n            total_cost += c_lib + (comp_size - 1) * (long)c_road;\n        }\n    }\n    return total_cost;\n}\n",
                "golang": "package main\n\nfunc roadsAndLibraries(n int32, c_lib int32, c_road int32, cities [][]int32) int64 {\n    if c_lib <= c_road {\n        return int64(n) * int64(c_lib)\n    }\n    adj := make([][]int32, n+1)\n    for _, edge := range cities {\n        adj[edge[0]] = append(adj[edge[0]], edge[1])\n        adj[edge[1]] = append(adj[edge[1]], edge[0])\n    }\n    visited := make([]bool, n+1)\n    var totalCost int64 = 0\n    for i := int32(1); i <= n; i++ {\n        if !visited[i] {\n            compSize := int64(0)\n            stack := []int32{i}\n            visited[i] = true\n            for len(stack) > 0 {\n                u := stack[len(stack)-1]\n                stack = stack[:len(stack)-1]\n                compSize++\n                for _, v := range adj[u] {\n                    if !visited[v] {\n                        visited[v] = true\n                        stack = append(stack, v)\n                    }\n                }\n            }\n            totalCost += int64(c_lib) + (compSize-1)*int64(c_road)\n        }\n    }\n    return totalCost\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Every connected component needs at least 1 library. Roads within a component span it with a tree (V-1 edges). If c_lib <= c_road, simply build libraries everywhere.",
                "invariants": "A component with V vertices requires 1 library and (V - 1) edges to be connected.",
                "brute_force": "Kruskal's / Prim's algorithm works but is overkill; any spanning tree works since all road costs are uniform.",
                "optimal_derivation": "DFS/BFS counts component size in O(V + E).",
                "dry_run": "n=3, c_lib=2, c_road=1. Single component with 3 cities: cost = 2 + (3-1)*1 = 4.",
                "edge_cases": ["Disconnected isolated cities (each needs its own library)", "c_lib <= c_road (avoid building any roads)"],
                "pitfalls": ["32-bit integer overflow when calculating total cost for large N (use 64-bit int / long)"],
                "follow_ups": ["What if road costs vary between edges? (Minimum Spanning Tree / Kruskal's algorithm)"],
            },
        ),

        # 18. SLIDING WINDOW (LeetCode - Bounded Distinct Elements)
        DsaRecommendedProblem(
            id="dsa-p1",
            title="Max Contiguous Subarray with Bounded Distinct Elements",
            difficulty="Medium",
            topic="Sliding Window",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/longest-substring-without-repeating-characters/",
            similar_to="LeetCode 3: Longest Substring Without Repeating Characters & LeetCode 340",
            description="Given an array of integers nums and an integer k, return the length of the longest contiguous subarray containing at most k distinct elements.",
            examples=[
                DsaProblemExample(
                    input="nums = [1, 2, 1, 2, 3], k = 2",
                    output="4",
                    explanation="The longest valid subarray is [1, 2, 1, 2] with length 4.",
                ),
                DsaProblemExample(
                    input="nums = [1, 2, 3, 1, 2, 3], k = 1",
                    output="1",
                    explanation="Any single element subarray contains 1 distinct element.",
                ),
            ],
            constraints=["1 <= nums.length <= 10^5", "0 <= nums[i] <= 10^5", "1 <= k <= nums.length"],
            hints=[
                "Maintain a sliding window [left, right] and a hash map tracking element frequencies.",
                "Whenever the map size exceeds k, shrink the window from the left until map size is <= k.",
            ],
            approach="Use a two-pointer sliding window with an element frequency hash map to achieve O(N) time and O(K) space.",
            time_complexity="O(N)",
            space_complexity="O(K)",
            starter_code={
                "python": "def maxSubarrayLength(nums: list[int], k: int) -> int:\n    left = 0\n    max_len = 0\n    counts = {}\n    for right, val in enumerate(nums):\n        counts[val] = counts.get(val, 0) + 1\n        while len(counts) > k:\n            counts[nums[left]] -= 1\n            if counts[nums[left]] == 0:\n                del counts[nums[left]]\n            left += 1\n        max_len = max(max_len, right - left + 1)\n    return max_len\n",
                "javascript": "function maxSubarrayLength(nums, k) {\n    let left = 0, maxLen = 0;\n    const counts = new Map();\n    for (let right = 0; right < nums.length; right++) {\n        counts.set(nums[right], (counts.get(nums[right]) || 0) + 1);\n        while (counts.size > k) {\n            const c = counts.get(nums[left]) - 1;\n            if (c === 0) counts.delete(nums[left]);\n            else counts.set(nums[left], c);\n            left++;\n        }\n        maxLen = Math.max(maxLen, right - left + 1);\n    }\n    return maxLen;\n}\n",
                "typescript": "function maxSubarrayLength(nums: number[], k: number): number {\n    let left = 0, maxLen = 0;\n    const counts = new Map<number, number>();\n    for (let right = 0; right < nums.length; right++) {\n        counts.set(nums[right], (counts.get(nums[right]) || 0) + 1);\n        while (counts.size > k) {\n            const c = counts.get(nums[left])! - 1;\n            if (c === 0) counts.delete(nums[left]);\n            else counts.set(nums[left], c);\n            left++;\n        }\n        maxLen = Math.max(maxLen, right - left + 1);\n    }\n    return maxLen;\n}\n",
                "java": "import java.util.*;\n\nclass Solution {\n    public int maxSubarrayLength(int[] nums, int k) {\n        int left = 0, maxLen = 0;\n        Map<Integer, Integer> counts = new HashMap<>();\n        for (int right = 0; right < nums.length; right++) {\n            counts.put(nums[right], counts.getOrDefault(nums[right], 0) + 1);\n            while (counts.size() > k) {\n                counts.put(nums[left], counts.get(nums[left]) - 1);\n                if (counts.get(nums[left]) == 0) counts.remove(nums[left]);\n                left++;\n            }\n            maxLen = Math.max(maxLen, right - left + 1);\n        }\n        return maxLen;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <unordered_map>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxSubarrayLength(vector<int>& nums, int k) {\n        int left = 0, maxLen = 0;\n        unordered_map<int, int> counts;\n        for (int right = 0; right < nums.size(); right++) {\n            counts[nums[right]]++;\n            while (counts.size() > k) {\n                counts[nums[left]]--;\n                if (counts[nums[left]] == 0) counts.erase(nums[left]);\n                left++;\n            }\n            maxLen = max(maxLen, right - left + 1);\n        }\n        return maxLen;\n    }\n};\n",
                "golang": "package main\n\nfunc maxSubarrayLength(nums []int, k int) int {\n    left := 0\n    maxLen := 0\n    counts := make(map[int]int)\n    for right, val := range nums {\n        counts[val]++\n        for len(counts) > k {\n            counts[nums[left]]--\n            if counts[nums[left]] == 0 {\n                delete(counts, nums[left])\n            }\n            left++\n        }\n        if right - left + 1 > maxLen {\n            maxLen = right - left + 1\n        }\n    }\n    return maxLen\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Maintain a dynamic window [left, right] that expands greedily with right. The moment distinct elements exceed k, shrink left until invariant holds.",
                "invariants": "The subarray nums[left..right] always contains at most k distinct elements.",
                "brute_force": "Check every possible subarray (O(N^2)) and count distinct elements (O(N)), leading to O(N^3) total time.",
                "optimal_derivation": "Both pointers move monotonically forward from 0 to N. Each element enters the hash map once and leaves once: O(N) time.",
                "dry_run": "nums=[1,2,1,2,3], k=2. Window expands to [1,2,1,2] (size 4, 2 distinct). When 3 arrives, window has 3 distinct, left advances until only {2, 3} remain.",
                "edge_cases": ["k >= nums.length (entire array valid)", "k == 1 (all same elements)", "empty or single element array"],
                "pitfalls": ["Forgetting to delete keys from the frequency map when count hits 0 (len(map) will remain too high)"],
                "follow_ups": ["Can we solve this in O(1) space if the alphabet or integer range is bounded to [1, 256]?"],
            },
        ),

        # 19. GRAPH BFS / DFS (LeetCode - Island Perimeter)
        DsaRecommendedProblem(
            id="dsa-p2",
            title="Island Perimeter and River Network Diameter",
            difficulty="Medium",
            topic="Graph BFS / DFS",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/island-perimeter/",
            similar_to="LeetCode 200: Number of Islands & LeetCode 695: Max Area of Island",
            description="You are given an m x n binary grid where 1 represents land and 0 represents water. An island is formed by horizontally or vertically adjacent lands. Return the maximum perimeter of any single connected island in the grid.",
            examples=[
                DsaProblemExample(
                    input="grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]",
                    output="12",
                    explanation="The top connected island has perimeter 12.",
                )
            ],
            constraints=["m == grid.length", "n == grid[i].length", "1 <= m, n <= 100"],
            hints=[
                "Traverse every unvisited 1 using Breadth-First Search (BFS) or Depth-First Search (DFS).",
                "For each cell in the island, its contribution to perimeter is 4 minus the number of valid land neighbors.",
            ],
            approach="Standard grid flood-fill traversal. Compute each cell's exposed perimeter boundaries directly.",
            time_complexity="O(M * N)",
            space_complexity="O(M * N)",
            starter_code={
                "python": "def maxIslandPerimeter(grid: list[list[int]]) -> int:\n    rows, cols = len(grid), len(grid[0])\n    visited = set()\n    max_p = 0\n    def dfs(r, c):\n        visited.add((r, c))\n        p = 0\n        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:\n            nr, nc = r + dr, c + dc\n            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:\n                if (nr, nc) not in visited:\n                    p += dfs(nr, nc)\n            else:\n                p += 1\n        return p\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == 1 and (r, c) not in visited:\n                max_p = max(max_p, dfs(r, c))\n    return max_p\n",
                "javascript": "function maxIslandPerimeter(grid) {\n    const rows = grid.length, cols = grid[0].length;\n    const visited = Array.from({ length: rows }, () => new Uint8Array(cols));\n    let maxP = 0;\n    function dfs(r, c) {\n        visited[r][c] = 1;\n        let p = 0;\n        for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {\n            const nr = r + dr, nc = c + dc;\n            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] === 1) {\n                if (!visited[nr][nc]) p += dfs(nr, nc);\n            } else {\n                p += 1;\n            }\n        }\n        return p;\n    }\n    for (let r = 0; r < rows; r++) {\n        for (let c = 0; c < cols; c++) {\n            if (grid[r][c] === 1 && !visited[r][c]) maxP = Math.max(maxP, dfs(r, c));\n        }\n    }\n    return maxP;\n}\n",
                "typescript": "function maxIslandPerimeter(grid: number[][]): number {\n    const rows = grid.length, cols = grid[0].length;\n    const visited = Array.from({ length: rows }, () => new Uint8Array(cols));\n    let maxP = 0;\n    function dfs(r: number, c: number): number {\n        visited[r][c] = 1;\n        let p = 0;\n        for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {\n            const nr = r + dr, nc = c + dc;\n            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] === 1) {\n                if (!visited[nr][nc]) p += dfs(nr, nc);\n            } else {\n                p += 1;\n            }\n        }\n        return p;\n    }\n    for (let r = 0; r < rows; r++) {\n        for (let c = 0; c < cols; c++) {\n            if (grid[r][c] === 1 && !visited[r][c]) maxP = Math.max(maxP, dfs(r, c));\n        }\n    }\n    return maxP;\n}\n",
                "java": "class Solution {\n    public int maxIslandPerimeter(int[][] grid) {\n        int rows = grid.length, cols = grid[0].length;\n        boolean[][] visited = new boolean[rows][cols];\n        int maxP = 0;\n        for (int r = 0; r < rows; r++) {\n            for (int c = 0; c < cols; c++) {\n                if (grid[r][c] == 1 && !visited[r][c]) {\n                    maxP = Math.max(maxP, dfs(grid, r, c, visited));\n                }\n            }\n        }\n        return maxP;\n    }\n    private int dfs(int[][] grid, int r, int c, boolean[][] visited) {\n        visited[r][c] = true;\n        int p = 0;\n        int[][] dirs = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};\n        for (int[] d : dirs) {\n            int nr = r + d[0], nc = c + d[1];\n            if (nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length && grid[nr][nc] == 1) {\n                if (!visited[nr][nc]) p += dfs(grid, nr, nc, visited);\n            } else {\n                p += 1;\n            }\n        }\n        return p;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxIslandPerimeter(vector<vector<int>>& grid) {\n        int rows = grid.size(), cols = grid[0].size();\n        vector<vector<bool>> visited(rows, vector<bool>(cols, false));\n        int maxP = 0;\n        for (int r = 0; r < rows; r++) {\n            for (int c = 0; c < cols; c++) {\n                if (grid[r][c] == 1 && !visited[r][c]) {\n                    maxP = max(maxP, dfs(grid, r, c, visited));\n                }\n            }\n        }\n        return maxP;\n    }\n    int dfs(vector<vector<int>>& grid, int r, int c, vector<vector<bool>>& visited) {\n        visited[r][c] = true;\n        int p = 0;\n        int dirs[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};\n        for (auto& d : dirs) {\n            int nr = r + d[0], nc = c + d[1];\n            if (nr >= 0 && nr < grid.size() && nc >= 0 && nc < grid[0].size() && grid[nr][nc] == 1) {\n                if (!visited[nr][nc]) p += dfs(grid, nr, nc, visited);\n            } else {\n                p += 1;\n            }\n        }\n        return p;\n    }\n};\n",
                "golang": "package main\n\nfunc maxIslandPerimeter(grid [][]int) int {\n    rows, cols := len(grid), len(grid[0])\n    visited := make([][]bool, rows)\n    for i := range visited { visited[i] = make([]bool, cols) }\n    maxP := 0\n    var dfs func(r, c int) int\n    dfs = func(r, c int) int {\n        visited[r][c] = true\n        p := 0\n        dirs := [][]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}\n        for _, d := range dirs {\n            nr, nc := r+d[0], c+d[1]\n            if nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 1 {\n                if !visited[nr][nc] { p += dfs(nr, nc) }\n            } else {\n                p += 1\n            }\n        }\n        return p\n    }\n    for r := 0; r < rows; r++ {\n        for c := 0; c < cols; c++ {\n            if grid[r][c] == 1 && !visited[r][c] {\n                val := dfs(r, c)\n                if val > maxP { maxP = val }\n            }\n        }\n    }\n    return maxP\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Every boundary between a land cell and a water cell (or grid boundary) contributes 1 unit to perimeter.",
                "invariants": "A land cell has 4 potential perimeter edges. Each orthogonal land neighbor reduces the perimeter contribution by 1.",
                "brute_force": "Visit all cells, and for each cell count how many of 4 sides are water or out of bounds.",
                "optimal_derivation": "Flood fill (DFS or BFS) finds connected components in O(M*N) time, keeping track of visited cells.",
                "dry_run": "A single isolated 1 cell: all 4 sides are out of bounds/water -> perimeter = 4. Two adjacent cells [1, 1]: each cell has 3 exposed sides -> perimeter = 6.",
                "edge_cases": ["Grid with all 0s (perimeter = 0)", "Single cell grid [[1]] (perimeter = 4)", "Grid with holes/lakes"],
                "pitfalls": ["Overcounting perimeter when two cells touch: each shared edge removes 2 from the combined perimeter (1 from each cell)"],
                "follow_ups": ["How to handle lakes inside the island that should not count towards external perimeter?"],
            },
        ),

        # 20. DYNAMIC PROGRAMMING (LeetCode - Stock Trading with Fee)
        DsaRecommendedProblem(
            id="dsa-p3",
            title="Stock Trading with Transaction Cooldown and Fee",
            difficulty="Medium",
            topic="Dynamic Programming",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/",
            similar_to="LeetCode 309: Best Time to Buy and Sell Stock with Cooldown",
            description="You are given an array prices where prices[i] is the price of a given stock on the ith day, and an integer fee representing a transaction fee. Find the maximum profit you can achieve. You may complete as many transactions as you like, but you cannot engage in multiple transactions simultaneously, and you must pay the fee for each transaction.",
            examples=[
                DsaProblemExample(
                    input="prices = [1, 3, 2, 8, 4, 9], fee = 2",
                    output="8",
                    explanation="Maximum profit = ((8 - 1) - 2) + ((9 - 4) - 2) = 5 + 3 = 8.",
                )
            ],
            constraints=["1 <= prices.length <= 5 * 10^4", "1 <= prices[i] <= 5 * 10^4", "0 <= fee <= 10^4"],
            hints=[
                "Define two states for each day: 'hold' (holding stock) and 'cash' (not holding stock).",
                "State transitions: cash = max(cash, hold + prices[i] - fee), hold = max(hold, cash_prev - prices[i]).",
            ],
            approach="State machine DP with 2 variables. Space can be compressed from O(N) to O(1).",
            time_complexity="O(N)",
            space_complexity="O(1)",
            starter_code={
                "python": "def maxProfit(prices: list[int], fee: int) -> int:\n    cash = 0\n    hold = -prices[0]\n    for p in prices[1:]:\n        cash = max(cash, hold + p - fee)\n        hold = max(hold, cash - p)\n    return cash\n",
                "javascript": "function maxProfit(prices, fee) {\n    let cash = 0, hold = -prices[0];\n    for (let i = 1; i < prices.length; i++) {\n        cash = Math.max(cash, hold + prices[i] - fee);\n        hold = Math.max(hold, cash - prices[i]);\n    }\n    return cash;\n}\n",
                "typescript": "function maxProfit(prices: number[], fee: number): number {\n    let cash = 0, hold = -prices[0];\n    for (let i = 1; i < prices.length; i++) {\n        cash = Math.max(cash, hold + prices[i] - fee);\n        hold = Math.max(hold, cash - prices[i]);\n    }\n    return cash;\n}\n",
                "java": "class Solution {\n    public int maxProfit(int[] prices, int fee) {\n        int cash = 0, hold = -prices[0];\n        for (int i = 1; i < prices.length; i++) {\n            cash = Math.max(cash, hold + prices[i] - fee);\n            hold = Math.max(hold, cash - prices[i]);\n        }\n        return cash;\n    }\n}\n",
                "cpp": "#include <vector>\n#include <algorithm>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxProfit(vector<int>& prices, int fee) {\n        int cash = 0, hold = -prices[0];\n        for (size_t i = 1; i < prices.size(); i++) {\n            cash = max(cash, hold + prices[i] - fee);\n            hold = max(hold, cash - prices[i]);\n        }\n        return cash;\n    }\n};\n",
                "golang": "package main\n\nfunc maxProfit(prices []int, fee int) int {\n    cash, hold := 0, -prices[0]\n    for i := 1; i < len(prices); i++ {\n        if hold + prices[i] - fee > cash {\n            cash = hold + prices[i] - fee\n        }\n        if cash - prices[i] > hold {\n            hold = cash - prices[i]\n        }\n    }\n    return cash\n}\n",
            },
            step_by_step_teaching={
                "intuition": "At the end of any day, you are in either of two mutually exclusive states: holding a stock or holding cash. The optimal decision on day i only depends on state at day i-1.",
                "invariants": "cash: max profit achievable on day i without stock. hold: max profit achievable on day i while holding stock.",
                "brute_force": "Branching recursion with choice to Buy, Sell, or Hold: O(2^N) exponential time.",
                "optimal_derivation": "State machine DP. cash = max(cash, hold + price - fee); hold = max(hold, cash - price). Runs in O(N) time and O(1) space.",
                "dry_run": "prices=[1,3,2,8], fee=2. Day 0: cash=0, hold=-1. Day 1 (p=3): cash=max(0,-1+3-2)=0, hold=max(-1, 0-3)=-1. Day 3 (p=8): cash=max(0, -1+8-2)=5.",
                "edge_cases": ["Monotonically decreasing prices (profit should be 0)", "Fee larger than any price swing", "Single day array"],
                "pitfalls": ["Deducting the fee twice (on buy and on sell)"],
                "follow_ups": ["What if there is a 1-day cooldown after selling before you can buy again? (LeetCode 309)"],
            },
        ),

        # 21. TREES & RECURSION (LeetCode - Lowest Common Ancestor)
        DsaRecommendedProblem(
            id="dsa-p4",
            title="Validate Lowest Ancestral Dependency Path",
            difficulty="Medium",
            topic="Trees & Recursion",
            platform="LeetCode",
            canonical_url="https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/",
            similar_to="LeetCode 236: Lowest Common Ancestor of a Binary Tree",
            description="Given the root of a binary tree and two nodes p and q, find the lowest common ancestor (LCA) node of the two given nodes in the tree.",
            examples=[
                DsaProblemExample(
                    input="root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1",
                    output="3",
                    explanation="The LCA of nodes 5 and 1 is 3.",
                )
            ],
            constraints=["Number of nodes is in [2, 10^5]", "-10^9 <= Node.val <= 10^9", "All Node.val are unique"],
            hints=[
                "Recursive post-order traversal: check if left subtree and right subtree contain p or q.",
                "If both subtrees return non-null, the current root is the LCA.",
            ],
            approach="Bottom-up recursive post-order traversal returning matched target references.",
            time_complexity="O(N)",
            space_complexity="O(H)",
            starter_code={
                "python": "# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, x):\n#         self.val = x\n#         self.left = None\n#         self.right = None\n\ndef lowestCommonAncestor(root, p, q):\n    if not root or root == p or root == q:\n        return root\n    left = lowestCommonAncestor(root.left, p, q)\n    right = lowestCommonAncestor(root.right, p, q)\n    if left and right:\n        return root\n    return left or right\n",
                "javascript": "function lowestCommonAncestor(root, p, q) {\n    if (!root || root === p || root === q) return root;\n    const left = lowestCommonAncestor(root.left, p, q);\n    const right = lowestCommonAncestor(root.right, p, q);\n    if (left && right) return root;\n    return left || right;\n}\n",
                "typescript": "function lowestCommonAncestor(root: any, p: any, q: any): any {\n    if (!root || root === p || root === q) return root;\n    const left = lowestCommonAncestor(root.left, p, q);\n    const right = lowestCommonAncestor(root.right, p, q);\n    if (left && right) return root;\n    return left || right;\n}\n",
                "java": "class Solution {\n    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n        if (root == null || root == p || root == q) return root;\n        TreeNode left = lowestCommonAncestor(root.left, p, q);\n        TreeNode right = lowestCommonAncestor(root.right, p, q);\n        if (left != null && right != null) return root;\n        return left != null ? left : right;\n    }\n}\n",
                "cpp": "class Solution {\npublic:\n    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {\n        if (!root || root == p || root == q) return root;\n        TreeNode* left = lowestCommonAncestor(root->left, p, q);\n        TreeNode* right = lowestCommonAncestor(root->right, p, q);\n        if (left && right) return root;\n        return left ? left : right;\n    }\n};\n",
                "golang": "package main\n\nfunc lowestCommonAncestor(root, p, q *TreeNode) *TreeNode {\n    if root == nil || root == p || root == q {\n        return root\n    }\n    left := lowestCommonAncestor(root.Left, p, q)\n    right := lowestCommonAncestor(root.Right, p, q)\n    if left != nil && right != nil {\n        return root\n    }\n    if left != nil {\n        return left\n    }\n    return right\n}\n",
            },
            step_by_step_teaching={
                "intuition": "Post-order bottom-up search. If current node is p or q, bubble it up. If left and right subtrees each return a target, the current node is their lowest common ancestor.",
                "invariants": "Returns null if neither p nor q is in the subtree. Returns the node if exactly one is present. Returns the LCA if both are present.",
                "brute_force": "Find the root-to-node path for p and q (storing parent pointers or path vectors) and find the last common node. Takes O(N) space and multiple traversals.",
                "optimal_derivation": "Single post-order traversal in O(N) time and O(H) recursion stack space.",
                "dry_run": "root=3, p=5, q=1. Left branch returns 5. Right branch returns 1. Since left and right both non-null, root 3 returns itself.",
                "edge_cases": ["One node is the ancestor of the other (e.g. p is root, q is child: returns p)", "p and q at leaf nodes on opposite ends"],
                "pitfalls": ["Assuming the tree is a Binary Search Tree (this is a general Binary Tree where values are not ordered)"],
                "follow_ups": ["How does the solution change if the tree is a Binary Search Tree (BST)? (LeetCode 235: compare node values in O(H) time without recursion)"],
            },
        ),
    ]
