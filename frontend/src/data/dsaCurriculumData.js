// Grounded DSA Curriculum and Masterclass Lessons for CareerVerse AI
// Provides authentic, topic-specific educational content across key DSA patterns.

export const DSA_PATTERN_GROUPS = [
  { id: "hash-maps", name: "Hash Maps & Sets", count: 3, icon: "Database" },
  { id: "two-pointers", name: "Two Pointers", count: 2, icon: "GitCommit" },
  { id: "sliding-window", name: "Sliding Window", count: 1, icon: "Sliders" },
  { id: "binary-search", name: "Binary Search", count: 2, icon: "Search" },
  { id: "trees", name: "Trees & Binary Search Trees", count: 1, icon: "GitFork" },
  { id: "graphs", name: "Graphs (BFS / DFS)", count: 2, icon: "Network" },
  { id: "dynamic-programming", name: "Dynamic Programming", count: 3, icon: "Layers" },
  { id: "prefix-sums", name: "Prefix Sums", count: 1, icon: "BarChart" },
  { id: "monotonic-stack", name: "Monotonic Stacks & Queues", count: 2, icon: "Stack" },
  { id: "linked-lists", name: "Linked Lists", count: 2, icon: "Link" },
  { id: "intervals", name: "Sorting & Intervals", count: 1, icon: "Calendar" },
  { id: "backtracking", name: "Recursion & Backtracking", count: 2, icon: "Cpu" },
];

export const CURATED_DSA_LESSONS = [
  {
    id: "two-sum",
    title: "Two Sum",
    subtitle: "Complement Lookup & Hash Map Invariant",
    topic: "Hash maps and sets",
    pattern_group: "hash-maps",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/two-sum/",
    status_type: "solved",
    learning_objectives: [
      "Replace quadratic O(N²) nested searches with an amortized O(N) single-pass lookup.",
      "Understand the complement mathematical invariant: if x + y = target, then y = target - x.",
      "Avoid common pitfalls such as using the same array index twice or mishandling duplicate values.",
      "Evaluate time and space trade-offs between hash table auxiliary memory and sorted two-pointer approaches."
    ],
    prerequisites: [
      { name: "Hash Tables", detail: "Amortized O(1) key lookup and insertion based on hash codes." },
      { name: "Array Traversal", detail: "Iterating through contiguous memory with index tracking." }
    ],
    problem_statement: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
    examples: [
      {
        input: "nums = [2, 7, 11, 15], target = 9",
        output: "[0, 1]",
        explanation: "Because nums[0] + nums[1] == 2 + 7 == 9, we return [0, 1]."
      },
      {
        input: "nums = [3, 2, 4], target = 6",
        output: "[1, 2]",
        explanation: "Because nums[1] + nums[2] == 2 + 4 == 6, we return [1, 2]."
      },
      {
        input: "nums = [3, 3], target = 6",
        output: "[0, 1]",
        explanation: "Because nums[0] + nums[1] == 3 + 3 == 6, we return [0, 1]."
      }
    ],
    constraints: [
      "2 <= nums.length <= 10^4 (An O(N²) approach requires ~10^8 operations, which will cause Time Limit Exceeded).",
      "-10^9 <= nums[i] <= 10^9 (Values can be negative; do not assume nums[i] < target).",
      "-10^9 <= target <= 10^9",
      "Only one valid answer exists."
    ],
    intuition: "Instead of asking 'for this number, does any future number complete the sum?', flip the question to: 'have I already seen the number needed to complete this sum?'\n\nFor every element x, its necessary partner is complement = target - x. By storing each visited element and its index in a hash map as we iterate, we can check if complement exists in O(1) amortized time before adding the current element to the map.",
    visual_trace: {
      description: "Step-by-step state trace for nums = [2, 7, 11, 15] and target = 9:",
      steps: [
        {
          step: 1,
          index: 0,
          current_num: 2,
          complement: "9 - 2 = 7",
          lookup_result: "7 not in seen map",
          seen_state: "{ 2: 0 }",
          explanation: "At index 0, number is 2. Complement is 7. Map is empty, so 7 is not found. Store {2: 0} for future lookups."
        },
        {
          step: 2,
          index: 1,
          current_num: 7,
          complement: "9 - 7 = 2",
          lookup_result: "2 FOUND in seen map at index 0!",
          seen_state: "{ 2: 0 }",
          explanation: "At index 1, number is 7. Complement is 2. 2 is already stored at index 0! Return [0, 1] immediately."
        }
      ]
    },
    baseline_solution: {
      name: "Brute-Force Nested Pair Search",
      complexity: "Time: O(N²) | Space: O(1)",
      description: "Checks every pair (i, j) with two nested loops. Redundant work occurs because previous elements are re-scanned repeatedly without memory.",
      code: `def two_sum_brute(nums: list[int], target: int) -> list[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []`
    },
    optimal_solution: {
      name: "One-Pass Hash Map Complement Lookup",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Maintains an auxiliary hash map tracking { value: index }. A single linear scan solves the problem in amortized O(N) time.",
      python_code: `def twoSum(nums: list[int], target: int) -> list[int]:
    # seen stores { number_value: index_where_it_appeared }
    seen = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        # Check if the needed partner was already visited
        if complement in seen:
            return [seen[complement], i]
        # Register current number for subsequent elements
        seen[num] = i
        
    return []`,
      javascript_code: `function twoSum(nums, target) {
    // Map stores number => index
    const seen = new Map();
    
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (seen.has(complement)) {
            return [seen.get(complement), i];
        }
        seen.set(nums[i], i);
    }
    return [];
}`,
      line_by_line: [
        {
          line: "seen = {}",
          explanation: "Initializes an empty dictionary to store previous numbers as keys and their 0-indexed positions as values."
        },
        {
          line: "complement = target - num",
          explanation: "Computes the exact counterpart needed to sum to target. For instance, if target is 9 and current num is 7, complement is 2."
        },
        {
          line: "if complement in seen:",
          explanation: "Performs an O(1) average lookup in Python's hash table. If present, we have found our pair."
        },
        {
          line: "return [seen[complement], i]",
          explanation: "Returns the earlier element's index first, followed by the current index. This guarantees indices are distinct."
        },
        {
          line: "seen[num] = i",
          explanation: "Inserts the current number AFTER checking the complement. This prevents an element from pairing with itself (e.g. target=6, nums=[3, 4])."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — We traverse the list containing N elements exactly once. Each lookup in the hash table costs O(1) amortized time.",
      space: "O(N) — In the worst case, we store up to N - 1 elements in the hash map before finding the matching pair."
    },
    edge_cases: [
      {
        case: "Same element used twice",
        risk: "If target = 6 and nums = [3, 4], a naive lookup might pair 3 with itself if stored before lookup.",
        mitigation: "Always check for the complement in the hash table BEFORE inserting the current element."
      },
      {
        case: "Duplicate values in input",
        risk: "If nums = [3, 3] and target = 6, inserting both might overwrite indices.",
        mitigation: "When the second 3 is encountered, the first 3 is already in the map and immediately satisfies the condition, returning [0, 1] before any key collision occurs."
      },
      {
        case: "Negative integers",
        risk: "Assumption that complement < target fails when numbers are negative (e.g. target = -5, nums = [-2, -3]).",
        mitigation: "Algebraic formula target - num works universally across negative and positive integers without special branches."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why do we check 'if complement in seen' BEFORE executing 'seen[num] = i'?",
        options: [
          "To optimize Python memory allocation.",
          "To prevent an element from matching with itself when target equals 2 * num.",
          "Because hash maps cannot store duplicate keys in any programming language.",
          "To keep the keys in ascending numerical order."
        ],
        correct_index: 1,
        explanation: "If you insert 'seen[num] = i' first, then for nums = [3, 1] and target = 6, complement is 6 - 3 = 3. Checking the map would find the 3 at index 0 that you just added, incorrectly returning [0, 0] instead of a valid pair of two distinct elements."
      },
      trace_prediction: {
        question: "For nums = [11, 15, 2, 7] and target = 9, what will the 'seen' map contain immediately BEFORE index 3 (value 7) is evaluated?",
        options: [
          "{ 11: 0, 15: 1, 2: 2 }",
          "{ 2: 2 }",
          "{ 9: 0, 7: 1 }",
          "{ 11: 0, 15: 1 }"
        ],
        correct_index: 0,
        explanation: "Indices 0 (11), 1 (15), and 2 (2) failed their complement lookups and were added to the map. Thus, before evaluating index 3, the map contains { 11: 0, 15: 1, 2: 2 }."
      },
      sandbox_test_cases: [
        { input: "nums = [2, 7, 11, 15], target = 9", expected: "[0, 1]" },
        { input: "nums = [3, 2, 4], target = 6", expected: "[1, 2]" },
        { input: "nums = [3, 3], target = 6", expected: "[0, 1]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Two Sum II (Input Array Is Sorted)",
      question: "What if the input array is already sorted in ascending order and you are restricted to O(1) auxiliary space (no hash map allowed)?",
      approach_shift: "Use the Two-Pointer convergence technique: place left = 0 and right = n - 1. If nums[left] + nums[right] > target, decrease right. If sum < target, increase left. This achieves O(N) time with strictly O(1) extra space."
    },
    verified_resources: [
      {
        title: "LeetCode #1: Two Sum Official Problem",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/two-sum/",
        type: "Problem Specification",
        summary: "The definitive problem statement, system constraints, and official submission platform."
      },
      {
        title: "Tech Interview Handbook: Array & Hash Table Patterns",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/array/",
        type: "Pattern Blueprint",
        summary: "Corner cases, memory invariants, and trade-offs between hash table lookups and two-pointer sorted scans."
      },
      {
        title: "NeetCode 150: Arrays & Hashing Roadmap",
        publisher: "NeetCode.io",
        url: "https://neetcode.io/roadmap",
        type: "Curriculum Guide",
        summary: "Structured progression from Two Sum to Group Anagrams and Top K Frequent Elements."
      }
    ]
  },

  {
    id: "longest-substring-without-repeating-characters",
    title: "Longest Substring Without Repeating Characters",
    subtitle: "Dynamic Window Expansion & Contraction",
    topic: "Sliding window",
    pattern_group: "sliding-window",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
    status_type: "attempted",
    learning_objectives: [
      "Master the dynamic sliding window pattern where boundaries expand and contract based on validity.",
      "Track last-seen character indices to perform O(1) left-pointer jumps rather than incremental shifts.",
      "Differentiate between contiguous substrings (sliding window) and non-contiguous subsequences (DP/backtracking).",
      "Analyze space complexity when the alphabet is bounded (ASCII vs Unicode)."
    ],
    prerequisites: [
      { name: "Two Pointers", detail: "Maintaining two moving indices [left, right] representing a valid slice." },
      { name: "Character Hashing", detail: "Using a dictionary or direct-address array to record character occurrences." }
    ],
    problem_statement: "Given a string s, find the length of the longest substring without duplicate characters.",
    examples: [
      {
        input: 's = "abcabcbb"',
        output: "3",
        explanation: 'The answer is "abc", with the length of 3.'
      },
      {
        input: 's = "bbbbb"',
        output: "1",
        explanation: 'The answer is "b", with the length of 1.'
      },
      {
        input: 's = "pwwkew"',
        output: "3",
        explanation: 'The answer is "wke", with the length of 3. Note that "pwke" is a subsequence, not a substring.'
      }
    ],
    constraints: [
      "0 <= s.length <= 5 * 10^4 (An O(N²) quadratic approach will hit ~2.5 * 10^9 operations and time out).",
      "s consists of English letters, digits, symbols and spaces."
    ],
    intuition: "Instead of regenerating and testing all substrings from scratch, maintain a contiguous window [left, right]. As right expands by 1 character at each step:\n\n1. If s[right] has already been seen inside the current active window (last_seen[s[right]] >= left), duplicate detected!\n2. Instantly jump left to last_seen[s[right]] + 1, skipping all intermediate redundant windows.\n3. Update the character's last seen index and record the maximum length: max_len = max(max_len, right - left + 1).",
    visual_trace: {
      description: 'Step-by-step trace for s = "abcabcbb":',
      steps: [
        {
          step: 1,
          index: 0,
          char: "a",
          left: 0,
          window: '"a"',
          max_len: 1,
          seen_map: "{ a: 0 }",
          explanation: "Right at 0 ('a'). Not in map. Window is 'a' (len 1). Store {a: 0}."
        },
        {
          step: 2,
          index: 1,
          char: "b",
          left: 0,
          window: '"ab"',
          max_len: 2,
          seen_map: "{ a: 0, b: 1 }",
          explanation: "Right at 1 ('b'). Window is 'ab' (len 2). Store {b: 1}."
        },
        {
          step: 3,
          index: 2,
          char: "c",
          left: 0,
          window: '"abc"',
          max_len: 3,
          seen_map: "{ a: 0, b: 1, c: 2 }",
          explanation: "Right at 2 ('c'). Window is 'abc' (len 3). Store {c: 2}."
        },
        {
          step: 4,
          index: 3,
          char: "a",
          left: 1,
          window: '"bca"',
          max_len: 3,
          seen_map: "{ a: 3, b: 1, c: 2 }",
          explanation: "'a' seen previously at index 0 (>= left 0). Duplicate! Jump left to 0 + 1 = 1. Window is 'bca' (len 3). Update seen[a] = 3."
        }
      ]
    },
    baseline_solution: {
      name: "Naive Substring Generation",
      complexity: "Time: O(N³) | Space: O(min(N, M))",
      description: "Generates all N*(N+1)/2 substrings and checks each for unique characters using a set in O(N) time.",
      code: `def length_of_longest_substring_naive(s: str) -> int:
    def all_unique(sub):
        return len(set(sub)) == len(sub)
    
    max_len = 0
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            if all_unique(s[i:j]):
                max_len = max(max_len, j - i)
    return max_len`
    },
    optimal_solution: {
      name: "Sliding Window with Index Mapping",
      complexity: "Time: O(N) | Space: O(min(N, Alphabet_Size))",
      description: "Uses a two-pointer sliding window with a dictionary storing the most recent index of each character, advancing right each step.",
      python_code: `def lengthOfLongestSubstring(s: str) -> int:
    last_seen = {}
    left = 0
    max_length = 0
    
    for right, char in enumerate(s):
        # If character is already in the active window, slide left boundary
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
            
        last_seen[char] = right
        max_length = max(max_length, right - left + 1)
        
    return max_length`,
      javascript_code: `function lengthOfLongestSubstring(s) {
    const lastSeen = new Map();
    let left = 0;
    let maxLength = 0;
    
    for (let right = 0; right < s.length; right++) {
        const char = s[right];
        if (lastSeen.has(char) && lastSeen.get(char) >= left) {
            left = lastSeen.get(char) + 1;
        }
        lastSeen.set(char, right);
        maxLength = Math.max(maxLength, right - left + 1);
    }
    return maxLength;
}`,
      line_by_line: [
        {
          line: "last_seen = {}",
          explanation: "Records { character: latest_index_position } to enable immediate left pointer jumps."
        },
        {
          line: "if char in last_seen and last_seen[char] >= left:",
          explanation: "The condition 'last_seen[char] >= left' is crucial: it ensures we only react to duplicates that lie inside our current active window, ignoring duplicates from discarded prefixes."
        },
        {
          line: "left = last_seen[char] + 1",
          explanation: "Jumps the left pointer directly past the previous occurrence of this character."
        },
        {
          line: "max_length = max(max_length, right - left + 1)",
          explanation: "The current valid window length is (right - left + 1). Updates our global maximum."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Both right and left pointers only move forward. The right pointer visits each character once, and the left pointer jumps forward monotonically.",
      space: "O(min(N, M)) — Auxiliary memory is bounded by the size of the input string N and the size of the alphabet M (e.g. 128 for standard ASCII)."
    },
    edge_cases: [
      {
        case: "Empty string s = \"\"",
        risk: "Loop doesn't run; uninitialized variables could return incorrect types.",
        mitigation: "Initialize max_length = 0 so an empty input naturally returns 0."
      },
      {
        case: "Duplicate appears outside active window",
        risk: "If s = 'abba', at index 3 ('a'), 'a' was seen at index 0. If left is not checked, left jumps back to 1, causing invalid window.",
        mitigation: "Always check 'last_seen[char] >= left' before updating left."
      },
      {
        case: "All characters unique (e.g. 'abcdef')",
        risk: "Window should span the entire string.",
        mitigation: "The formula right - left + 1 smoothly expands to len(s) without triggering any contraction."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "In s = 'abba', when right reaches the final 'a' at index 3, why is checking 'last_seen[char] >= left' required?",
        options: [
          "To avoid KeyError in the dictionary.",
          "Because 'a' was last seen at index 0, which is behind the current left pointer (2). Jumping to 0 + 1 would move left BACKWARD.",
          "To reset the max_length variable.",
          "Because JavaScript Map does not allow duplicate keys."
        ],
        correct_index: 1,
        explanation: "At index 2 ('b'), left jumped to index 2. When 'a' is seen at index 3, its previous index is 0. If we blindly set left = last_seen['a'] + 1, left would regress from 2 back to 1, re-introducing the duplicate 'b' into the window!"
      },
      trace_prediction: {
        question: "For string s = 'pwwkew', what is the maximum length discovered and what substring produces it?",
        options: [
          "Length 4 from 'pwke'",
          "Length 3 from 'wke'",
          "Length 2 from 'pw'",
          "Length 5 from 'pwwke'"
        ],
        correct_index: 1,
        explanation: "The contiguous substrings without duplicates are 'pw' (2), 'w' (1), 'wke' (3), and 'kew' (3). The maximum contiguous length is 3 (e.g. 'wke'). 'pwke' is not contiguous."
      },
      sandbox_test_cases: [
        { input: 's = "abcabcbb"', expected: "3" },
        { input: 's = "bbbbb"', expected: "1" },
        { input: 's = "pwwkew"', expected: "3" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Longest Substring with At Most K Distinct Characters",
      question: "How does the sliding window adapt if the substring is allowed to contain at most K distinct characters?",
      approach_shift: "Use a frequency map tracking character counts. Expand right and increment count. While len(frequency_map) > K, decrement count at left and remove from map when count reaches 0, incrementing left until distinct characters <= K."
    },
    verified_resources: [
      {
        title: "LeetCode #3: Longest Substring Without Repeating Characters",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        type: "Official Problem",
        summary: "Problem description, test runner, and submission platform."
      },
      {
        title: "Tech Interview Handbook: Sliding Window Pattern",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/two-pointers/",
        type: "Pattern Blueprint",
        summary: "Universal sliding window blueprint for dynamic versus fixed-size windows."
      }
    ]
  },

  {
    id: "container-with-most-water",
    title: "Container With Most Water",
    subtitle: "Converging Boundaries & Area Maximization",
    topic: "Two pointers",
    pattern_group: "two-pointers",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/container-with-most-water/",
    status_type: "solved",
    learning_objectives: [
      "Derive the mathematical proof for why advancing the shorter line never eliminates the optimal container.",
      "Implement the two-pointer converging boundary pattern from opposite ends of an array.",
      "Formulate area bounds: Area = min(height[left], height[right]) * (right - left).",
      "Achieve optimal O(N) linear time and O(1) constant auxiliary space."
    ],
    prerequisites: [
      { name: "Two Pointers", detail: "Converging inward from extremes (left = 0, right = n - 1)." },
      { name: "Greedy Choice Property", detail: "Making a locally optimal step that provably preserves global optimality." }
    ],
    problem_statement: "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).\n\nFind two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
    examples: [
      {
        input: "height = [1, 8, 6, 2, 5, 4, 8, 3, 7]",
        output: "49",
        explanation: "The vertical lines are at indices 1 (height 8) and 8 (height 7). Distance is 8 - 1 = 7. Height is min(8, 7) = 7. Area = 7 * 7 = 49."
      },
      {
        input: "height = [1, 1]",
        output: "1",
        explanation: "Distance is 1, min height is 1. Area = 1 * 1 = 1."
      }
    ],
    constraints: [
      "n == height.length",
      "2 <= n <= 10^5 (O(N²) quadratic nested loops will perform 10^10 operations and time out).",
      "0 <= height[i] <= 10^4"
    ],
    intuition: "Start with the widest possible container: left = 0 and right = n - 1.\n\nThe area is bounded by the shorter line: Area = min(height[left], height[right]) * (right - left).\n\nIf we move the pointer pointing to the TALLER line inward, the width decreases by 1, while the maximum possible height is still constrained by the shorter line. Thus, moving the taller pointer CANNOT produce a larger area.\n\nThe ONLY way to find a larger area is if we find a taller boundary. Therefore, we must move the pointer at the SHORTER line inward. This decision guarantees no potential maximum is ever overlooked.",
    visual_trace: {
      description: "Converging pointer execution trace for height = [1, 8, 6, 2, 5, 4, 8, 3, 7]:",
      steps: [
        {
          step: 1,
          left: 0,
          right: 8,
          h_left: 1,
          h_right: 7,
          width: 8,
          current_area: "min(1, 7) * 8 = 8",
          action: "h[0] (1) < h[8] (7). Advance left to 1.",
          max_water: 8
        },
        {
          step: 2,
          left: 1,
          right: 8,
          h_left: 8,
          h_right: 7,
          width: 7,
          current_area: "min(8, 7) * 7 = 49",
          action: "h[8] (7) < h[1] (8). Decrement right to 7.",
          max_water: 49
        },
        {
          step: 3,
          left: 1,
          right: 7,
          h_left: 8,
          h_right: 3,
          width: 6,
          current_area: "min(8, 3) * 6 = 18",
          action: "h[7] (3) < h[1] (8). Decrement right to 6.",
          max_water: 49
        }
      ]
    },
    baseline_solution: {
      name: "Exhaustive Pair Scan",
      complexity: "Time: O(N²) | Space: O(1)",
      description: "Compares every pair of vertical lines (i, j) with nested loops.",
      code: `def max_area_brute(height: list[int]) -> int:
    max_w = 0
    n = len(height)
    for i in range(n):
        for j in range(i + 1, n):
            area = min(height[i], height[j]) * (j - i)
            max_w = max(max_w, area)
    return max_w`
    },
    optimal_solution: {
      name: "Two-Pointer Inward Convergence",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Positions pointers at opposite ends and greedily moves the shorter line inward until pointers meet.",
      python_code: `def maxArea(height: list[int]) -> int:
    left = 0
    right = len(height) - 1
    max_water = 0
    
    while left < right:
        # Calculate water bounded by current lines
        h = min(height[left], height[right])
        width = right - left
        max_water = max(max_water, h * width)
        
        # Advance the pointer with the smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
            
    return max_water`,
      javascript_code: `function maxArea(height) {
    let left = 0;
    let right = height.length - 1;
    let maxWater = 0;
    
    while (left < right) {
        const h = Math.min(height[left], height[right]);
        const width = right - left;
        maxWater = Math.max(maxWater, h * width);
        
        if (height[left] < height[right]) {
            left++;
        } else {
            right--;
        }
    }
    return maxWater;
}`,
      line_by_line: [
        {
          line: "left, right = 0, len(height) - 1",
          explanation: "Starts at maximal possible container width across the full array bounds."
        },
        {
          line: "h = min(height[left], height[right])",
          explanation: "Water level is strictly limited by the shorter vertical wall."
        },
        {
          line: "if height[left] < height[right]: left += 1",
          explanation: "Discard the shorter line by moving left inward. Retaining it cannot beat the current area."
        },
        {
          line: "else: right -= 1",
          explanation: "If right is shorter (or equal), advance right inward."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — In each iteration of the while loop, distance (right - left) decreases by exactly 1. The loop executes at most N times.",
      space: "O(1) — Only a constant number of scalar pointer variables (left, right, max_water) are stored."
    },
    edge_cases: [
      {
        case: "Both lines have equal height (height[left] == height[right])",
        risk: "Uncertainty about which pointer to move.",
        mitigation: "Moving either pointer (or both) is mathematically safe, as neither can form a larger container with any intermediate line without a taller counterpart."
      },
      {
        case: "Zero height lines (e.g. [0, 2])",
        risk: "Area evaluates to 0.",
        mitigation: "Handled naturally by min(0, 2) * 1 = 0 without special checks."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why does moving the pointer at the taller line NEVER increase the area?",
        options: [
          "Because width decreases and height is still bottlenecked by the shorter line.",
          "Because the array must be sorted first.",
          "Because pointers must always move to the right.",
          "Because the taller line is automatically deleted from memory."
        ],
        correct_index: 0,
        explanation: "Area = min(height[left], height[right]) * width. Moving the taller line decreases width by 1, while the new height is at best equal to the shorter line (or smaller). Therefore, area can only stay the same or decrease."
      },
      trace_prediction: {
        question: "If height = [3, 1, 2, 4, 5], what is the initial area evaluated at left=0 and right=4?",
        options: [
          "min(3, 5) * 4 = 12",
          "min(3, 5) * 5 = 15",
          "max(3, 5) * 4 = 20",
          "min(1, 4) * 3 = 3"
        ],
        correct_index: 0,
        explanation: "At left=0 (height 3) and right=4 (height 5), width is 4 - 0 = 4. Bottleneck height is min(3, 5) = 3. Area = 3 * 4 = 12."
      },
      sandbox_test_cases: [
        { input: "height = [1, 8, 6, 2, 5, 4, 8, 3, 7]", expected: "49" },
        { input: "height = [1, 1]", expected: "1" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Trapping Rain Water",
      question: "In Container With Most Water, water is held between two outer walls. How does the invariant change for Trapping Rain Water where intermediate bars fill up?",
      approach_shift: "In Trapping Rain Water, water trapped above each bar i is min(left_max, right_max) - height[i]. Use two pointers maintaining running left_max and right_max, accumulating water at the side with the smaller max."
    },
    verified_resources: [
      {
        title: "LeetCode #11: Container With Most Water",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/container-with-most-water/",
        type: "Problem Specification",
        summary: "Official LeetCode problem statement and constraints."
      },
      {
        title: "Tech Interview Handbook: Two Pointers Deep Dive",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/two-pointers/",
        type: "Pattern Guide",
        summary: "In-depth guide to converging and parallel pointer techniques."
      }
    ]
  },

  {
    id: "search-in-rotated-sorted-array",
    title: "Search in Rotated Sorted Array",
    subtitle: "Logarithmic Division on Discontinuous Spaces",
    topic: "Binary search and search-space reduction",
    pattern_group: "binary-search",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/search-in-rotated-sorted-array/",
    status_type: "solved",
    learning_objectives: [
      "Identify the invariant: In any rotated sorted array, splitting at midpoint mid leaves at least ONE half strictly sorted.",
      "Check monotonic bounds on the sorted half to determine if target lies within it in O(1) time.",
      "Achieve logarithmic O(log N) runtime without un-rotating or finding the pivot index first.",
      "Handle edge cases including single-element arrays and non-rotated inputs."
    ],
    prerequisites: [
      { name: "Binary Search", detail: "Standard O(log N) divide-and-conquer on strictly sorted sequences." },
      { name: "Monotonicity", detail: "Using sorted boundary invariants to discard half the search space." }
    ],
    problem_statement: "There is an integer array nums sorted in ascending order (with distinct values).\n\nPrior to being passed to your function, nums is possibly rotated at an unknown pivot index k (1 <= k < nums.length) such that the resulting array is [nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]].\n\nGiven the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums.\n\nYou must write an algorithm with O(log n) runtime complexity.",
    examples: [
      {
        input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 0",
        output: "4",
        explanation: "0 is located at index 4."
      },
      {
        input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 3",
        output: "-1",
        explanation: "3 is not in nums."
      },
      {
        input: "nums = [1], target = 0",
        output: "-1",
        explanation: "Single element does not match target."
      }
    ],
    constraints: [
      "1 <= nums.length <= 5000",
      "-10^4 <= nums[i] <= 10^4",
      "All values of nums are unique.",
      "Must achieve O(log n) time complexity (linear scan O(N) is forbidden)."
    ],
    intuition: "Even though the entire array is not sorted, any slice divided at mid has the following property:\n\nEither the LEFT half (nums[left] .. nums[mid]) is sorted, OR the RIGHT half (nums[mid] .. nums[right]) is sorted.\n\n1. Check if nums[left] <= nums[mid]. If true, left half is strictly sorted!\n   - If nums[left] <= target < nums[mid], target must be in the left half: right = mid - 1.\n   - Otherwise, target must be in the right half: left = mid + 1.\n2. Otherwise, right half is strictly sorted!\n   - If nums[mid] < target <= nums[right], target must be in right half: left = mid + 1.\n   - Otherwise: right = mid - 1.",
    visual_trace: {
      description: "Search trace for nums = [4, 5, 6, 7, 0, 1, 2] and target = 0:",
      steps: [
        {
          step: 1,
          left: 0,
          right: 6,
          mid: 3,
          mid_val: 7,
          is_left_sorted: "nums[0] (4) <= nums[3] (7) -> TRUE. Left half [4, 5, 6, 7] is sorted.",
          target_in_sorted: "Is 4 <= 0 < 7? FALSE. Target (0) is NOT in left half.",
          action: "Search right half: left = mid + 1 = 4."
        },
        {
          step: 2,
          left: 4,
          right: 6,
          mid: 5,
          mid_val: 1,
          is_left_sorted: "nums[4] (0) <= nums[5] (1) -> TRUE. Left half [0, 1] is sorted.",
          target_in_sorted: "Is 0 <= 0 < 1? TRUE! Target (0) IS in left half.",
          action: "Search left: right = mid - 1 = 4."
        },
        {
          step: 3,
          left: 4,
          right: 4,
          mid: 4,
          mid_val: 0,
          is_left_sorted: "nums[4] == target (0) == 0!",
          target_in_sorted: "MATCH FOUND",
          action: "Return index 4."
        }
      ]
    },
    baseline_solution: {
      name: "Linear Scan",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Checks each element sequentially. Violates the O(log N) interview requirement.",
      code: `def search_linear(nums: list[int], target: int) -> int:
    for i, n in enumerate(nums):
        if n == target:
            return i
    return -1`
    },
    optimal_solution: {
      name: "Modified Binary Search on Sorted Half",
      complexity: "Time: O(log N) | Space: O(1)",
      description: "Identifies the sorted half at each midpoint and discards the other half in logarithmic steps.",
      python_code: `def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
            
        # Determine which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted: check if target is inside left bounds
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted: check if target is inside right bounds
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
                
    return -1`,
      javascript_code: `function search(nums, target) {
    let left = 0;
    let right = nums.length - 1;
    
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (nums[mid] === target) return mid;
        
        if (nums[left] <= nums[mid]) {
            if (nums[left] <= target && target < nums[mid]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            if (nums[mid] < target && target <= nums[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    return -1;
}`,
      line_by_line: [
        {
          line: "if nums[left] <= nums[mid]:",
          explanation: "If the leftmost value is <= midpoint, the left segment is strictly ascending with no rotation pivot inside it."
        },
        {
          line: "if nums[left] <= target < nums[mid]: right = mid - 1",
          explanation: "Since the left half is monotonic, we can test target membership simply by comparing with both ends. If inside, focus left."
        },
        {
          line: "else: left = mid + 1",
          explanation: "If target falls outside the sorted left half, it must reside in the remaining unsorted half."
        }
      ]
    },
    time_space_analysis: {
      time: "O(log N) — At every step, we discard exactly half of the remaining search range.",
      space: "O(1) — Only 3 pointers (left, right, mid) are retained in memory."
    },
    edge_cases: [
      {
        case: "Array not rotated (k = 0)",
        risk: "nums[left] <= nums[mid] holds universally, behaving identically to standard binary search.",
        mitigation: "The algorithm naturally handles unrotated arrays without any conditional branch modification."
      },
      {
        case: "Single element array nums = [1]",
        risk: "Boundary checks mid = 0.",
        mitigation: "while left <= right handles 1-element arrays correctly, either matching or returning -1."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why is it guaranteed that at least one half of the rotated array is strictly sorted?",
        options: [
          "Because a single rotation pivot divides the array into at most two sorted subarrays; a midpoint can only divide one of them.",
          "Because the array values are all positive.",
          "Because Python automatically sorts arrays before binary search.",
          "Because duplicate values are not allowed."
        ],
        correct_index: 0,
        explanation: "The rotation consists of exactly one discontinuity (pivot). When you split any array with at most one pivot into two halves, at least one half will NOT contain the pivot and is therefore strictly sorted."
      },
      trace_prediction: {
        question: "In nums = [5, 1, 3] with target = 5: at left=0 (5), right=2 (3), mid=1 (1). Which half is sorted?",
        options: [
          "The left half [5, 1]",
          "The right half [1, 3] because nums[mid] (1) <= nums[right] (3)",
          "Neither half is sorted",
          "Both halves are sorted"
        ],
        correct_index: 1,
        explanation: "nums[left] (5) <= nums[mid] (1) is FALSE. Thus right half is sorted (1 <= 3). 5 does not lie in (1, 3], so search space shifts to the left half."
      },
      sandbox_test_cases: [
        { input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 0", expected: "4" },
        { input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 3", expected: "-1" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Search in Rotated Sorted Array II (With Duplicates)",
      question: "If nums contains duplicates (e.g. [1, 0, 1, 1, 1]), nums[left] == nums[mid] == nums[right]. How does this affect complexity?",
      approach_shift: "When nums[left] == nums[mid] == nums[right], you cannot determine which half is sorted. You must increment left and decrement right (left += 1, right -= 1), which degrades the worst-case runtime to O(N)."
    },
    verified_resources: [
      {
        title: "LeetCode #33: Search in Rotated Sorted Array",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/search-in-rotated-sorted-array/",
        type: "Official Problem",
        summary: "Problem description, test runner, and submission platform."
      },
      {
        title: "Tech Interview Handbook: Binary Search",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/binary-search/",
        type: "Pattern Guide",
        summary: "Search space reduction, boundary templates, and logarithmic predicates."
      }
    ]
  },

  {
    id: "invert-binary-tree",
    title: "Invert Binary Tree",
    subtitle: "Tree Recursion & Subtree Swapping",
    topic: "Trees, BSTs, and tree traversals",
    pattern_group: "trees",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/invert-binary-tree/",
    status_type: "solved",
    learning_objectives: [
      "Understand tree recursion and call-stack frame execution order.",
      "Formulate the recursive base case: an empty subtree (root is None) returns None.",
      "Swap child references (left and right) after recursively inverting children.",
      "Analyze recursive call stack depth: O(H) where H is tree height."
    ],
    prerequisites: [
      { name: "Binary Tree Fundamentals", detail: "TreeNode structure with val, left, and right pointers." },
      { name: "Recursion & Call Stack", detail: "Base cases, recursive unwinding, and post-order aggregation." }
    ],
    problem_statement: "Given the root of a binary tree, invert the tree, and return its root.",
    examples: [
      {
        input: "root = [4, 2, 7, 1, 3, 6, 9]",
        output: "[4, 7, 2, 9, 6, 3, 1]",
        explanation: "Every node's left and right children are mirrored across the tree."
      },
      {
        input: "root = [2, 1, 3]",
        output: "[2, 3, 1]",
        explanation: "Left child 1 and right child 3 are swapped."
      },
      {
        input: "root = []",
        output: "[]",
        explanation: "An empty tree inverts to an empty tree."
      }
    ],
    constraints: [
      "The number of nodes in the tree is in the range [0, 100].",
      "-100 <= Node.val <= 100"
    ],
    intuition: "Inverting a binary tree means that for every node, its left child becomes its right child and vice versa, applied recursively to every descendant.\n\n1. Base case: If root is None, there is nothing to invert; return None.\n2. Invert both subtrees: recursively call invertTree(root.left) and invertTree(root.right).\n3. Swap pointers: root.left, root.right = inverted_right, inverted_left.\n4. Return the root.",
    visual_trace: {
      description: "Call stack progression for root = [2, 1, 3]:",
      steps: [
        {
          step: 1,
          action: "Call invertTree(node 2)",
          state: "Waiting on children of 2",
          explanation: "Node 2 calls invertTree(1) on left child and invertTree(3) on right child."
        },
        {
          step: 2,
          action: "Call invertTree(node 1)",
          state: "Children are None",
          explanation: "Left child of 1 is None -> returns None. Right child of 1 is None -> returns None. 1 swaps None and None, returns node 1."
        },
        {
          step: 3,
          action: "Call invertTree(node 3)",
          state: "Children are None",
          explanation: "Both children are None. Returns node 3."
        },
        {
          step: 4,
          action: "Unwind node 2",
          state: "Swap left and right of node 2",
          explanation: "node 2 sets left = 3 and right = 1. Returns node 2. Result is [2, 3, 1]."
        }
      ]
    },
    baseline_solution: {
      name: "Iterative BFS Queue Inversion",
      complexity: "Time: O(N) | Space: O(W) where W is max tree width",
      description: "Uses an explicit queue to visit each node level by level, swapping children iteratively.",
      code: `from collections import deque

def invert_tree_iterative(root):
    if not root:
        return None
    queue = deque([root])
    while queue:
        curr = queue.popleft()
        curr.left, curr.right = curr.right, curr.left
        if curr.left:
            queue.append(curr.left)
        if curr.right:
            queue.append(curr.right)
    return root`
    },
    optimal_solution: {
      name: "Recursive DFS Subtree Swap",
      complexity: "Time: O(N) | Space: O(H) where H is tree height",
      description: "Clean recursive post-order tree traversal swapping pointers during call-stack unwinding.",
      python_code: `class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def invertTree(root: TreeNode | None) -> TreeNode | None:
    if not root:
        return None
        
    # Recursively invert subtrees
    left_inverted = invertTree(root.left)
    right_inverted = invertTree(root.right)
    
    # Swap children
    root.left = right_inverted
    root.right = left_inverted
    
    return root`,
      javascript_code: `function invertTree(root) {
    if (!root) return null;
    
    const leftInverted = invertTree(root.left);
    const rightInverted = invertTree(root.right);
    
    root.left = rightInverted;
    root.right = leftInverted;
    
    return root;
}`,
      line_by_line: [
        {
          line: "if not root: return None",
          explanation: "Essential base case. Leaf node children (None) terminate recursion without NullPointer exceptions."
        },
        {
          line: "left_inverted = invertTree(root.left)",
          explanation: "Recursively processes the entire left subtree down to its leaves."
        },
        {
          line: "root.left = right_inverted; root.right = left_inverted",
          explanation: "Swaps pointers after both subtrees are inverted."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Every node in the binary tree is visited exactly once.",
      space: "O(H) — Space is consumed by the call stack. For a balanced tree, height H is O(log N); in a worst-case completely skewed tree, H is O(N)."
    },
    edge_cases: [
      {
        case: "Empty tree root = None",
        risk: "Calling root.left will raise an AttributeError/TypeError.",
        mitigation: "Check if not root as the very first line of the function."
      },
      {
        case: "Asymmetric tree (one child is None)",
        risk: "One child becomes None while the other has subtrees.",
        mitigation: "Swapping None with an inverted subtree works seamlessly."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "What is the space complexity of recursive invertTree on a completely skewed tree of N nodes?",
        options: [
          "O(N) because the recursion stack depth reaches N.",
          "O(1) because no new tree nodes are allocated.",
          "O(log N) always for any binary tree.",
          "O(N²)"
        ],
        correct_index: 0,
        explanation: "When a tree is skewed (like a linked list where every node only has a left child), the recursive call stack depth equals N, requiring O(N) auxiliary stack memory."
      },
      trace_prediction: {
        question: "If root has val=4, left child 2, and right child 7, what is root.left.val after invertTree finishes?",
        options: [
          "7",
          "2",
          "4",
          "None"
        ],
        correct_index: 0,
        explanation: "The left and right children are swapped. The right child (7) becomes the new left child, so root.left.val is 7."
      },
      sandbox_test_cases: [
        { input: "root = [4, 2, 7, 1, 3, 6, 9]", expected: "[4, 7, 2, 9, 6, 3, 1]" },
        { input: "root = [2, 1, 3]", expected: "[2, 3, 1]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Maximum Depth of Binary Tree",
      question: "How does the recursive post-order template adapt to find the maximum depth of a binary tree?",
      approach_shift: "Base case: if not root: return 0. Recursively compute depth of children: return 1 + max(maxDepth(root.left), maxDepth(root.right))."
    },
    verified_resources: [
      {
        title: "LeetCode #226: Invert Binary Tree",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/invert-binary-tree/",
        type: "Official Problem",
        summary: "Standard problem statement and test harness."
      },
      {
        title: "Tech Interview Handbook: Tree Traversals",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/tree/",
        type: "Pattern Blueprint",
        summary: "Comprehensive guide to tree DFS vs BFS recursion patterns."
      }
    ]
  },

  {
    id: "number-of-islands",
    title: "Number of Islands",
    subtitle: "Grid Flood Fill & Connected Components",
    topic: "Graphs, BFS, DFS, and topological sorting",
    pattern_group: "graphs",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/number-of-islands/",
    status_type: "recommended",
    learning_objectives: [
      "Represent a 2D matrix as an implicit undirected graph where adjacent cells are connected.",
      "Execute Depth-First Search (DFS) or Breadth-First Search (BFS) flood fill to sink connected components.",
      "Mutate grid cells in-place ('1' -> '0') to achieve O(1) auxiliary space beyond the recursion stack.",
      "Handle boundary constraints (r < 0, r >= rows, c < 0, c >= cols) safely."
    ],
    prerequisites: [
      { name: "Graph Traversal", detail: "DFS connected component discovery and marking visited states." },
      { name: "2D Matrix Navigation", detail: "4-directional delta vectors: (0, 1), (0, -1), (1, 0), (-1, 0)." }
    ],
    problem_statement: "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.\n\nAn island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.",
    examples: [
      {
        input: 'grid = [\n  ["1","1","1","1","0"],\n  ["1","1","0","1","0"],\n  ["1","1","0","0","0"],\n  ["0","0","0","0","0"]\n]',
        output: "1",
        explanation: "All adjacent land cells connect horizontally and vertically to form 1 single island."
      },
      {
        input: 'grid = [\n  ["1","1","0","0","0"],\n  ["1","1","0","0","0"],\n  ["0","0","1","0","0"],\n  ["0","0","0","1","1"]\n]',
        output: "3",
        explanation: "There are 3 distinct islands."
      }
    ],
    constraints: [
      "m == grid.length, n == grid[i].length",
      "1 <= m, n <= 300",
      "grid[i][j] is '0' or '1'."
    ],
    intuition: "Iterate across every cell (r, c) in the matrix:\n\n1. When an unvisited land cell ('1') is encountered, we have discovered a NEW island! Increment islands_count by 1.\n2. Immediately launch a DFS flood fill starting at (r, c) that visits all 4 adjacent cells (up, down, left, right).\n3. In the DFS, sink each visited land cell by flipping grid[r][c] = '0'. This ensures we never count any cell belonging to this island again.\n4. When all cells have been scanned, return islands_count.",
    visual_trace: {
      description: "Grid flood fill execution trace:",
      steps: [
        {
          step: 1,
          action: "Cell (0, 0) is '1'",
          state: "Island #1 discovered!",
          explanation: "Increment count to 1. DFS begins at (0, 0)."
        },
        {
          step: 2,
          action: "Sink connected land",
          state: "Flip '1' to '0'",
          explanation: "DFS traverses (0, 0) -> (0, 1) -> (1, 0). Mutates all connected cells to '0'."
        },
        {
          step: 3,
          action: "Resume scanning",
          state: "Skipping '0' cells",
          explanation: "Main loop scans (0, 1), (0, 2), etc., which are now '0'. No extra islands counted."
        }
      ]
    },
    baseline_solution: {
      name: "BFS Traversal with Auxiliary Visited Set",
      complexity: "Time: O(M * N) | Space: O(M * N) for visited set",
      description: "Uses an explicit set of coordinate tuples to avoid grid mutation.",
      code: `from collections import deque

def num_islands_bfs(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()
    islands = 0
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                islands += 1
                queue = deque([(r, c)])
                visited.add((r, c))
                while queue:
                    curr_r, curr_c = queue.popleft()
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            queue.append((nr, nc))
    return islands`
    },
    optimal_solution: {
      name: "In-Place DFS Flood Fill",
      complexity: "Time: O(M * N) | Space: O(M * N) recursion stack worst case",
      description: "Sinks cells directly in the grid ('1' -> '0') to eliminate the visited set.",
      python_code: `def numIslands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0
        
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def dfs(r, c):
        # Base case: out of bounds or water cell
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
            
        # Sink cell to avoid revisiting
        grid[r][c] = "0"
        
        # Explore 4 cardinal directions
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
        
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                dfs(r, c)
                
    return count`,
      javascript_code: `function numIslands(grid) {
    if (!grid || !grid.length) return 0;
    
    const rows = grid.length;
    const cols = grid[0].length;
    let count = 0;
    
    function dfs(r, c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] !== '1') {
            return;
        }
        grid[r][c] = '0';
        dfs(r + 1, c);
        dfs(r - 1, c);
        dfs(r, c + 1);
        dfs(r, c - 1);
    }
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === '1') {
                count++;
                dfs(r, c);
            }
        }
    }
    return count;
}`,
      line_by_line: [
        {
          line: "if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1': return",
          explanation: "Single line guarding against matrix boundary overflow and skipping water cells."
        },
        {
          line: "grid[r][c] = '0'",
          explanation: "In-place mutation marks this cell as visited, preventing infinite cycles between adjacent cells."
        },
        {
          line: "dfs(r + 1, c); dfs(r - 1, c); dfs(r, c + 1); dfs(r, c - 1)",
          explanation: "Explores all 4 cardinal directions. Diagonals are omitted as problem requires horizontal/vertical adjacency only."
        }
      ]
    },
    time_space_analysis: {
      time: "O(M * N) — Every cell is visited at most a constant number of times (once by the outer loop, and once by DFS).",
      space: "O(M * N) — In the worst case where the grid is filled entirely with land '1's, the recursion stack depth reaches M * N."
    },
    edge_cases: [
      {
        case: "Diagonal land cells (e.g. [[1,0],[0,1]])",
        risk: "Incorrectly assuming diagonal connectivity.",
        mitigation: "Only test cardinal steps: (-1,0), (1,0), (0,-1), (0,1). The diagonal grid correctly produces 2 islands."
      },
      {
        case: "Grid with only water",
        risk: "No DFS calls executed.",
        mitigation: "Returns 0 naturally."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why do we set grid[r][c] = '0' inside DFS?",
        options: [
          "To sink the land cell so that future scans and recursion branches do not visit it again.",
          "Because 0 is faster to compare than 1.",
          "To decrease the memory footprint of the matrix.",
          "Because the problem asks us to delete the grid."
        ],
        correct_index: 0,
        explanation: "Flipping '1' to '0' acts as a built-in visited flag, eliminating infinite recursion cycles between adjacent cells and preventing double-counting."
      },
      trace_prediction: {
        question: "For a 2x2 grid [['1', '0'], ['0', '1']], how many islands exist?",
        options: [
          "2 because diagonal cells do not connect horizontally or vertically.",
          "1 because they touch diagonally.",
          "0",
          "4"
        ],
        correct_index: 0,
        explanation: "The problem statement explicitly specifies: 'formed by connecting adjacent lands horizontally or vertically'. Diagonals are not connected, so there are 2 separate islands."
      },
      sandbox_test_cases: [
        { input: 'grid = [["1","1","0"],["0","1","0"],["0","0","1"]]', expected: "2" },
        { input: 'grid = [["0","0"],["0","0"]]', expected: "0" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Max Area of Island",
      question: "Instead of counting the total number of islands, how would you find the maximum area of a single island?",
      approach_shift: "Modify dfs(r, c) to return the area of the connected component: return 1 + dfs(up) + dfs(down) + dfs(left) + dfs(right). Track max_area = max(max_area, dfs(r, c))."
    },
    verified_resources: [
      {
        title: "LeetCode #200: Number of Islands",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/number-of-islands/",
        type: "Official Problem",
        summary: "Problem description, test cases, and judge."
      },
      {
        title: "Tech Interview Handbook: Graph BFS/DFS",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/graph/",
        type: "Pattern Blueprint",
        summary: "Grid traversal, topological sorting, and cycle detection."
      }
    ]
  },

  {
    id: "climbing-stairs",
    title: "Climbing Stairs",
    subtitle: "Fibonacci Recurrence & State Compression",
    topic: "Dynamic programming",
    pattern_group: "dynamic-programming",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/climbing-stairs/",
    status_type: "recommended",
    learning_objectives: [
      "Break down a dynamic programming problem into overlapping subproblems and optimal substructure.",
      "Derive the state recurrence: dp[i] = dp[i-1] + dp[i-2].",
      "Compress O(N) space tabulation down to O(1) space using two rolling variables.",
      "Avoid exponential O(2^N) naive recursion with top-down memoization or bottom-up tabulation."
    ],
    prerequisites: [
      { name: "Induction & Recurrence", detail: "Expressing solution to step N as a combination of smaller sub-steps." },
      { name: "Space Optimization", detail: "Recognizing that only the last two state values are required." }
    ],
    problem_statement: "You are climbing a staircase. It takes n steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
    examples: [
      {
        input: "n = 2",
        output: "2",
        explanation: "There are two ways to climb to the top: 1. 1 step + 1 step, 2. 2 steps."
      },
      {
        input: "n = 3",
        output: "3",
        explanation: "There are three ways: 1. 1 + 1 + 1, 2. 1 + 2, 3. 2 + 1."
      }
    ],
    constraints: [
      "1 <= n <= 45"
    ],
    intuition: "To reach step n, you can only arrive from two possible previous positions:\n\n1. From step n - 1 (taking a single 1-step leap).\n2. From step n - 2 (taking a single 2-step leap).\n\nTherefore, total distinct ways to reach step n is the sum of ways to reach step n - 1 and ways to reach step n - 2:\nways(n) = ways(n - 1) + ways(n - 2).\n\nThis is identical to the Fibonacci sequence with base cases ways(1) = 1, ways(2) = 2. Since each step only depends on the previous two values, we only need to store two variables (prev1, prev2), achieving O(N) time and O(1) space.",
    visual_trace: {
      description: "State progression table up to n = 5:",
      steps: [
        {
          step: 1,
          n_val: 1,
          ways: 1,
          formula: "Base case: [1]",
          explanation: "Only 1 way to climb 1 step: [1]."
        },
        {
          step: 2,
          n_val: 2,
          ways: 2,
          formula: "Base case: [1+1, 2]",
          explanation: "2 ways: [1+1] or [2]."
        },
        {
          step: 3,
          n_val: 3,
          ways: 3,
          formula: "ways(2) + ways(1) = 2 + 1 = 3",
          explanation: "3 ways: [1+1+1], [1+2], [2+1]."
        },
        {
          step: 4,
          n_val: 4,
          ways: 5,
          formula: "ways(3) + ways(2) = 3 + 2 = 5",
          explanation: "5 distinct combinations."
        },
        {
          step: 5,
          n_val: 5,
          ways: 8,
          formula: "ways(4) + ways(3) = 5 + 3 = 8",
          explanation: "8 distinct combinations."
        }
      ]
    },
    baseline_solution: {
      name: "Naive Exponential Recursion",
      complexity: "Time: O(2^N) | Space: O(N) stack",
      description: "Computes identical subproblems repeatedly in an exponential recursion tree.",
      code: `def climb_stairs_naive(n: int) -> int:
    if n <= 2:
        return n
    return climb_stairs_naive(n - 1) + climb_stairs_naive(n - 2)`
    },
    optimal_solution: {
      name: "Iterative Rolling State (Fibonacci)",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Maintains two variables representing dp[i-1] and dp[i-2], updating in a single loop.",
      python_code: `def climbStairs(n: int) -> int:
    if n <= 2:
        return n
        
    prev2 = 1  # ways to reach step 1
    prev1 = 2  # ways to reach step 2
    
    for step in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
        
    return prev1`,
      javascript_code: `function climbStairs(n) {
    if (n <= 2) return n;
    
    let prev2 = 1;
    let prev1 = 2;
    
    for (let i = 3; i <= n; i++) {
        const current = prev1 + prev2;
        prev2 = prev1;
        prev1 = current;
    }
    return prev1;
}`,
      line_by_line: [
        {
          line: "if n <= 2: return n",
          explanation: "Base cases: 1 step has 1 way, 2 steps has 2 ways."
        },
        {
          line: "current = prev1 + prev2",
          explanation: "State transition: sum of reaching n-1 and n-2."
        },
        {
          line: "prev2 = prev1; prev1 = current",
          explanation: "Slide rolling variables forward for the next iteration without array allocation."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Single loop executing n - 2 times.",
      space: "O(1) — Strictly constant memory; no array or recursion stack."
    },
    edge_cases: [
      {
        case: "n = 1",
        risk: "Loop bounds range(3, 2) wouldn't execute.",
        mitigation: "Early return if n <= 2 handles n = 1 immediately."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why can't the naive recursion climb_stairs(n-1) + climb_stairs(n-2) pass within time limits for n = 45?",
        options: [
          "Because O(2^45) is approximately 3.5 * 10^13 operations, which takes hours to compute.",
          "Because recursion is not allowed in Python.",
          "Because integers overflow in Python.",
          "Because the answer for 45 is negative."
        ],
        correct_index: 0,
        explanation: "Without memoization, overlapping subproblems like climb_stairs(3) are re-evaluated millions of times, leading to an exponential O(2^N) time complexity that times out on modern CPUs."
      },
      trace_prediction: {
        question: "For n = 4, what is the value of climbStairs(4)?",
        options: [
          "5",
          "4",
          "6",
          "8"
        ],
        correct_index: 0,
        explanation: "climbStairs(1)=1, climbStairs(2)=2, climbStairs(3)=3, climbStairs(4)=3+2=5."
      },
      sandbox_test_cases: [
        { input: "n = 2", expected: "2" },
        { input: "n = 3", expected: "3" },
        { input: "n = 5", expected: "8" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: House Robber",
      question: "How does this 2-step DP invariant translate to House Robber where you cannot rob adjacent houses?",
      approach_shift: "At house i, you either rob house i + loot from i-2, or skip house i and keep loot from i-1: dp[i] = max(dp[i-1], dp[i-2] + nums[i])."
    },
    verified_resources: [
      {
        title: "LeetCode #70: Climbing Stairs",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/climbing-stairs/",
        type: "Official Problem",
        summary: "Official problem statement and benchmarks."
      },
      {
        title: "Tech Interview Handbook: Dynamic Programming",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/dynamic-programming/",
        type: "Pattern Guide",
        summary: "Patterns, memoization vs tabulation, and space compression."
      }
    ]
  },

  {
    id: "subarray-sum-equals-k",
    title: "Subarray Sum Equals K",
    subtitle: "Cumulative Sum Difference Frequency Mapping",
    topic: "Prefix sums",
    pattern_group: "prefix-sums",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/subarray-sum-equals-k/",
    status_type: "recommended",
    learning_objectives: [
      "Convert contiguous range sum queries into differences: sum(i..j) = prefix[j] - prefix[i-1].",
      "Store prefix sum frequencies in a hash map to achieve O(N) linear time.",
      "Initialize hash map with { 0: 1 } to account for subarrays starting at index 0.",
      "Explain why sliding window cannot be used when negative numbers are present."
    ],
    prerequisites: [
      { name: "Prefix Sums", detail: "Cumulative array sums where subsegment sums equal prefix differences." },
      { name: "Hash Map Frequencies", detail: "Recording how many times a particular cumulative sum has been reached." }
    ],
    problem_statement: "Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k.\n\nA subarray is a contiguous non-empty sequence of elements within an array.",
    examples: [
      {
        input: "nums = [1, 1, 1], k = 2",
        output: "2",
        explanation: "Subarrays [nums[0], nums[1]] and [nums[1], nums[2]] both sum to 2."
      },
      {
        input: "nums = [1, 2, 3], k = 3",
        output: "2",
        explanation: "Subarrays [1, 2] and [3] both sum to 3."
      }
    ],
    constraints: [
      "1 <= nums.length <= 2 * 10^4",
      "-1000 <= nums[i] <= 1000 (Negative numbers are allowed; sliding window DOES NOT apply here!)",
      "-10^7 <= k <= 10^7"
    ],
    intuition: "Let prefix_sum[j] be the sum of nums[0 .. j]. The sum of any subarray from index i to j is:\nsum(i .. j) = prefix_sum[j] - prefix_sum[i - 1].\n\nWe want sum(i .. j) == k, which rearranges to:\nprefix_sum[i - 1] == prefix_sum[j] - k.\n\nAs we iterate through the array maintaining a running cumulative sum:\n1. Check how many times (running_sum - k) has appeared in our frequency map so far. Add that frequency to our total count.\n2. Increment the frequency of running_sum in our map.\n3. Base case: initialize prefix_counts = { 0: 1 } so that if running_sum == k, running_sum - k = 0 will match.",
    visual_trace: {
      description: "Prefix sum frequency trace for nums = [1, 2, 3] and k = 3:",
      steps: [
        {
          step: 1,
          index: 0,
          num: 1,
          curr_sum: 1,
          need: "1 - 3 = -2",
          found_count: 0,
          map: "{ 0: 1, 1: 1 }",
          explanation: "Sum is 1. Need -2. Not in map. Record sum 1."
        },
        {
          step: 2,
          index: 1,
          num: 2,
          curr_sum: 3,
          need: "3 - 3 = 0",
          found_count: 1,
          map: "{ 0: 1, 1: 1, 3: 1 }",
          explanation: "Sum is 3. Need 0. 0 is in map (count 1)! Subarray [1, 2] found. Total count = 1."
        },
        {
          step: 3,
          index: 2,
          num: 3,
          curr_sum: 6,
          need: "6 - 3 = 3",
          found_count: 1,
          map: "{ 0: 1, 1: 1, 3: 1, 6: 1 }",
          explanation: "Sum is 6. Need 3. 3 is in map (count 1)! Subarray [3] found. Total count = 2."
        }
      ]
    },
    baseline_solution: {
      name: "Brute-Force Subarray Enumeration",
      complexity: "Time: O(N²) | Space: O(1)",
      description: "Computes the sum of all N*(N+1)/2 subarrays using nested loops.",
      code: `def subarray_sum_brute(nums: list[int], k: int) -> int:
    count = 0
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == k:
                count += 1
    return count`
    },
    optimal_solution: {
      name: "Prefix Sum Frequency Hash Map",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Maintains running cumulative sum and counts occurrences of (curr_sum - k) in a frequency dictionary.",
      python_code: `def subarraySum(nums: list[int], k: int) -> int:
    count = 0
    curr_sum = 0
    # Map stores { prefix_sum_value: number_of_times_seen }
    prefix_counts = {0: 1}
    
    for n in nums:
        curr_sum += n
        
        # Check if there is an earlier prefix such that curr_sum - earlier_prefix = k
        if curr_sum - k in prefix_counts:
            count += prefix_counts[curr_sum - k]
            
        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1
        
    return count`,
      javascript_code: `function subarraySum(nums, k) {
    let count = 0;
    let currSum = 0;
    const prefixCounts = new Map([[0, 1]]);
    
    for (const n of nums) {
        currSum += n;
        if (prefixCounts.has(currSum - k)) {
            count += prefixCounts.get(currSum - k);
        }
        prefixCounts.set(currSum, (prefixCounts.get(currSum) || 0) + 1);
    }
    return count;
}`,
      line_by_line: [
        {
          line: "prefix_counts = {0: 1}",
          explanation: "Represents an empty prefix sum of 0 occurring once. This handles subarrays that sum to k starting directly at index 0."
        },
        {
          line: "if curr_sum - k in prefix_counts:",
          explanation: "Algebraic complement: if curr_sum - earlier_prefix == k, then earlier_prefix == curr_sum - k."
        },
        {
          line: "count += prefix_counts[curr_sum - k]",
          explanation: "Adds how many times this earlier prefix sum occurred, as each occurrence defines a distinct valid subarray."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Exactly one pass through nums with O(1) average hash map lookups.",
      space: "O(N) — Storing up to N distinct prefix sums in the frequency map."
    },
    edge_cases: [
      {
        case: "Negative numbers in array",
        risk: "Cumulative sum is not monotonic, meaning standard two-pointer sliding window fails.",
        mitigation: "Prefix sum hash map works regardless of positive, zero, or negative numbers."
      },
      {
        case: "k = 0",
        risk: "Zero sum subarrays (e.g. [1, -1]).",
        mitigation: "curr_sum - 0 in prefix_counts correctly matches whenever cumulative sum repeats."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why can't we use a two-pointer sliding window to solve Subarray Sum Equals K when nums contains negative numbers?",
        options: [
          "Because expanding the right pointer does not guarantee the window sum increases, breaking the monotonic expansion/contraction invariant.",
          "Because sliding window only works on strings.",
          "Because negative numbers crash the while loop.",
          "Because two pointers requires O(N) extra space."
        ],
        correct_index: 0,
        explanation: "Sliding window relies on the property that expanding right increases the sum and moving left decreases it. With negative numbers, adding an element can decrease the sum and removing an element can increase it, destroying the invariant."
      },
      trace_prediction: {
        question: "Why must prefix_counts be initialized with { 0: 1 }?",
        options: [
          "To account for subarrays starting at index 0 whose sum directly equals k (curr_sum - k = 0).",
          "Because dictionary indices in Python must start at 0.",
          "To avoid an empty dictionary exception.",
          "It is optional and does not affect the answer."
        ],
        correct_index: 0,
        explanation: "If the first element is nums[0] = k, curr_sum becomes k. Then curr_sum - k = 0. Without {0: 1}, this valid subarray would not be counted!"
      },
      sandbox_test_cases: [
        { input: "nums = [1, 1, 1], k = 2", expected: "2" },
        { input: "nums = [1, 2, 3], k = 3", expected: "2" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Subarray Sums Divisible by K",
      question: "How do prefix sums adapt when the subarray sum must be divisible by K (sum % K == 0)?",
      approach_shift: "Store prefix_sum % K in the frequency map. Normalize negative remainders: (curr_sum % k + k) % k. If two prefix sums have the same remainder modulo K, their difference is divisible by K."
    },
    verified_resources: [
      {
        title: "LeetCode #560: Subarray Sum Equals K",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/subarray-sum-equals-k/",
        type: "Official Problem",
        summary: "Problem description, test runner, and submission platform."
      },
      {
        title: "GeeksforGeeks: Prefix Sum Array & Range Sum",
        publisher: "GeeksforGeeks",
        url: "https://www.geeksforgeeks.org/prefix-sum-array-implementation-applications_competitive-programming/",
        type: "Tutorial",
        summary: "Detailed overview of range sum transformations and frequency hashing."
      }
    ]
  },

  {
    id: "daily-temperatures",
    title: "Daily Temperatures",
    subtitle: "Monotonically Decreasing Index Stack",
    topic: "Monotonic stacks and queues",
    pattern_group: "monotonic-stack",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/daily-temperatures/",
    status_type: "recommended",
    learning_objectives: [
      "Understand the monotonic stack invariant: storing unresolved elements in strictly decreasing order.",
      "Recognize the 'Next Greater Element' pattern in O(N) amortized time.",
      "Store indices on the stack rather than values to compute distances between days.",
      "Prove why every element is pushed and popped at most once."
    ],
    prerequisites: [
      { name: "Stack (LIFO)", detail: "Push and pop operations in O(1) time." },
      { name: "Next Greater Element Pattern", detail: "Resolving waiting items when a larger value appears." }
    ],
    problem_statement: "Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.",
    examples: [
      {
        input: "temperatures = [73, 74, 75, 71, 69, 72, 76, 73]",
        output: "[1, 1, 4, 2, 1, 1, 0, 0]",
        explanation: "Day 0 (73) -> Day 1 (74, wait 1). Day 1 (74) -> Day 2 (75, wait 1). Day 2 (75) -> Day 6 (76, wait 4)."
      },
      {
        input: "temperatures = [30, 40, 50, 60]",
        output: "[1, 1, 1, 0]",
        explanation: "Each day is immediately followed by a warmer day."
      }
    ],
    constraints: [
      "1 <= temperatures.length <= 10^5",
      "30 <= temperatures[i] <= 100"
    ],
    intuition: "Instead of scanning forward for each day (which takes O(N²) in the worst case when temperatures are descending):\n\nMaintain a stack storing INDICES of days whose warmer temperature has NOT yet been found. The temperatures corresponding to stack indices will be in monotonically decreasing order.\n\nFor each day i with temperature curr_temp:\nWhile stack is not empty and curr_temp > temperatures[stack[-1]]:\n  prev_day = stack.pop()\n  answer[prev_day] = i - prev_day\n\nPush index i onto the stack. Days that never find a warmer temperature remain 0 in the result.",
    visual_trace: {
      description: "Monotonic stack execution trace for [73, 74, 75, 71, 69, 72]:",
      steps: [
        {
          step: 1,
          day: 0,
          temp: 73,
          stack: "[0 (73)]",
          res: "[0, 0, 0, 0, 0, 0]",
          explanation: "Push day 0 (73) to stack."
        },
        {
          step: 2,
          day: 1,
          temp: 74,
          stack: "[1 (74)]",
          res: "[1, 0, 0, 0, 0, 0]",
          explanation: "74 > 73! Pop day 0, res[0] = 1 - 0 = 1. Push day 1 (74)."
        },
        {
          step: 3,
          day: 2,
          temp: 75,
          stack: "[2 (75)]",
          res: "[1, 1, 0, 0, 0, 0]",
          explanation: "75 > 74! Pop day 1, res[1] = 2 - 1 = 1. Push day 2 (75)."
        },
        {
          step: 4,
          day: 3,
          temp: 71,
          stack: "[2 (75), 3 (71)]",
          res: "[1, 1, 0, 0, 0, 0]",
          explanation: "71 < 75. Push day 3."
        },
        {
          step: 5,
          day: 4,
          temp: 69,
          stack: "[2 (75), 3 (71), 4 (69)]",
          res: "[1, 1, 0, 0, 0, 0]",
          explanation: "69 < 71. Push day 4."
        },
        {
          step: 6,
          day: 5,
          temp: 72,
          stack: "[2 (75), 5 (72)]",
          res: "[1, 1, 0, 2, 1, 0]",
          explanation: "72 > 69 (pop 4, res[4]=1), 72 > 71 (pop 3, res[3]=2), 72 < 75. Push day 5."
        }
      ]
    },
    baseline_solution: {
      name: "Forward Scan Brute Force",
      complexity: "Time: O(N²) | Space: O(1)",
      description: "For each day, iterates through all subsequent days until finding a strictly warmer one.",
      code: `def daily_temperatures_brute(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    res = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                res[i] = j - i
                break
    return res`
    },
    optimal_solution: {
      name: "Monotonic Decreasing Stack",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Pushes indices of days to a stack; pops and resolves waiting days as soon as a warmer temperature is encountered.",
      python_code: `def dailyTemperatures(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    res = [0] * n
    stack = []  # Stores indices of unresolved days
    
    for i, t in enumerate(temperatures):
        # Resolve all waiting days that are colder than today's temperature
        while stack and t > temperatures[stack[-1]]:
            prev_day = stack.pop()
            res[prev_day] = i - prev_day
            
        stack.append(i)
        
    return res`,
      javascript_code: `function dailyTemperatures(temperatures) {
    const n = temperatures.length;
    const res = new Array(n).fill(0);
    const stack = [];
    
    for (let i = 0; i < n; i++) {
        while (stack.length && temperatures[i] > temperatures[stack[stack.length - 1]]) {
            const prevDay = stack.pop();
            res[prevDay] = i - prevDay;
        }
        stack.push(i);
    }
    return res;
}`,
      line_by_line: [
        {
          line: "stack = []",
          explanation: "Maintains indices of days waiting for a warmer temperature in decreasing order of temperature."
        },
        {
          line: "while stack and t > temperatures[stack[-1]]:",
          explanation: "Whenever today is warmer than the day on top of the stack, today is that day's next warmer day."
        },
        {
          line: "res[prev_day] = i - prev_day",
          explanation: "Calculates the distance in days between the previous cold day and today."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Each day index is pushed onto the stack exactly once and popped at most once across the entire algorithm.",
      space: "O(N) — In the worst case (strictly descending temperatures), all N indices reside on the stack."
    },
    edge_cases: [
      {
        case: "Strictly decreasing temperatures [90, 80, 70]",
        risk: "No warmer day exists for any day.",
        mitigation: "Array is initialized with 0; unresolved indices stay 0."
      },
      {
        case: "Strictly increasing temperatures [30, 40, 50]",
        risk: "Every day resolves on the very next step.",
        mitigation: "Stack depth never exceeds 1; resolves smoothly in O(N)."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why does the while loop inside the for loop NOT cause O(N²) worst-case runtime?",
        options: [
          "Because each index is pushed to the stack once and popped at most once across all iterations (amortized O(1) per element).",
          "Because temperatures are capped at 100.",
          "Because Python stacks operate in parallel.",
          "Because only odd indices are pushed."
        ],
        correct_index: 0,
        explanation: "Even though the inner loop can pop multiple elements in a single step, an element can only be popped if it was previously pushed. With N pushes, there can be at most N total pops throughout the entire execution, guaranteeing strict O(N) time."
      },
      trace_prediction: {
        question: "For temperatures = [30, 40], what is res[0]?",
        options: [
          "1",
          "0",
          "40",
          "-1"
        ],
        correct_index: 0,
        explanation: "Day 0 (30) waits until day 1 (40) for a warmer temperature. The wait time is 1 - 0 = 1 day."
      },
      sandbox_test_cases: [
        { input: "temperatures = [73, 74, 75, 71, 69, 72, 76, 73]", expected: "[1, 1, 4, 2, 1, 1, 0, 0]" },
        { input: "temperatures = [30, 40, 50, 60]", expected: "[1, 1, 1, 0]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Largest Rectangle in Histogram",
      question: "How does a monotonic stack find the largest rectangle in a histogram?",
      approach_shift: "Use a monotonically INCREASING stack of indices. When a shorter bar is encountered, pop previous bars; the popped bar's height can extend between the new top of stack and current index."
    },
    verified_resources: [
      {
        title: "LeetCode #739: Daily Temperatures",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/daily-temperatures/",
        type: "Official Problem",
        summary: "Problem description, constraints, and test suite."
      },
      {
        title: "NeetCode: Monotonic Stack Guide",
        publisher: "NeetCode.io",
        url: "https://neetcode.io/courses/dsa-for-beginners/20",
        type: "Guide",
        summary: "Detailed visual guide to monotonic stacks and next greater element patterns."
      }
    ]
  }
,

  {
    id: "reverse-linked-list",
    title: "Reverse Linked List",
    subtitle: "Pointer Reversal & In-Place Iteration",
    topic: "Linked lists and in-place pointer manipulation",
    pattern_group: "linked-lists",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/reverse-linked-list/",
    status_type: "solved",
    learning_objectives: [
      "Master the three-pointer technique (prev, curr, next_temp) for safe in-place node redirection.",
      "Understand why pointer order is critical: overwriting curr.next destroys the remaining chain if not preserved.",
      "Identify the terminating base condition: when curr becomes None, prev points to the new head.",
      "Contrast O(1) space iterative reversal with O(N) call-stack space recursive reversal."
    ],
    prerequisites: [
      { name: "Singly Linked List Node", detail: "ListNode structure with val and next references." },
      { name: "Pointers & References", detail: "Understanding reference updates in heap-allocated objects." }
    ],
    problem_statement: "Given the head of a singly linked list, reverse the list, and return the reversed list's head.",
    examples: [
      {
        input: "head = [1, 2, 3, 4, 5]",
        output: "[5, 4, 3, 2, 1]",
        explanation: "Pointers between nodes are reversed so 5 becomes the new head and 1 points to null."
      },
      {
        input: "head = [1, 2]",
        output: "[2, 1]",
        explanation: "Node 2 points to node 1, which points to null."
      },
      {
        input: "head = []",
        output: "[]",
        explanation: "Empty list reverses to an empty list."
      }
    ],
    constraints: [
      "The number of nodes in the list is the range [0, 5000].",
      "-5000 <= Node.val <= 5000"
    ],
    intuition: "To reverse a linked list, each node must point backwards to the node that preceded it. Maintain two main pointers: prev (starts at None) and curr (starts at head).\n\nAt each node:\n1. Save curr.next into a temporary variable next_temp.\n2. Reverse the link: curr.next = prev.\n3. Advance prev to curr.\n4. Advance curr to next_temp.\nWhen curr reaches None, prev sits at the new head.",
    visual_trace: {
      description: "Reversing [1 -> 2 -> 3]:",
      steps: [
        {
          step: 1,
          state: "prev = None, curr = 1",
          action: "Save 2. Point 1 to None. Advance prev = 1, curr = 2.",
          explanation: "Node 1 now points to None (new tail)."
        },
        {
          step: 2,
          state: "prev = 1, curr = 2",
          action: "Save 3. Point 2 to 1. Advance prev = 2, curr = 3.",
          explanation: "Node 2 points backwards to 1."
        },
        {
          step: 3,
          state: "prev = 2, curr = 3",
          action: "Save None. Point 3 to 2. Advance prev = 3, curr = None.",
          explanation: "Node 3 points backwards to 2. curr is None."
        },
        {
          step: 4,
          state: "prev = 3, curr = None",
          action: "Loop terminates. Return prev (node 3).",
          explanation: "The reversed list is 3 -> 2 -> 1 -> None."
        }
      ]
    },
    baseline_solution: {
      name: "Auxiliary Array Reversal",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Extracts all node values into an array, reverses the array, and overwrites node values. Unnecessarily allocates O(N) memory.",
      code: `def reverse_list_array(head):
    vals = []
    curr = head
    while curr:
        vals.append(curr.val)
        curr = curr.next
    vals.reverse()
    curr = head
    for v in vals:
        curr.val = v
        curr = curr.next
    return head`
    },
    optimal_solution: {
      name: "Iterative In-Place Three-Pointer Reversal",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Walks the list once, redirecting next pointers backwards with O(1) auxiliary memory.",
      python_code: `class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        next_temp = curr.next  # Store remaining list
        curr.next = prev       # Reverse direction
        prev = curr            # Move prev forward
        curr = next_temp       # Move curr forward
    return prev`,
      javascript_code: `function reverseList(head) {
    let prev = null;
    let curr = head;
    while (curr !== null) {
        const nextTemp = curr.next;
        curr.next = prev;
        prev = curr;
        curr = nextTemp;
    }
    return prev;
}`,
      line_by_line: [
        {
          line: "prev = None; curr = head",
          explanation: "Initialize prev to None (the tail's next pointer in reversed list) and curr to head."
        },
        {
          line: "next_temp = curr.next",
          explanation: "Crucial step: safeguard reference to next node before overwriting curr.next."
        },
        {
          line: "curr.next = prev",
          explanation: "Inverts link so current node points backwards."
        },
        {
          line: "prev = curr; curr = next_temp",
          explanation: "Slides the two-pointer window forward by one step."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Every node is visited and its pointer redirected exactly once.",
      space: "O(1) — Only two reference pointers (prev, next_temp) are maintained in auxiliary memory."
    },
    edge_cases: [
      {
        case: "Empty list (head is None)",
        risk: "Accessing head.next throws an immediate NullPointerException/AttributeError.",
        mitigation: "The while curr loop never executes when curr is None, returning prev (None) safely."
      },
      {
        case: "Single-node list (head.next is None)",
        risk: "Accidental cycle creation if node points to itself.",
        mitigation: "curr.next is assigned to prev (None). Loop finishes, returning the single node intact."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why must next_temp be stored before updating curr.next = prev?",
        options: [
          "Because once curr.next is reassigned, the reference to the rest of the list is permanently lost.",
          "To avoid infinite recursion on the call stack.",
          "Because Python does not allow assignment to curr.next without a temporary pointer.",
          "To calculate the total length of the list."
        ],
        correct_index: 0,
        explanation: "Linked list nodes only know their immediate successor. If curr.next is overwritten without saving its target, the rest of the list becomes orphaned in memory."
      },
      trace_prediction: {
        question: "For head = [1, 2], what is prev after the first iteration of the while loop?",
        options: [
          "Node with value 1, pointing to None.",
          "Node with value 2.",
          "None.",
          "Node with value 1, pointing to 2."
        ],
        correct_index: 0,
        explanation: "During iteration 1, node 1's next pointer is set to None. prev is updated to node 1. So prev is node 1 (pointing to None)."
      },
      sandbox_test_cases: [
        { input: "head = [1, 2, 3, 4, 5]", expected: "[5, 4, 3, 2, 1]" },
        { input: "head = [1, 2]", expected: "[2, 1]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Reverse Linked List II (Sublist Reversal)",
      question: "How do you reverse a sublist from position left to position right in a single pass?",
      approach_shift: "Use a dummy head. Walk to position left - 1. Perform in-place reversals only for right - left nodes, then reconnect the left boundary's head and tail."
    },
    verified_resources: [
      {
        title: "LeetCode #206: Reverse Linked List",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/reverse-linked-list/",
        type: "Official Problem",
        summary: "Standard problem statement and test harness."
      },
      {
        title: "Tech Interview Handbook: Linked Lists",
        publisher: "Tech Interview Handbook",
        url: "https://techinterviewhandbook.org/algorithms/linked-list/",
        type: "Pattern Guide",
        summary: "In-depth guide to linked list pointer manipulation patterns."
      }
    ]
  },

  {
    id: "merge-two-sorted-lists",
    title: "Merge Two Sorted Lists",
    subtitle: "Dummy Head Sentinel & Pointer Splicing",
    topic: "Linked lists and multi-pointer comparison",
    pattern_group: "linked-lists",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/merge-two-sorted-lists/",
    status_type: "solved",
    learning_objectives: [
      "Use a dummy head sentinel node to eliminate edge cases around initializing the result list head.",
      "Compare values at the heads of two sorted lists in O(1) and splice the smaller node.",
      "Attach the non-empty remainder list in O(1) without iterating once one list is exhausted.",
      "Analyze the O(M + N) linear time bound and O(1) in-place space advantage."
    ],
    prerequisites: [
      { name: "Linked List Traversal", detail: "Advancing pointers via curr = curr.next." },
      { name: "Merge Step of MergeSort", detail: "Two-way comparison of sorted streams." }
    ],
    problem_statement: "You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the head of the merged linked list.",
    examples: [
      {
        input: "list1 = [1, 2, 4], list2 = [1, 3, 4]",
        output: "[1, 1, 2, 3, 4, 4]",
        explanation: "Nodes are spliced together in non-decreasing order."
      },
      {
        input: "list1 = [], list2 = []",
        output: "[]",
        explanation: "Both lists are empty, returning empty list."
      },
      {
        input: "list1 = [], list2 = [0]",
        output: "[0]",
        explanation: "list1 is empty; the merged result is list2 directly."
      }
    ],
    constraints: [
      "The number of nodes in both lists is in the range [0, 50].",
      "-100 <= Node.val <= 100",
      "Both list1 and list2 are sorted in non-decreasing order."
    ],
    intuition: "Because both input lists are already sorted, the smallest remaining element is always at either list1 or list2.\n\n1. Create a dummy node to anchor the result.\n2. Compare list1.val and list2.val. Attach the smaller node to tail.next and advance that list's pointer.\n3. Once one list is exhausted, splice the entire remaining segment of the other list directly with tail.next = list1 or list2.\n4. Return dummy.next.",
    visual_trace: {
      description: "Merging [1, 4] and [2, 3]:",
      steps: [
        {
          step: 1,
          state: "list1 = 1, list2 = 2, dummy -> None",
          action: "1 <= 2: attach 1. Advance list1 to 4.",
          explanation: "dummy -> 1"
        },
        {
          step: 2,
          state: "list1 = 4, list2 = 2",
          action: "2 < 4: attach 2. Advance list2 to 3.",
          explanation: "dummy -> 1 -> 2"
        },
        {
          step: 3,
          state: "list1 = 4, list2 = 3",
          action: "3 < 4: attach 3. Advance list2 to None.",
          explanation: "dummy -> 1 -> 2 -> 3"
        },
        {
          step: 4,
          state: "list2 is None, list1 = 4",
          action: "Attach remaining list1 (4) directly.",
          explanation: "Result: 1 -> 2 -> 3 -> 4"
        }
      ]
    },
    baseline_solution: {
      name: "List Values Array Merge",
      complexity: "Time: O((M+N) log(M+N)) | Space: O(M+N)",
      description: "Copies all values into an array, sorts the array, and constructs a new list. Ignores the pre-sorted property.",
      code: `def merge_lists_naive(l1, l2):
    vals = []
    while l1:
        vals.append(l1.val)
        l1 = l1.next
    while l2:
        vals.append(l2.val)
        l2 = l2.next
    vals.sort()
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next`
    },
    optimal_solution: {
      name: "Iterative Dummy-Head Two-Pointer Splice",
      complexity: "Time: O(M + N) | Space: O(1)",
      description: "Splices existing nodes in-place using a sentinel dummy head without allocating new node memory.",
      python_code: `def mergeTwoLists(list1: ListNode | None, list2: ListNode | None) -> ListNode | None:
    dummy = ListNode(-1)
    tail = dummy
    
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
        
    # Attach remaining elements in O(1)
    tail.next = list1 if list1 else list2
    return dummy.next`,
      javascript_code: `function mergeTwoLists(list1, list2) {
    const dummy = { val: -1, next: null };
    let tail = dummy;
    
    while (list1 !== null && list2 !== null) {
        if (list1.val <= list2.val) {
            tail.next = list1;
            list1 = list1.next;
        } else {
            tail.next = list2;
            list2 = list2.next;
        }
        tail = tail.next;
    }
    
    tail.next = list1 !== null ? list1 : list2;
    return dummy.next;
}`,
      line_by_line: [
        {
          line: "dummy = ListNode(-1); tail = dummy",
          explanation: "Creates dummy sentinel node; tail keeps track of current end of merged chain."
        },
        {
          line: "while list1 and list2:",
          explanation: "Iterates as long as both lists have nodes remaining to compare."
        },
        {
          line: "tail.next = list1 if list1 else list2",
          explanation: "Key O(1) step: links the entire remainder of whichever list is not yet empty."
        }
      ]
    },
    time_space_analysis: {
      time: "O(M + N) — Each comparison advances at least one pointer; every node is visited once.",
      space: "O(1) — Only dummy and tail pointers are used; nodes are spliced in place."
    },
    edge_cases: [
      {
        case: "One list is empty initially (e.g., list1 = None)",
        risk: "Unnecessary loop overhead or null checks.",
        mitigation: "while list1 and list2 loop does not trigger; tail.next immediately points to list2."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why do we write tail.next = list1 if list1 else list2 instead of continuing a loop?",
        options: [
          "Because the remaining nodes in the non-empty list are already sorted and linked; splicing the head attaches the entire rest of the list in O(1).",
          "Because while loops cannot handle single lists.",
          "To avoid an out-of-memory error.",
          "Because linked lists cannot exceed length 50."
        ],
        correct_index: 0,
        explanation: "Since list1 and list2 are already pre-sorted, once one list runs out, every remaining node in the other list is greater than any node spliced so far. Attaching the remaining pointer links all of them at once in O(1) time."
      },
      trace_prediction: {
        question: "For list1 = [1, 3] and list2 = [2], after 1 is attached, what are the next two nodes attached to the merged list?",
        options: [
          "Node 2, then Node 3.",
          "Node 3, then Node 2.",
          "Node 1, then Node 2.",
          "None."
        ],
        correct_index: 0,
        explanation: "After 1 is spliced, list1 is at 3, list2 is at 2. 2 < 3, so 2 is attached. list2 is now empty, so the remainder of list1 (3) is spliced next."
      },
      sandbox_test_cases: [
        { input: "list1 = [1, 2, 4], list2 = [1, 3, 4]", expected: "[1, 1, 2, 3, 4, 4]" },
        { input: "list1 = [], list2 = [0]", expected: "[0]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Merge K Sorted Lists",
      question: "How does merging two lists scale to merging K sorted linked lists?",
      approach_shift: "Use a min-heap of size K holding the current head of each list, or divide-and-conquer merge lists in pairs to achieve O(N log K) time."
    },
    verified_resources: [
      {
        title: "LeetCode #21: Merge Two Sorted Lists",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/merge-two-sorted-lists/",
        type: "Official Problem",
        summary: "Standard problem statement and test cases."
      }
    ]
  },

  {
    id: "merge-intervals",
    title: "Merge Intervals",
    subtitle: "Sorting Invariant & Interval Overlap Merging",
    topic: "Sorting and interval scheduling",
    pattern_group: "intervals",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/merge-intervals/",
    status_type: "solved",
    learning_objectives: [
      "Establish the sorting invariant: sorting intervals by start time guarantees overlapping intervals are adjacent.",
      "Detect interval overlap in O(1): current.start <= previous.end.",
      "Merge overlapping intervals by expanding the end bound: prev.end = max(prev.end, curr.end).",
      "Analyze the O(N log N) sorting bottleneck and O(N) space complexity."
    ],
    prerequisites: [
      { name: "Sorting by Key", detail: "Sorting an array of pairs/tuples by index 0 in Python/JavaScript." },
      { name: "Interval Representation", detail: "Closed intervals [start, end] where start <= end." }
    ],
    problem_statement: "Given an array of intervals where intervals[i] = [start_i, end_i], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
    examples: [
      {
        input: "intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]",
        output: "[[1, 6], [8, 10], [15, 18]]",
        explanation: "Since intervals [1, 3] and [2, 6] overlap, merge them into [1, 6]."
      },
      {
        input: "intervals = [[1, 4], [4, 5]]",
        output: "[[1, 5]]",
        explanation: "Intervals [1, 4] and [4, 5] touch at 4, so they are considered overlapping and merged."
      }
    ],
    constraints: [
      "1 <= intervals.length <= 10^4",
      "intervals[i].length == 2",
      "0 <= start_i <= end_i <= 10^4"
    ],
    intuition: "If intervals are unsorted, determining overlap requires pairwise checks in O(N²). By sorting intervals by their start time, we ensure that if interval B overlaps with interval A, B's start time must be between A.start and A.end.\n\nIterate through sorted intervals: if curr.start <= merged[-1].end, update merged[-1].end = max(merged[-1].end, curr.end). Otherwise, append curr as a fresh disjoint interval.",
    visual_trace: {
      description: "Merging [[1, 3], [2, 6], [8, 10]]:",
      steps: [
        {
          step: 1,
          state: "curr = [1, 3], merged = []",
          action: "Initialize merged with [1, 3].",
          explanation: "merged = [[1, 3]]"
        },
        {
          step: 2,
          state: "curr = [2, 6], last = [1, 3]",
          action: "2 <= 3 (overlap!). Update end = max(3, 6) = 6.",
          explanation: "merged = [[1, 6]]"
        },
        {
          step: 3,
          state: "curr = [8, 10], last = [1, 6]",
          action: "8 > 6 (no overlap). Append [8, 10].",
          explanation: "merged = [[1, 6], [8, 10]]"
        }
      ]
    },
    baseline_solution: {
      name: "Connected Components Graph Search",
      complexity: "Time: O(N²) | Space: O(N²)",
      description: "Builds an overlap graph where vertices are intervals and edges represent overlap, then finds connected components.",
      code: `def merge_graph(intervals):
    # O(N^2) pairwise intersection and component traversal
    pass`
    },
    optimal_solution: {
      name: "Sort-and-Sweep Invariant Merge",
      complexity: "Time: O(N log N) | Space: O(N)",
      description: "Sorts intervals by start time and performs a single linear scan merging overlapping boundaries.",
      python_code: `def merge(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
        
    # Sort strictly by start time
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    for curr in intervals[1:]:
        last_interval = merged[-1]
        
        # Check overlap condition
        if curr[0] <= last_interval[1]:
            last_interval[1] = max(last_interval[1], curr[1])
        else:
            merged.append(curr)
            
    return merged`,
      javascript_code: `function merge(intervals) {
    if (intervals.length <= 1) return intervals;
    
    intervals.sort((a, b) => a[0] - b[0]);
    const merged = [intervals[0]];
    
    for (let i = 1; i < intervals.length; i++) {
        const last = merged[merged.length - 1];
        const curr = intervals[i];
        
        if (curr[0] <= last[1]) {
            last[1] = Math.max(last[1], curr[1]);
        } else {
            merged.push(curr);
        }
    }
    return merged;
}`,
      line_by_line: [
        {
          line: "intervals.sort(key=lambda x: x[0])",
          explanation: "Sorts intervals by start timestamp in O(N log N) time."
        },
        {
          line: "if curr[0] <= last_interval[1]:",
          explanation: "Detects overlap: if current starts before or at the end of the preceding interval."
        },
        {
          line: "last_interval[1] = max(last_interval[1], curr[1])",
          explanation: "Expands end boundary if current interval extends further than previous."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N log N) — Dominated by sorting intervals. The linear merge pass takes O(N).",
      space: "O(N) — Memory to store the merged intervals list and sort stack."
    },
    edge_cases: [
      {
        case: "Interval fully enveloped (e.g., [1, 10] and [2, 5])",
        risk: "Prematurely resetting end to 5.",
        mitigation: "max(last_interval[1], curr[1]) preserves 10."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why is sorting intervals by start time essential?",
        options: [
          "It guarantees that any intervals that could possibly merge must appear consecutively in the traversal.",
          "It reduces the space complexity to O(1).",
          "It prevents negative numbers in interval endpoints.",
          "It converts the problem into binary search."
        ],
        correct_index: 0,
        explanation: "Sorting ensures that each new interval has a start time >= the previous start time. Therefore, we only ever need to compare the current interval with the last interval in merged."
      },
      trace_prediction: {
        question: "For intervals [[1, 4], [2, 3]], what is the merged output?",
        options: [
          "[[1, 4]]",
          "[[1, 3]]",
          "[[1, 4], [2, 3]]",
          "[[2, 4]]"
        ],
        correct_index: 0,
        explanation: "[2, 3] starts at 2 <= 4. max(4, 3) is 4. The interval [2, 3] is completely enveloped within [1, 4], resulting in [[1, 4]]."
      },
      sandbox_test_cases: [
        { input: "intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]", expected: "[[1, 6], [8, 10], [15, 18]]" },
        { input: "intervals = [[1, 4], [4, 5]]", expected: "[[1, 5]]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Non-overlapping Intervals",
      question: "How do you find the minimum number of intervals to remove to make the rest non-overlapping?",
      approach_shift: "Sort by end time (greedy interval scheduling); always keep the interval that finishes earliest to leave maximum room for future intervals."
    },
    verified_resources: [
      {
        title: "LeetCode #56: Merge Intervals",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/merge-intervals/",
        type: "Official Problem",
        summary: "Problem description and official test harness."
      }
    ]
  },

  {
    id: "subsets",
    title: "Subsets",
    subtitle: "State-Space Tree Exploration & Power Set Generation",
    topic: "Recursion and backtracking",
    pattern_group: "backtracking",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/subsets/",
    status_type: "solved",
    learning_objectives: [
      "Understand the 2^N state-space tree where each element is either included or excluded.",
      "Master the backtrack step: append candidate -> recurse -> pop candidate to restore state.",
      "Avoid duplicate subsets by advancing the start index strictly forward in each recursive branch.",
      "Analyze the O(N * 2^N) time and space complexity inherent to power set generation."
    ],
    prerequisites: [
      { name: "Recursion", detail: "Call stack unwinding and base conditions." },
      { name: "Combinatorics", detail: "A set of N unique elements has 2^N distinct subsets." }
    ],
    problem_statement: "Given an integer array nums of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.",
    examples: [
      {
        input: "nums = [1, 2, 3]",
        output: "[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]",
        explanation: "All 8 (2^3) distinct combinations are generated."
      },
      {
        input: "nums = [0]",
        output: "[[], [0]]",
        explanation: "The empty set and [0]."
      }
    ],
    constraints: [
      "1 <= nums.length <= 10",
      "-10 <= nums[i] <= 10",
      "All the numbers of nums are unique."
    ],
    intuition: "Think of this as a decision tree. At index 0, we can either include nums[0] or not. Alternatively, using DFS backtracking:\n\nAt each level of recursion, the current path is already a valid subset! Add path.copy() to results. Then loop i from start to len(nums), add nums[i] to path, recurse with i + 1, and pop nums[i] (backtrack).",
    visual_trace: {
      description: "Backtracking decisions for nums = [1, 2]:",
      steps: [
        {
          step: 1,
          state: "path = []",
          action: "Record [] into results. Loop i=0 (num=1).",
          explanation: "results = [[]]"
        },
        {
          step: 2,
          state: "path = [1]",
          action: "Record [1]. Recurse with start=1. Loop i=1 (num=2).",
          explanation: "results = [[], [1]]"
        },
        {
          step: 3,
          state: "path = [1, 2]",
          action: "Record [1, 2]. Recurse with start=2 (exceeds len). Backtrack: pop 2, pop 1.",
          explanation: "results = [[], [1], [1, 2]]"
        },
        {
          step: 4,
          state: "path = [2]",
          action: "Loop i=1 (num=2). Record [2]. Recurse start=2. Backtrack pop 2.",
          explanation: "results = [[], [1], [1, 2], [2]]"
        }
      ]
    },
    baseline_solution: {
      name: "Bit Manipulation Power Set",
      complexity: "Time: O(N * 2^N) | Space: O(N * 2^N)",
      description: "Iterates through all integers from 0 to 2^N - 1, using bitmask checks to include elements.",
      code: `def subsets_bits(nums):
    n = len(nums)
    res = []
    for mask in range(1 << n):
        sub = [nums[i] for i in range(n) if (mask & (1 << i))]
        res.append(sub)
    return res`
    },
    optimal_solution: {
      name: "DFS Backtracking State-Space Traversal",
      complexity: "Time: O(N * 2^N) | Space: O(N) call stack",
      description: "Recursively explores candidate subsets, using push-and-pop backtrack steps to reuse memory.",
      python_code: `def subsets(nums: list[int]) -> list[list[int]]:
    result = []
    path = []
    
    def backtrack(start: int):
        # Every node in the decision tree is a valid subset
        result.append(path.copy())
        
        for i in range(start, len(nums)):
            path.append(nums[i])      # Choose
            backtrack(i + 1)          # Explore
            path.pop()                # Un-choose (backtrack)
            
    backtrack(0)
    return result`,
      javascript_code: `function subsets(nums) {
    const result = [];
    const path = [];
    
    function backtrack(start) {
        result.push([...path]);
        
        for (let i = start; i < nums.length; i++) {
            path.push(nums[i]);
            backtrack(i + 1);
            path.pop();
        }
    }
    
    backtrack(0);
    return result;
}`,
      line_by_line: [
        {
          line: "result.append(path.copy())",
          explanation: "Copies the current path state; must be copied because path is mutated in place."
        },
        {
          line: "path.append(nums[i]); backtrack(i + 1); path.pop()",
          explanation: "The quintessential 3-part backtracking pattern: Choose, Explore, Un-choose."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N * 2^N) — There are 2^N subsets, and copying each takes O(N) time.",
      space: "O(N) — Maximum recursion depth is N."
    },
    edge_cases: [
      {
        case: "Single element nums = [1]",
        risk: "Missing the empty set.",
        mitigation: "The root of backtrack(0) immediately records [], followed by [1]."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why must path.copy() be appended to results instead of path?",
        options: [
          "Because path is a single mutable list reference; appending path would store references that change as elements are popped.",
          "Because Python prohibits lists in lists.",
          "To sort the subset in ascending order.",
          "To remove duplicate values."
        ],
        correct_index: 0,
        explanation: "Lists in Python and arrays in JavaScript are passed by reference. If you append path without copying, every entry in result would point to the same list, which ends up empty [] after backtracking completes."
      },
      trace_prediction: {
        question: "How many total subsets are generated for nums = [1, 2, 3, 4]?",
        options: [
          "16 (2^4)",
          "8",
          "24",
          "12"
        ],
        correct_index: 0,
        explanation: "Every element has 2 independent choices (included or excluded), so 2^4 = 16 subsets."
      },
      sandbox_test_cases: [
        { input: "nums = [1, 2, 3]", expected: "8 subsets including [], [1], [2], [3], [1, 2, 3]" },
        { input: "nums = [0]", expected: "[[], [0]]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Subsets II (With Duplicate Numbers)",
      question: "How do you adapt the backtracking template when nums contains duplicate numbers?",
      approach_shift: "Sort nums first. In the loop, skip duplicates with if i > start and nums[i] == nums[i-1]: continue."
    },
    verified_resources: [
      {
        title: "LeetCode #78: Subsets",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/subsets/",
        type: "Official Problem",
        summary: "Standard problem statement and test harness."
      }
    ]
  },

  {
    id: "group-anagrams",
    title: "Group Anagrams",
    subtitle: "Canonical Character Counting & Hash Bucketing",
    topic: "Hash maps and frequency tuple keys",
    pattern_group: "hash-maps",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/group-anagrams/",
    status_type: "solved",
    learning_objectives: [
      "Understand the anagram equivalence relation: two words are anagrams if and only if their sorted character representation or character frequency tuple are identical.",
      "Use hash tables with canonical keys (tuples) to bucket matching words in O(N * K) time.",
      "Avoid the O(N * K log K) sorting overhead by using a 26-element character count tuple.",
      "Analyze memory trade-offs when storing string buckets in a hash table."
    ],
    prerequisites: [
      { name: "Hash Maps & Hashable Keys", detail: "In Python, tuples are immutable and hashable; lists are not." },
      { name: "Character Frequency Counting", detail: "Counting frequencies of lowercase English letters 'a' through 'z'." }
    ],
    problem_statement: "Given an array of strings strs, group the anagrams together. You can return the answer in any order.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
    examples: [
      {
        input: 'strs = ["eat", "tea", "tan", "ate", "nat", "bat"]',
        output: '[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]',
        explanation: 'All anagram groups are clustered together.'
      },
      {
        input: 'strs = [""]',
        output: '[[""]]',
        explanation: "Empty string forms its own single-element group."
      }
    ],
    constraints: [
      "1 <= strs.length <= 10^4",
      "0 <= strs[i].length <= 100",
      "strs[i] consists of lowercase English letters."
    ],
    intuition: "Anagrams contain the exact same characters in the exact same frequencies. Therefore, if we convert each word into a canonical signature (either by sorting characters or creating a 26-element frequency tuple), all anagrams will produce the exact same key!\n\nMap each canonical key to a list of original words. Finally, return all map values.",
    visual_trace: {
      description: 'Bucketing ["eat", "tea", "tan"]:',
      steps: [
        {
          step: 1,
          word: "eat",
          canonical_key: "'aet'",
          map_state: "{ 'aet': ['eat'] }",
          explanation: "First word inserted under key 'aet'."
        },
        {
          step: 2,
          word: "tea",
          canonical_key: "'aet'",
          map_state: "{ 'aet': ['eat', 'tea'] }",
          explanation: "Matches key 'aet'! Appended to existing bucket."
        },
        {
          step: 3,
          word: "tan",
          canonical_key: "'ant'",
          map_state: "{ 'aet': ['eat', 'tea'], 'ant': ['tan'] }",
          explanation: "Produces key 'ant'. New bucket created."
        }
      ]
    },
    baseline_solution: {
      name: "Sorted String Key Hash Map",
      complexity: "Time: O(N * K log K) | Space: O(N * K)",
      description: "Sorts each string of length K to use as the dictionary key.",
      code: `from collections import defaultdict

def group_anagrams_sort(strs):
    groups = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())`
    },
    optimal_solution: {
      name: "26-Count Frequency Tuple Hash Map",
      complexity: "Time: O(N * K) | Space: O(N * K)",
      description: "Builds a 26-integer count tuple in O(K) without sorting, achieving optimal linear time.",
      python_code: `from collections import defaultdict

def groupAnagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    
    for s in strs:
        count = [0] * 26
        for ch in s:
            count[ord(ch) - ord('a')] += 1
            
        # Tuple is hashable and serves as dict key
        groups[tuple(count)].append(s)
        
    return list(groups.values())`,
      javascript_code: `function groupAnagrams(strs) {
    const map = new Map();
    
    for (const s of strs) {
        const count = new Array(26).fill(0);
        for (let i = 0; i < s.length; i++) {
            count[s.charCodeAt(i) - 97]++;
        }
        const key = count.join("#");
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(s);
    }
    return Array.from(map.values());
}`,
      line_by_line: [
        {
          line: "count[ord(ch) - ord('a')] += 1",
          explanation: "Increments character count in O(1) for each letter."
        },
        {
          line: "groups[tuple(count)].append(s)",
          explanation: "Converts list to immutable tuple to use as dictionary hash key."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N * K) where N is the number of strings and K is the maximum string length.",
      space: "O(N * K) to store the grouped strings in the hash map."
    },
    edge_cases: [
      {
        case: "Empty strings strs = ['', '']",
        risk: "Zero length strings causing index errors.",
        mitigation: "Count array remains all zeros, properly grouping all empty strings into a single bucket."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why do we convert count to a tuple in Python before using it as a dictionary key?",
        options: [
          "Lists are mutable and cannot be hashed in Python; tuples are immutable and hashable.",
          "Tuples use less memory than lists.",
          "Tuples sort faster than lists.",
          "Because dictionary keys must be strings."
        ],
        correct_index: 0,
        explanation: "Python dictionary keys must be hashable and immutable. Lists can be modified in place, so Python raises a TypeError: unhashable type: 'list'. Tuples are immutable and hashable."
      },
      trace_prediction: {
        question: "How many unique keys are created for strs = ['ab', 'ba', 'cd']?",
        options: [
          "2",
          "3",
          "1",
          "4"
        ],
        correct_index: 0,
        explanation: "'ab' and 'ba' produce the exact same frequency key, while 'cd' produces a second key. Total = 2."
      },
      sandbox_test_cases: [
        { input: 'strs = ["eat", "tea", "tan", "ate", "nat", "bat"]', expected: "3 groups" },
        { input: 'strs = ["a"]', expected: '[["a"]]' }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Find All Anagrams in a String",
      question: "How do you find all start indices of anagrams of string p in string s?",
      approach_shift: "Use a fixed-size sliding window of length len(p). Maintain character frequency counts and compare with p's count in O(1) per step."
    },
    verified_resources: [
      {
        title: "LeetCode #49: Group Anagrams",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/group-anagrams/",
        type: "Official Problem",
        summary: "Problem description and official test harness."
      }
    ]
  },

  {
    id: "valid-palindrome",
    title: "Valid Palindrome",
    subtitle: "Converging Bidirectional Pointers & Character Sanitization",
    topic: "Two pointers and symmetry verification",
    pattern_group: "two-pointers",
    difficulty: "Easy",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/valid-palindrome/",
    status_type: "solved",
    learning_objectives: [
      "Master the inward-converging two-pointer technique (left and right pointers).",
      "Sanitize inputs on-the-fly with isalnum() checks without allocating temporary string copies.",
      "Verify symmetry in O(N) time and O(1) space.",
      "Identify the termination condition: left >= right indicates the string is a valid palindrome."
    ],
    prerequisites: [
      { name: "ASCII / Alphanumeric Checks", detail: "Distinguishing alphanumeric letters/digits from spaces and punctuation." },
      { name: "Two Pointers", detail: "Converging pointers from array extremities towards the center." }
    ],
    problem_statement: "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers. Given a string s, return true if it is a palindrome, or false otherwise.",
    examples: [
      {
        input: 's = "A man, a plan, a canal: Panama"',
        output: "true",
        explanation: '"amanaplanacanalpanama" is a palindrome.'
      },
      {
        input: 's = "race a car"',
        output: "false",
        explanation: '"raceacar" is not a palindrome.'
      },
      {
        input: 's = " "',
        output: "true",
        explanation: "After removing non-alphanumeric characters, s is empty string '', which reads the same backwards."
      }
    ],
    constraints: [
      "1 <= s.length <= 2 * 10^5",
      "s consists only of printable ASCII characters."
    ],
    intuition: "Place left pointer at 0 and right pointer at len(s) - 1.\n\nWhile left < right:\n1. Skip non-alphanumeric characters at left by incrementing left.\n2. Skip non-alphanumeric characters at right by decrementing right.\n3. Compare s[left].lower() and s[right].lower(). If they mismatch, return false.\n4. Advance both pointers inward.\nIf the pointers meet without any mismatch, return true.",
    visual_trace: {
      description: 'Verifying "A man, Panama":',
      steps: [
        {
          step: 1,
          state: "left='A', right='a'",
          action: "Both alphanumeric. 'a' == 'a'. Advance left, decrement right.",
          explanation: "Characters match."
        },
        {
          step: 2,
          state: "left=' ', right='m'",
          action: "left is space: skip to 'm'. Compare 'm' and 'm'. Match!",
          explanation: "Non-alphanumeric bypassed in O(1)."
        }
      ]
    },
    baseline_solution: {
      name: "String Cleaning & Reversal",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Filters string into clean alphanumeric lowercase string, then checks clean == clean[::-1]. Allocates extra memory.",
      code: `def is_palindrome_naive(s: str) -> bool:
    clean = "".join(ch.lower() for ch in s if ch.isalnum())
    return clean == clean[::-1]`
    },
    optimal_solution: {
      name: "In-Place Converging Two Pointers",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Directly scans the string from both ends, skipping non-alphanumeric characters without allocating copies.",
      python_code: `def isPalindrome(s: str) -> bool:
    left = 0
    right = len(s) - 1
    
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
            
        if s[left].lower() != s[right].lower():
            return False
            
        left += 1
        right -= 1
        
    return True`,
      javascript_code: `function isPalindrome(s) {
    let left = 0;
    let right = s.length - 1;
    
    function isAlnum(ch) {
        const code = ch.charCodeAt(0);
        return (code >= 48 && code <= 57) || (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
    }
    
    while (left < right) {
        while (left < right && !isAlnum(s[left])) left++;
        while (left < right && !isAlnum(s[right])) right--;
        
        if (s[left].toLowerCase() !== s[right].toLowerCase()) return false;
        left++;
        right--;
    }
    return true;
}`,
      line_by_line: [
        {
          line: "while left < right and not s[left].isalnum(): left += 1",
          explanation: "Advances left past spaces, commas, and punctuation."
        },
        {
          line: "if s[left].lower() != s[right].lower(): return False",
          explanation: "Immediate early exit on first character mismatch."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Every character is examined at most twice by the converging pointers.",
      space: "O(1) — No auxiliary string copies or allocations."
    },
    edge_cases: [
      {
        case: "String with no alphanumeric characters s = '.,?!'",
        risk: "Pointers crossing out of bounds.",
        mitigation: "left < right guard inside inner while loops prevents pointer overshoot."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why is the inner while left < right condition required inside the skip loops?",
        options: [
          "To prevent left from incrementing past right when the string has consecutive punctuation characters.",
          "To ensure uppercase characters become lowercase.",
          "To avoid infinite recursion.",
          "To handle numbers."
        ],
        correct_index: 0,
        explanation: "If the remainder of the string consists solely of non-alphanumeric characters, without left < right in the inner loop, left could exceed right and walk off the end of the string."
      },
      trace_prediction: {
        question: "Does '0P' evaluate to True or False?",
        options: [
          "False, because '0' != 'p'.",
          "True, because 0 is ignored.",
          "False, because numbers are not allowed.",
          "True."
        ],
        correct_index: 0,
        explanation: "Both '0' and 'P' are alphanumeric. '0' != 'p', so it evaluates to False."
      },
      sandbox_test_cases: [
        { input: 's = "A man, a plan, a canal: Panama"', expected: "true" },
        { input: 's = "race a car"', expected: "false" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Valid Palindrome II",
      question: "Can you make the string a palindrome by deleting at most one character?",
      approach_shift: "On the first mismatch at s[left] != s[right], check if s[left+1:right+1] or s[left:right] is a palindrome."
    },
    verified_resources: [
      {
        title: "LeetCode #125: Valid Palindrome",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/valid-palindrome/",
        type: "Official Problem",
        summary: "Official problem statement and test cases."
      }
    ]
  },

  {
    id: "coin-change",
    title: "Coin Change",
    subtitle: "Unbounded Knapsack & Bottom-Up Subproblem Tabulation",
    topic: "Dynamic programming and minimization recurrence",
    pattern_group: "dynamic-programming",
    difficulty: "Medium",
    provider: "LeetCode",
    problem_url: "https://leetcode.com/problems/coin-change/",
    status_type: "solved",
    learning_objectives: [
      "Formulate the optimal substructure recurrence: dp[i] = min(dp[i], dp[i - coin] + 1).",
      "Initialize base cases: dp[0] = 0 (zero coins needed for amount 0), all other dp[i] = infinity.",
      "Identify unreachable amounts where dp[amount] remains infinity and return -1.",
      "Analyze the O(amount * len(coins)) pseudopolynomial time and O(amount) space complexity."
    ],
    prerequisites: [
      { name: "Dynamic Programming Fundamentals", detail: "Overlapping subproblems and bottom-up tabulation." },
      { name: "Unbounded Knapsack", detail: "Re-using items multiple times to reach a target capacity." }
    ],
    problem_statement: "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1. You may assume that you have an infinite number of each kind of coin.",
    examples: [
      {
        input: "coins = [1, 2, 5], amount = 11",
        output: "3",
        explanation: "11 = 5 + 5 + 1 (3 coins)."
      },
      {
        input: "coins = [2], amount = 3",
        output: "-1",
        explanation: "Cannot form 3 using only 2."
      },
      {
        input: "coins = [1], amount = 0",
        output: "0",
        explanation: "0 amount requires 0 coins."
      }
    ],
    constraints: [
      "1 <= coins.length <= 12",
      "1 <= coins[i] <= 2^31 - 1",
      "0 <= amount <= 10^4"
    ],
    intuition: "Greedy choice fails here (e.g., coins = [1, 3, 4], amount = 6: greedy takes 4 + 1 + 1 = 3 coins, but optimal is 3 + 3 = 2 coins).\n\nDefine dp[i] as the minimum coins needed for amount i.\nFor each target amount i from 1 to amount:\n  For each coin c in coins:\n    If i - c >= 0:\n      dp[i] = min(dp[i], dp[i - c] + 1)\nReturn dp[amount] if valid else -1.",
    visual_trace: {
      description: "Tabulation for coins = [1, 2, 5], amount = 5:",
      steps: [
        {
          step: 1,
          amount_target: 1,
          action: "dp[1] = min(inf, dp[1-1]+1) = 1 coin (using 1)",
          dp_state: "[0, 1, inf, inf, inf, inf]"
        },
        {
          step: 2,
          amount_target: 2,
          action: "dp[2] = min(dp[2-1]+1, dp[2-2]+1) = min(2, 1) = 1 coin (using 2)",
          dp_state: "[0, 1, 1, inf, inf, inf]"
        },
        {
          step: 3,
          amount_target: 5,
          action: "dp[5] = min(dp[5-5]+1) = 0 + 1 = 1 coin (using 5)",
          dp_state: "[0, 1, 1, 2, 2, 1]"
        }
      ]
    },
    baseline_solution: {
      name: "Naive Recursive Branching",
      complexity: "Time: O(len(coins)^amount) | Space: O(amount)",
      description: "Explores all coin combinations recursively without memoization, leading to an exponential explosion.",
      code: `def coin_change_naive(coins, amount):
    if amount == 0: return 0
    if amount < 0: return float('inf')
    return 1 + min(coin_change_naive(coins, amount - c) for c in coins)`
    },
    optimal_solution: {
      name: "Bottom-Up Dynamic Programming Tabulation",
      complexity: "Time: O(amount * len(coins)) | Space: O(amount)",
      description: "Computes minimum coins iteratively from 1 to amount using subproblem results.",
      python_code: `def coinChange(coins: list[int], amount: int) -> int:
    # Initialize DP table with infinity
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # 0 coins needed for amount 0
    
    for i in range(1, amount + 1):
        for c in coins:
            if i - c >= 0:
                dp[i] = min(dp[i], dp[i - c] + 1)
                
    return dp[amount] if dp[amount] != float('inf') else -1`,
      javascript_code: `function coinChange(coins, amount) {
    const dp = new Array(amount + 1).fill(Infinity);
    dp[0] = 0;
    
    for (let i = 1; i <= amount; i++) {
        for (const c of coins) {
            if (i - c >= 0) {
                dp[i] = Math.min(dp[i], dp[i - c] + 1);
            }
        }
    }
    return dp[amount] === Infinity ? -1 : dp[amount];
}`,
      line_by_line: [
        {
          line: "dp = [float('inf')] * (amount + 1); dp[0] = 0",
          explanation: "Initializes base subproblem: 0 amount requires 0 coins."
        },
        {
          line: "dp[i] = min(dp[i], dp[i - c] + 1)",
          explanation: "Transition recurrence: add 1 coin to optimal answer for remaining amount i - c."
        }
      ]
    },
    time_space_analysis: {
      time: "O(A * C) where A is amount and C is number of coins.",
      space: "O(A) space for the 1D dp array."
    },
    edge_cases: [
      {
        case: "amount = 0",
        risk: "Returning -1 incorrectly.",
        mitigation: "dp[0] is explicitly initialized to 0."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why does a greedy approach (always choosing the largest coin) fail for Coin Change?",
        options: [
          "Because choosing the largest coin can leave an amount that cannot be formed or requires more smaller coins than an alternative combination.",
          "Because greedy algorithms only work on trees.",
          "Because coins cannot be sorted.",
          "Because amounts can be negative."
        ],
        correct_index: 0,
        explanation: "Counterexample: coins = [1, 3, 4], amount = 6. Greedy picks 4, leaving 2 (4 + 1 + 1 = 3 coins). But DP finds 3 + 3 = 2 coins."
      },
      trace_prediction: {
        question: "If coins = [2] and amount = 3, what is dp[3]?",
        options: [
          "-1 (or infinity in the array)",
          "1",
          "2",
          "0"
        ],
        correct_index: 0,
        explanation: "3 - 2 = 1. dp[1] is infinity, so dp[3] remains infinity, which converts to -1."
      },
      sandbox_test_cases: [
        { input: "coins = [1, 2, 5], amount = 11", expected: "3" },
        { input: "coins = [2], amount = 3", expected: "-1" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Coin Change II (Total Ways)",
      question: "How do you count the number of combinations that make up the amount instead of the minimum coins?",
      approach_shift: "Change the recurrence: dp[i] += dp[i - coin], looping coins on the outside to count unique combinations rather than permutations."
    },
    verified_resources: [
      {
        title: "LeetCode #322: Coin Change",
        publisher: "LeetCode",
        url: "https://leetcode.com/problems/coin-change/",
        type: "Official Problem",
        summary: "Standard problem statement and test cases."
      }
    ]
  },

  {
    id: "ransom-note-hr",
    title: "Hash Tables: Ransom Note",
    subtitle: "Word Frequency Decrementing & Multiset Containment",
    topic: "Hash tables and frequency matching",
    pattern_group: "hash-maps",
    difficulty: "Easy",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/ctci-ransom-note/problem",
    status_type: "solved",
    learning_objectives: [
      "Understand multiset containment: checking whether magazine words can cover all words in the ransom note.",
      "Build word frequency dictionaries in O(M) time.",
      "Check note words by decrementing counts in O(N) time; if count drops below 0, return 'No'.",
      "Contrast full sorting O(M log M) with optimal O(M + N) hash table lookup."
    ],
    prerequisites: [
      { name: "Hash Maps & Frequency Tables", detail: "Using collections.Counter or standard dict for count tracking." }
    ],
    problem_statement: "Harold is a kidnapper who wrote a ransom note, but now he is worried it will be traced back to him through his handwriting. He found a magazine and wants to know if he can cut out whole words from it to assemble his note. The words in his note are case-sensitive and he must use whole words.\n\nGiven the words in the magazine and the words in the ransom note, print 'Yes' if he can replicate his note exactly using the magazine; otherwise, print 'No'.",
    examples: [
      {
        input: "magazine = ['give', 'me', 'one', 'grand', 'today', 'night'], note = ['give', 'one', 'grand', 'today']",
        output: "'Yes'",
        explanation: "All words exist in the magazine with sufficient frequency."
      },
      {
        input: "magazine = ['two', 'times', 'three', 'is', 'not', 'four'], note = ['two', 'times', 'two', 'is', 'four']",
        output: "'No'",
        explanation: "Word 'two' appears only once in magazine but is required twice in note."
      }
    ],
    constraints: [
      "1 <= m, n <= 30000",
      "1 <= length of word <= 5",
      "Each word consists of English letters and is case-sensitive."
    ],
    intuition: "Count the frequency of each word in the magazine using a hash map. Then iterate through each word in the note:\nIf word not in map or map[word] == 0, return 'No'.\nOtherwise, decrement map[word] by 1.\nIf all words are satisfied, return 'Yes'.",
    visual_trace: {
      description: "Checking note ['two', 'two'] against magazine ['two', 'times']:",
      steps: [
        {
          step: 1,
          action: "Build magazine map: {'two': 1, 'times': 1}",
          state: "Ready for note checks"
        },
        {
          step: 2,
          action: "Check first 'two': found (count = 1). Decrement to 0.",
          state: "{'two': 0, 'times': 1}"
        },
        {
          step: 3,
          action: "Check second 'two': count is 0! Insufficient word availability.",
          state: "Output: 'No'"
        }
      ]
    },
    baseline_solution: {
      name: "List Removal Search",
      complexity: "Time: O(M * N) | Space: O(1)",
      description: "Calls magazine.remove(word) for each word in note. list.remove() is O(M), resulting in quadratic O(M * N) time.",
      code: `def checkMagazine_naive(magazine, note):
    for word in note:
        if word in magazine:
            magazine.remove(word)
        else:
            print("No")
            return
    print("Yes")`
    },
    optimal_solution: {
      name: "Hash Map Word Frequency Counting",
      complexity: "Time: O(M + N) | Space: O(M)",
      description: "Builds word counts from magazine in O(M) and satisfies note in O(N).",
      python_code: `from collections import Counter

def checkMagazine(magazine: list[str], note: list[str]) -> str:
    mag_counts = Counter(magazine)
    
    for word in note:
        if mag_counts[word] <= 0:
            return "No"
        mag_counts[word] -= 1
        
    return "Yes"`,
      javascript_code: `function checkMagazine(magazine, note) {
    const counts = new Map();
    for (const word of magazine) {
        counts.set(word, (counts.get(word) || 0) + 1);
    }
    
    for (const word of note) {
        const available = counts.get(word) || 0;
        if (available <= 0) return "No";
        counts.set(word, available - 1);
    }
    return "Yes";
}`,
      line_by_line: [
        {
          line: "mag_counts = Counter(magazine)",
          explanation: "Builds word frequency histogram in O(M) time."
        },
        {
          line: "if mag_counts[word] <= 0: return 'No'",
          explanation: "Verifies that word exists with remaining count > 0."
        }
      ]
    },
    time_space_analysis: {
      time: "O(M + N) — Linear scan over magazine words followed by note words.",
      space: "O(M) — Storage for magazine word counts in the hash table."
    },
    edge_cases: [
      {
        case: "Case sensitivity ('Give' vs 'give')",
        risk: "Mismatched casing causing false negatives.",
        mitigation: "Keep exact case as required by problem specifications."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why does using magazine.remove(word) cause Time Limit Exceeded on HackerRank?",
        options: [
          "magazine.remove() scans the array in O(M) time for each of the N words, causing O(M * N) ~ 9 * 10^8 operations.",
          "Because HackerRank does not support Python lists.",
          "Because remove() throws an uncatchable exception.",
          "Because sets cannot be removed."
        ],
        correct_index: 0,
        explanation: "Array removal requires searching and shifting elements in O(M). For M, N = 30,000, 30,000^2 = 900,000,000 operations, which times out."
      },
      trace_prediction: {
        question: "If magazine = ['a', 'b'] and note = ['a', 'a'], what is returned?",
        options: [
          "'No'",
          "'Yes'",
          "False",
          "None"
        ],
        correct_index: 0,
        explanation: "The letter 'a' is only available once in the magazine, so the second 'a' cannot be formed, returning 'No'."
      },
      sandbox_test_cases: [
        { input: "magazine = ['give', 'me', 'one'], note = ['give', 'one']", expected: "'Yes'" },
        { input: "magazine = ['two'], note = ['two', 'two']", expected: "'No'" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Two Strings",
      question: "How do you check if two strings share a common substring?",
      approach_shift: "A common substring of any length exists if and only if they share at least one single character: set(s1) & set(s2)."
    },
    verified_resources: [
      {
        title: "HackerRank: Hash Tables: Ransom Note",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/ctci-ransom-note/problem",
        type: "Official Problem",
        summary: "Official HackerRank interview preparation kit problem."
      }
    ]
  },

  {
    id: "balanced-brackets-hr",
    title: "Balanced Brackets",
    subtitle: "LIFO Bracket Matching & Delimiter Verification",
    topic: "Stacks and string grammar parsing",
    pattern_group: "monotonic-stack",
    difficulty: "Medium",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/balanced-brackets/problem",
    status_type: "solved",
    learning_objectives: [
      "Master the Last-In, First-Out (LIFO) stack invariant for nested grammar matching.",
      "Map closing brackets to opening brackets in a constant-time dictionary.",
      "Identify invalid cases: popping from an empty stack or mismatched bracket types.",
      "Check final termination: stack must be empty when string iteration finishes."
    ],
    prerequisites: [
      { name: "Stack Data Structure", detail: "LIFO operations (append, pop) in O(1)." }
    ],
    problem_statement: "A bracket is considered to be any one of the following characters: '(', ')', '{', '}', '[', or ']'. A sequence of brackets is balanced if every opening bracket has a matching closing bracket of the same type and brackets are properly nested.\n\nGiven a string of brackets, determine whether it is balanced. If balanced, return 'YES'; otherwise, return 'NO'.",
    examples: [
      {
        input: "s = '{[()]}'",
        output: "'YES'",
        explanation: "All brackets are properly matched and nested."
      },
      {
        input: "s = '{[(])}'",
        output: "'NO'",
        explanation: "] closes before matching ()."
      },
      {
        input: "s = '{{[[(())]]}}'",
        output: "'YES'",
        explanation: "All brackets are balanced."
      }
    ],
    constraints: [
      "1 <= s.length <= 1000",
      "s consists only of '(){}[]'."
    ],
    intuition: "When we see an opening bracket ('(', '{', '['), push it onto the stack. When we see a closing bracket (')', '}', ']'), pop the top of the stack and check if it matches the closing bracket. If the stack is empty or the popped element doesn't match, return 'NO'. After scanning all characters, if the stack is empty, return 'YES'.",
    visual_trace: {
      description: "Evaluating '{[()]}':",
      steps: [
        { step: 1, action: "Push '{', push '[', push '('", state: "stack = ['{', '[', '(']" },
        { step: 2, action: "Seen ')': pop '(', matches ')'", state: "stack = ['{', '[']" },
        { step: 3, action: "Seen ']': pop '[', matches ']'", state: "stack = ['{']" },
        { step: 4, action: "Seen '}': pop '{', matches '}'", state: "stack = [] -> Return 'YES'" }
      ]
    },
    baseline_solution: {
      name: "Repeated String Replacement",
      complexity: "Time: O(N²) | Space: O(N)",
      description: "Repeatedly replaces '()', '[]', '{}' with '' until no changes occur. Quadratic due to string re-creation.",
      code: `def is_balanced_replace(s):
    prev = ""
    while prev != s:
        prev = s
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return "YES" if not s else "NO"`
    },
    optimal_solution: {
      name: "LIFO Stack Matching",
      complexity: "Time: O(N) | Space: O(N)",
      description: "Single linear pass using a stack to match delimiters in O(1) per character.",
      python_code: `def isBalanced(s: str) -> str:
    bracket_map = {')': '(', '}': '{', ']': '['}
    stack = []
    
    for ch in s:
        if ch in bracket_map:  # Closing bracket
            top_element = stack.pop() if stack else '#'
            if bracket_map[ch] != top_element:
                return "NO"
        else:  # Opening bracket
            stack.append(ch)
            
    return "YES" if not stack else "NO"`,
      javascript_code: `function isBalanced(s) {
    const map = { ')': '(', '}': '{', ']': '[' };
    const stack = [];
    
    for (let i = 0; i < s.length; i++) {
        const ch = s[i];
        if (map[ch]) {
            const top = stack.length ? stack.pop() : '#';
            if (map[ch] !== top) return "NO";
        } else {
            stack.push(ch);
        }
    }
    return stack.length === 0 ? "YES" : "NO";
}`,
      line_by_line: [
        {
          line: "top_element = stack.pop() if stack else '#'",
          explanation: "Safely pops if stack is non-empty; otherwise uses sentinel '#' to detect premature closing."
        },
        {
          line: "return 'YES' if not stack else 'NO'",
          explanation: "Guarantees that all opened brackets were successfully closed."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Scans the string of length N once.",
      space: "O(N) — In the worst case (all opening brackets), stack stores N characters."
    },
    edge_cases: [
      {
        case: "Starts with closing bracket s = ']'",
        risk: "Popping from an empty stack.",
        mitigation: "stack check returns sentinel '#' and exits immediately."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why must the stack be checked for empty status at the end (not stack)?",
        options: [
          "To catch unclosed opening brackets like '(((' where no mismatches occurred during iteration.",
          "To reset memory.",
          "Because HackerRank tests require it.",
          "To reverse the brackets."
        ],
        correct_index: 0,
        explanation: "If s = '(((', all characters are opening brackets and get pushed without ever hitting a closing bracket check. Only checking not stack at the end catches this."
      },
      trace_prediction: {
        question: "What is returned for s = '(()'?",
        options: [
          "'NO'",
          "'YES'",
          "Error",
          "None"
        ],
        correct_index: 0,
        explanation: "One '(' remains on the stack at the end, so it returns 'NO'."
      },
      sandbox_test_cases: [
        { input: "s = '{[()]}'", expected: "'YES'" },
        { input: "s = '{[(])}'", expected: "'NO'" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Minimum Add to Make Parentheses Valid",
      question: "How do you count the minimum number of parentheses required to balance a string?",
      approach_shift: "Maintain open count and needed count: if '(', increment open; if ')', decrement open if open > 0 else increment needed."
    },
    verified_resources: [
      {
        title: "HackerRank: Balanced Brackets",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/balanced-brackets/problem",
        type: "Official Problem",
        summary: "Standard problem statement and test cases."
      }
    ]
  },

  {
    id: "roads-and-libraries-hr",
    title: "Roads and Libraries",
    subtitle: "Connected Components & Greedy Minimum Spanning Tree",
    topic: "Graphs, BFS/DFS traversal, and component discovery",
    pattern_group: "graphs",
    difficulty: "Medium",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/torque-and-development/problem",
    status_type: "solved",
    learning_objectives: [
      "Model civil engineering problems as graph connected components.",
      "Formulate greedy cost comparison: if c_lib <= c_road, build a library in every city.",
      "Use BFS or DFS to discover the size of each connected component in O(V + E) time.",
      "Calculate minimum cost per component: 1 library + (size - 1) roads."
    ],
    prerequisites: [
      { name: "Graph Adjacency List", detail: "Representing undirected edges using dict of lists." },
      { name: "Connected Components", detail: "Traversing all nodes reachable from a starting vertex." }
    ],
    problem_statement: "The Ruler of HackerLand wants to provide all citizens with library access. There are n cities numbered 1 to n. Road building costs c_road per road, and building a library in a city costs c_lib. Citizens have library access if their city has a library or can reach a city with a library via road.\n\nDetermine the minimum cost to provide library access to all citizens.",
    examples: [
      {
        input: "n = 3, c_lib = 2, c_road = 1, cities = [[1, 2], [3, 1], [2, 3]]",
        output: "4",
        explanation: "All 3 cities form 1 connected component. 1 library (2) + 2 roads (2 * 1) = 4."
      },
      {
        input: "n = 6, c_lib = 2, c_road = 5, cities = [[1, 3], [3, 4], [2, 4], [1, 2], [2, 3], [5, 6]]",
        output: "12",
        explanation: "c_lib (2) <= c_road (5), so it is cheaper to build a library in all 6 cities: 6 * 2 = 12."
      }
    ],
    constraints: [
      "1 <= n <= 10^5",
      "0 <= m <= min(10^5, n*(n-1)/2)",
      "1 <= c_road, c_lib <= 10^5"
    ],
    intuition: "Key Insight: If c_lib <= c_road, building roads is never cheaper than building libraries! Simply build a library in all n cities: cost = n * c_lib.\n\nOtherwise (c_road < c_lib), in any connected component of size k, the optimal strategy is to build 1 library and (k - 1) roads to connect all other cities to it. Total cost for that component is c_lib + (k - 1) * c_road. Sum across all connected components.",
    visual_trace: {
      description: "Analyzing n=3, c_lib=2, c_road=1 with edge [1, 2]:",
      steps: [
        { step: 1, action: "Component 1: cities {1, 2} (size 2)", cost: "1 lib (2) + 1 road (1) = 3" },
        { step: 2, action: "Component 2: city {3} isolated (size 1)", cost: "1 lib (2) + 0 road = 2" },
        { step: 3, action: "Total Cost", cost: "3 + 2 = 5" }
      ]
    },
    baseline_solution: {
      name: "Kruskal's Full MST with Virtual Source",
      complexity: "Time: O(E log E) | Space: O(V + E)",
      description: "Connects a virtual super-source to all cities with edge weight c_lib and runs Kruskal's algorithm.",
      code: `def roadsAndLibraries_kruskal(n, c_lib, c_road, cities):
    # Standard Kruskal's MST
    pass`
    },
    optimal_solution: {
      name: "BFS/DFS Connected Component Counting",
      complexity: "Time: O(V + E) | Space: O(V + E)",
      description: "Counts component sizes with DFS/BFS in linear time.",
      python_code: `from collections import defaultdict

def roadsAndLibraries(n: int, c_lib: int, c_road: int, cities: list[list[int]]) -> int:
    # If library is cheaper than or equal to road, build libraries everywhere
    if c_lib <= c_road:
        return n * c_lib
        
    adj = defaultdict(list)
    for u, v in cities:
        adj[u].append(v)
        adj[v].append(u)
        
    visited = set()
    total_cost = 0
    
    def dfs(node):
        size = 1
        visited.add(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                size += dfs(neighbor)
        return size
        
    for city in range(1, n + 1):
        if city not in visited:
            comp_size = dfs(city)
            total_cost += c_lib + (comp_size - 1) * c_road
            
    return total_cost`,
      javascript_code: `function roadsAndLibraries(n, c_lib, c_road, cities) {
    if (c_lib <= c_road) return n * c_lib;
    
    const adj = Array.from({ length: n + 1 }, () => []);
    for (const [u, v] of cities) {
        adj[u].push(v);
        adj[v].push(u);
    }
    
    const visited = new Uint8Array(n + 1);
    let totalCost = 0;
    
    function dfs(node) {
        let size = 1;
        visited[node] = 1;
        for (const neighbor of adj[node]) {
            if (!visited[neighbor]) size += dfs(neighbor);
        }
        return size;
    }
    
    for (let i = 1; i <= n; i++) {
        if (!visited[i]) {
            const compSize = dfs(i);
            totalCost += c_lib + (compSize - 1) * c_road;
        }
    }
    return totalCost;
}`,
      line_by_line: [
        {
          line: "if c_lib <= c_road: return n * c_lib",
          explanation: "Essential greedy short-circuit: avoids graph construction when roads offer no savings."
        },
        {
          line: "total_cost += c_lib + (comp_size - 1) * c_road",
          explanation: "Each component needs exactly 1 library and a spanning tree of size - 1 roads."
        }
      ]
    },
    time_space_analysis: {
      time: "O(V + E) — Each city and road is traversed once during DFS.",
      space: "O(V + E) for adjacency list and visited set."
    },
    edge_cases: [
      {
        case: "No roads (cities is empty)",
        risk: "Missing edges handling.",
        mitigation: "Each city is its own component of size 1: n * c_lib."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "When c_lib <= c_road, why do we never build roads?",
        options: [
          "Because building a road costs more than or equal to putting a library in that city directly, offering zero cost savings.",
          "Because graphs cannot have cycles.",
          "Because libraries must be on roads.",
          "Because n is always odd."
        ],
        correct_index: 0,
        explanation: "If a road costs $5 and a library costs $2, building a road to connect to another library costs $5, whereas building a library directly in that city costs only $2."
      },
      trace_prediction: {
        question: "For 4 cities in one connected component with c_lib = 5, c_road = 2, what is the cost?",
        options: [
          "11 (5 + 3 * 2)",
          "13",
          "20",
          "8"
        ],
        correct_index: 0,
        explanation: "1 library (5) + 3 roads (3 * 2 = 6) = 11."
      },
      sandbox_test_cases: [
        { input: "n = 3, c_lib = 2, c_road = 1, cities = [[1, 2], [3, 1], [2, 3]]", expected: "4" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Number of Connected Components in an Undirected Graph",
      question: "How do you count the number of disconnected subgraphs in an undirected graph?",
      approach_shift: "Use the same DFS/BFS loop or Disjoint Set Union (Union-Find) to count component roots."
    },
    verified_resources: [
      {
        title: "HackerRank: Roads and Libraries",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/torque-and-development/problem",
        type: "Official Problem",
        summary: "Graph traversal interview preparation problem."
      }
    ]
  },

  {
    id: "max-array-sum-hr",
    title: "Max Array Sum",
    subtitle: "Non-Adjacent Subset Sum & Optimal Substructure",
    topic: "Dynamic programming and state selection",
    pattern_group: "dynamic-programming",
    difficulty: "Medium",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/max-array-sum/problem",
    status_type: "solved",
    learning_objectives: [
      "Understand the classic House Robber / Non-adjacent max subset sum state transition.",
      "Formulate recurrence: dp[i] = max(dp[i-1], arr[i] + max(0, dp[i-2]), arr[i]).",
      "Compress state from O(N) array to two variables: prev2 and prev1 in O(1) space.",
      "Handle negative integers safely without corrupting max sums."
    ],
    prerequisites: [
      { name: "Dynamic Programming", detail: "State transitions without adjacent element selection." }
    ],
    problem_statement: "Given an array of integers, find the subset of non-adjacent elements with the maximum sum. Calculate the sum of that subset. It is possible that the maximum sum is 0 if all numbers are negative.",
    examples: [
      {
        input: "arr = [3, 7, 4, 6, 5]",
        output: "13",
        explanation: "The non-adjacent subset [7, 6] produces sum 13."
      },
      {
        input: "arr = [2, 1, 5, 8, 4]",
        output: "11",
        explanation: "Subset [2, 5, 4] produces sum 11."
      }
    ],
    constraints: [
      "1 <= arr.length <= 10^5",
      "-10^4 <= arr[i] <= 10^4"
    ],
    intuition: "At each element arr[i], you have two choices:\n1. Skip arr[i]: the max sum is the same as dp[i-1].\n2. Take arr[i]: you cannot take arr[i-1], so add arr[i] to dp[i-2] (if positive).\nTherefore, dp[i] = max(dp[i-1], arr[i] + max(0, dp[i-2]), arr[i]).\nOnly the previous two states are needed, enabling O(1) memory.",
    visual_trace: {
      description: "Tracing [3, 7, 4, 6]:",
      steps: [
        { step: 1, action: "arr[0] = 3", state: "dp[0] = 3" },
        { step: 2, action: "arr[1] = 7", state: "dp[1] = max(3, 7) = 7" },
        { step: 3, action: "arr[2] = 4", state: "dp[2] = max(7, 4 + 3) = 7" },
        { step: 4, action: "arr[3] = 6", state: "dp[3] = max(7, 6 + 7) = 13" }
      ]
    },
    baseline_solution: {
      name: "Recursive Branching",
      complexity: "Time: O(2^N) | Space: O(N)",
      description: "Explores include/exclude choices recursively without caching.",
      code: `def max_array_sum_rec(arr, i=0):
    if i >= len(arr): return 0
    return max(arr[i] + max_array_sum_rec(arr, i + 2), max_array_sum_rec(arr, i + 1))`
    },
    optimal_solution: {
      name: "O(1) Space Tabulation",
      complexity: "Time: O(N) | Space: O(1)",
      description: "Computes non-adjacent max sum in linear time with two state registers.",
      python_code: `def maxSubsetSum(arr: list[int]) -> int:
    if not arr:
        return 0
    if len(arr) == 1:
        return max(0, arr[0])
        
    prev2 = max(0, arr[0])
    prev1 = max(prev2, arr[1])
    
    for i in range(2, len(arr)):
        curr = max(prev1, arr[i] + prev2, arr[i])
        prev2 = prev1
        prev1 = curr
        
    return prev1`,
      javascript_code: `function maxSubsetSum(arr) {
    if (arr.length === 0) return 0;
    if (arr.length === 1) return Math.max(0, arr[0]);
    
    let prev2 = Math.max(0, arr[0]);
    let prev1 = Math.max(prev2, arr[1]);
    
    for (let i = 2; i < arr.length; i++) {
        const curr = Math.max(prev1, arr[i] + prev2, arr[i]);
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}`,
      line_by_line: [
        {
          line: "curr = max(prev1, arr[i] + prev2, arr[i])",
          explanation: "Selects the optimal of: skipping current, taking current + subproblem i-2, or starting anew with current."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N) — Single pass across the array.",
      space: "O(1) — Constant memory using prev1 and prev2 registers."
    },
    edge_cases: [
      {
        case: "All negative numbers arr = [-2, -1, -3]",
        risk: "Returning negative sum.",
        mitigation: "max(0, ...) ensures result never drops below 0 for an empty subset."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why can't we take arr[i-1] when including arr[i]?",
        options: [
          "The problem explicitly forbids adjacent elements in the subset.",
          "Because arr[i-1] is negative.",
          "To avoid infinite recursion.",
          "Because arrays cannot be indexed twice."
        ],
        correct_index: 0,
        explanation: "The problem condition requires non-adjacent elements; if index i is chosen, index i-1 is disqualified."
      },
      trace_prediction: {
        question: "For arr = [2, 1, 5, 8, 4], what is the maximum non-adjacent sum?",
        options: [
          "11 (2 + 5 + 4)",
          "10",
          "8",
          "13"
        ],
        correct_index: 0,
        explanation: "Elements at indices 0, 2, 4 give 2 + 5 + 4 = 11. Alternatively index 3 (8) + index 0 (2) gives 10. Maximum is 11."
      },
      sandbox_test_cases: [
        { input: "arr = [3, 7, 4, 6, 5]", expected: "13" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: House Robber II (Circular Street)",
      question: "How do you solve non-adjacent max sum when the array is circular (first and last elements are adjacent)?",
      approach_shift: "Run the algorithm twice: once for arr[0:-1] (excluding last) and once for arr[1:] (excluding first), then take max."
    },
    verified_resources: [
      {
        title: "HackerRank: Max Array Sum",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/max-array-sum/problem",
        type: "Official Problem",
        summary: "Classic DP interview preparation problem."
      }
    ]
  },

  {
    id: "recursive-digit-sum-hr",
    title: "Recursive Digit Sum",
    subtitle: "Super Digit Reduction & Number Theory Invariants",
    topic: "Recursion and digital root mathematics",
    pattern_group: "backtracking",
    difficulty: "Medium",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/recursive-digit-sum/problem",
    status_type: "solved",
    learning_objectives: [
      "Understand digital root recursion: repeatedly summing digits until a single digit remains.",
      "Leverage the multiplication property: superDigit(p) = superDigit(superDigit(n) * k) to avoid string memory overflow.",
      "Recognize the modulo 9 digital root congruence theorem.",
      "Analyze recursive call stack depth: at most O(log10 N) levels."
    ],
    prerequisites: [
      { name: "Recursion & Base Cases", detail: "Terminating when a single digit integer (x < 10) is reached." },
      { name: "Modular Arithmetic", detail: "Properties of numbers modulo 9." }
    ],
    problem_statement: "We define super digit of an integer x using the following rules: If x has only 1 digit, then its super digit is x. Otherwise, the super digit of x is equal to the super digit of the sum of the digits of x.\n\nYou are given two numbers, n and k. The number p is created by concatenating string n k times. Find the super digit of p.",
    examples: [
      {
        input: "n = '148', k = 3",
        output: "3",
        explanation: "p = '148148148'. Sum = 1+4+8 + 1+4+8 + 1+4+8 = 39. 3 + 9 = 12. 1 + 2 = 3."
      },
      {
        input: "n = '9875', k = 4",
        output: "8",
        explanation: "Sum of digits in n is 29. 29 * 4 = 116. 1 + 1 + 6 = 8."
      }
    ],
    constraints: [
      "1 <= n <= 10^100000",
      "1 <= k <= 10^5"
    ],
    intuition: "Crucial Insight: Concatenating n k times creates a string of up to 10^100000 characters, which causes Memory Limit Exceeded!\n\nInstead of building the string, sum the digits of n once: sum_n = sum(int(c) for c in n). Then initial_sum = sum_n * k. Now recursively compute superDigit(str(initial_sum)). After just one step, the number shrinks to a small integer!",
    visual_trace: {
      description: "Computing superDigit('148', 3):",
      steps: [
        { step: 1, action: "Sum digits of '148': 1 + 4 + 8 = 13", state: "sum_n = 13" },
        { step: 2, action: "Multiply by k=3: 13 * 3 = 39", state: "num = 39" },
        { step: 3, action: "Sum digits of 39: 3 + 9 = 12", state: "num = 12" },
        { step: 4, action: "Sum digits of 12: 1 + 2 = 3", state: "Single digit! Return 3" }
      ]
    },
    baseline_solution: {
      name: "Naive String Concatenation",
      complexity: "Time: O(k * len(n)) | Space: O(k * len(n))",
      description: "Allocates p = n * k directly in memory, crashing with Out of Memory for large k.",
      code: `def superDigit_naive(n, k):
    p = n * k
    while len(p) > 1:
        p = str(sum(int(c) for c in p))
    return int(p)`
    },
    optimal_solution: {
      name: "Digit Sum Multiplication Recursion",
      complexity: "Time: O(len(n)) | Space: O(log N)",
      description: "Sums digits once and multiplies by k before recursing.",
      python_code: `def superDigit(n: str, k: int) -> int:
    def helper(num_str: str) -> int:
        if len(num_str) == 1:
            return int(num_str)
        digit_sum = sum(int(c) for c in num_str)
        return helper(str(digit_sum))
        
    initial_sum = sum(int(c) for c in n) * k
    return helper(str(initial_sum))`,
      javascript_code: `function superDigit(n, k) {
    function helper(numStr) {
        if (numStr.length === 1) return parseInt(numStr, 10);
        let sum = 0;
        for (let i = 0; i < numStr.length; i++) {
            sum += parseInt(numStr[i], 10);
        }
        return helper(sum.toString());
    }
    
    let sumN = 0;
    for (let i = 0; i < n.length; i++) {
        sumN += parseInt(n[i], 10);
    }
    return helper((sumN * k).toString());
}`,
      line_by_line: [
        {
          line: "initial_sum = sum(int(c) for c in n) * k",
          explanation: "Bypasses massive string concatenation by exploiting distributive property of digit sums."
        },
        {
          line: "if len(num_str) == 1: return int(num_str)",
          explanation: "Recursive base condition: single digit terminal state."
        }
      ]
    },
    time_space_analysis: {
      time: "O(len(n)) — One pass over n's characters; subsequent recursive calls process numbers < 1000.",
      space: "O(log10(initial_sum)) recursive call stack space."
    },
    edge_cases: [
      {
        case: "Single digit initial input n = '7', k = 1",
        risk: "Unnecessary recursion.",
        mitigation: "helper immediately returns 7 on first check."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why does n * k cause a memory crash on HackerRank when n has 100,000 digits and k = 100,000?",
        options: [
          "n * k would allocate a 10 GB string in memory, vastly exceeding available RAM.",
          "Because strings cannot be multiplied in Python.",
          "Because recursive functions cannot accept strings.",
          "Because HackerRank limits string length to 10."
        ],
        correct_index: 0,
        explanation: "100,000 * 100,000 = 10,000,000,000 characters (~10 GB), which immediately causes a Memory Limit Exceeded crash."
      },
      trace_prediction: {
        question: "What is superDigit('9875', 1)?",
        options: [
          "2",
          "8",
          "9",
          "5"
        ],
        correct_index: 0,
        explanation: "9 + 8 + 7 + 5 = 29. 2 + 9 = 11. 1 + 1 = 2."
      },
      sandbox_test_cases: [
        { input: "n = '148', k = 3", expected: "3" },
        { input: "n = '9875', k = 4", expected: "8" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Add Digits (LeetCode #258)",
      question: "How do you compute the digital root of a number in O(1) time without any loops?",
      approach_shift: "Use the modulo 9 property: if num == 0 return 0; else return 1 + (num - 1) % 9."
    },
    verified_resources: [
      {
        title: "HackerRank: Recursive Digit Sum",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/recursive-digit-sum/problem",
        type: "Official Problem",
        summary: "Recursion and mathematical optimization challenge."
      }
    ]
  },

  {
    id: "ice-cream-parlor-hr",
    title: "Ice Cream Parlor (Binary Search)",
    subtitle: "Target Cost Complement Search in Sorted Cost Arrays",
    topic: "Binary search and value-index pairing",
    pattern_group: "binary-search",
    difficulty: "Easy",
    provider: "HackerRank",
    problem_url: "https://www.hackerrank.com/challenges/icecream-parlor/problem",
    status_type: "solved",
    learning_objectives: [
      "Pair values with original 1-based indices before sorting: [(cost, idx+1)].",
      "Apply binary search to locate the complement target = money - current_cost in O(log N) time.",
      "Avoid selecting the same index twice when two items have identical prices.",
      "Contrast O(N log N) binary search with O(N) hash map approaches."
    ],
    prerequisites: [
      { name: "Binary Search", detail: "Logarithmic halving on sorted collections." },
      { name: "Index Preservation", detail: "Tracking original indices when sorting." }
    ],
    problem_statement: "Two friends like to pool their money each time they go to the ice cream parlor. They always choose two distinct flavors that together cost all of their money.\n\nGiven a list of prices for the flavors of ice cream and the amount of money they have, determine the 1-based indices of the two flavors they will purchase. Return the smaller index first.",
    examples: [
      {
        input: "m = 4, arr = [1, 4, 5, 3, 2]",
        output: "[1, 4]",
        explanation: "Flavors at 1-based indices 1 and 4 cost 1 + 3 = 4."
      },
      {
        input: "m = 4, arr = [2, 2, 4, 3]",
        output: "[1, 2]",
        explanation: "Flavors at indices 1 and 2 cost 2 + 2 = 4."
      }
    ],
    constraints: [
      "1 <= t <= 50 (test cases)",
      "2 <= m <= 10^4 (money)",
      "2 <= n <= 10^4 (flavors)",
      "1 <= cost[i] <= 10^4"
    ],
    intuition: "For each flavor with price cost, its pair must cost complement = m - cost.\n\nPreserve original 1-based indices: sorted_costs = sorted([(cost, i + 1) for i, cost in enumerate(arr)]).\nFor each item, binary search for complement in sorted_costs. When found, ensure the indices are distinct, sort the two indices ascending, and return.",
    visual_trace: {
      description: "Solving m = 4, arr = [1, 4, 5, 3, 2]:",
      steps: [
        { step: 1, action: "Pair with indices: [(1, 1), (4, 2), (5, 3), (3, 4), (2, 5)]", state: "Indexed" },
        { step: 2, action: "Sort by cost: [(1, 1), (2, 5), (3, 4), (4, 2), (5, 3)]", state: "Sorted" },
        { step: 3, action: "At (1, 1), target is 4 - 1 = 3. Binary search finds (3, 4) at index 4!", state: "Found!" },
        { step: 4, action: "Indices are 1 and 4. Sorted: [1, 4]", state: "Done" }
      ]
    },
    baseline_solution: {
      name: "Nested Pair Search",
      complexity: "Time: O(N²) | Space: O(1)",
      description: "Examines all pairs (i, j) with nested loops.",
      code: `def icecreamParlor_naive(m, arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] + arr[j] == m:
                return [i + 1, j + 1]`
    },
    optimal_solution: {
      name: "Binary Search with Preserved Indices",
      complexity: "Time: O(N log N) | Space: O(N)",
      description: "Sorts indexed pairs and binary searches for the target complement in O(log N) per item.",
      python_code: `import bisect

def icecreamParlor(m: int, arr: list[int]) -> list[int]:
    indexed = sorted((cost, idx + 1) for idx, cost in enumerate(arr))
    costs_only = [c[0] for c in indexed]
    
    for i, (cost, orig_idx) in enumerate(indexed):
        target = m - cost
        # Binary search for target in costs_only
        pos = bisect.bisect_left(costs_only, target)
        while pos < len(indexed) and indexed[pos][0] == target:
            if indexed[pos][1] != orig_idx:
                return sorted([orig_idx, indexed[pos][1]])
            pos += 1
            
    return []`,
      javascript_code: `function icecreamParlor(m, arr) {
    const indexed = arr.map((cost, idx) => ({ cost, idx: idx + 1 }));
    indexed.sort((a, b) => a.cost - b.cost);
    
    for (let i = 0; i < indexed.length; i++) {
        const target = m - indexed[i].cost;
        let left = 0, right = indexed.length - 1;
        while (left <= right) {
            const mid = Math.floor((left + right) / 2);
            if (indexed[mid].cost === target) {
                if (indexed[mid].idx !== indexed[i].idx) {
                    return [indexed[i].idx, indexed[mid].idx].sort((a, b) => a - b);
                }
                // Check adjacent duplicates
                if (mid + 1 < indexed.length && indexed[mid + 1].cost === target && indexed[mid + 1].idx !== indexed[i].idx) {
                    return [indexed[i].idx, indexed[mid + 1].idx].sort((a, b) => a - b);
                }
                break;
            } else if (indexed[mid].cost < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    return [];
}`,
      line_by_line: [
        {
          line: "indexed = sorted((cost, idx + 1) for idx, cost in enumerate(arr))",
          explanation: "Pairs costs with 1-based indices and sorts in O(N log N)."
        },
        {
          line: "pos = bisect.bisect_left(costs_only, target)",
          explanation: "Logarithmic binary search finding potential complement flavor."
        }
      ]
    },
    time_space_analysis: {
      time: "O(N log N) — Sorting takes O(N log N); N binary searches take O(N log N).",
      space: "O(N) for the indexed array."
    },
    edge_cases: [
      {
        case: "Two flavors have identical price (m=4, cost=[2, 2])",
        risk: "Returning the exact same index twice [1, 1].",
        mitigation: "indexed[pos][1] != orig_idx check prevents reusing the identical flavor."
      }
    ],
    guided_checkpoints: {
      comprehension: {
        question: "Why must we pair the original index with each price before sorting?",
        options: [
          "Sorting changes the position of elements, so original 1-based indices are lost without explicit tracking.",
          "Because HackerRank doesn't allow 0-based indexing.",
          "To speed up binary search.",
          "Because binary search cannot work on numbers."
        ],
        correct_index: 0,
        explanation: "Sorting reorders the array. Since the question asks for the original 1-based indices of the flavors in the input array, we must store the original index alongside each cost."
      },
      trace_prediction: {
        question: "For m = 4 and arr = [2, 2], what are the returned 1-based indices?",
        options: [
          "[1, 2]",
          "[1, 1]",
          "[2, 2]",
          "[0, 1]"
        ],
        correct_index: 0,
        explanation: "The flavors are at original indices 1 and 2, so the returned answer is [1, 2]."
      },
      sandbox_test_cases: [
        { input: "m = 4, arr = [1, 4, 5, 3, 2]", expected: "[1, 4]" },
        { input: "m = 4, arr = [2, 2, 4, 3]", expected: "[1, 2]" }
      ]
    },
    transfer_challenge: {
      title: "Variant Challenge: Two Sum II - Input Array Is Sorted",
      question: "How do you find two numbers that sum to target when the array is already sorted?",
      approach_shift: "Use two pointers from the ends: if sum < target left++; if sum > target right--; in O(N) time and O(1) space."
    },
    verified_resources: [
      {
        title: "HackerRank: Ice Cream Parlor",
        publisher: "HackerRank",
        url: "https://www.hackerrank.com/challenges/icecream-parlor/problem",
        type: "Official Problem",
        summary: "Standard problem statement and test cases."
      }
    ]
  }
];

export const ALL_DSA_LESSONS = CURATED_DSA_LESSONS;
