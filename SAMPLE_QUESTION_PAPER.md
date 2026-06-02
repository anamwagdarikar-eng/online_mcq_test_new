# Sample Question Paper - Data Structures (DS-101)

## Test Details
- **Test Name:** Data Structures Mid Term Exam
- **Subject:** Data Structures (CS Department)
- **Semester:** 2
- **Total Marks:** 100
- **Duration:** 120 minutes
- **Passing Marks:** 40
- **Negative Marking:** Yes (0.25 per wrong answer)
- **Total Questions:** 40

---

## Section A: Basic Concepts (1 Mark Each) - 10 Questions

### Q1. Time Complexity of Binary Search
**Question:** What is the time complexity of Binary Search?
- A) O(n²)
- B) O(n log n)
- **C) O(log n)** ✓
- D) O(1)

**Explanation:** Binary search divides the search space in half with each comparison, resulting in logarithmic time complexity.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q2. LIFO Principle
**Question:** Which data structure uses the LIFO (Last In First Out) principle?
- A) Queue
- **B) Stack** ✓
- C) Array
- D) Linked List

**Explanation:** Stack follows LIFO principle where the last element added is the first one to be removed.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q3. Array Indexing
**Question:** In most programming languages, arrays are indexed starting from:
- **A) 0** ✓
- B) 1
- C) -1
- D) It depends on the language

**Explanation:** Most modern programming languages (C, C++, Java, Python) use 0-based indexing.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q4. Linked List Advantage
**Question:** What is a major advantage of Linked List over Array?
- A) Faster access time
- B) Better cache locality
- **C) Dynamic size allocation** ✓
- D) Better for sorting

**Explanation:** Linked lists can grow and shrink dynamically without pre-allocating memory.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q5. Tree Terminology
**Question:** What is the root in a tree data structure?
- A) Any node that has no children
- **B) The topmost node with no parent** ✓
- C) The node with maximum value
- D) The node that is most accessed

**Explanation:** The root is the topmost node in a tree hierarchy that serves as the starting point.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q6. Graph Definition
**Question:** A graph with no cycles is called:
- A) Complete Graph
- **B) Acyclic Graph (DAG)** ✓
- C) Connected Graph
- D) Directed Graph

**Explanation:** A Directed Acyclic Graph (DAG) is a graph with no cycles.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q7. Hash Table Collision
**Question:** When two keys hash to the same index, it's called:
- A) Clustering
- B) Collision** ✓
- C) Conflict
- D) Collision Resolution

**Explanation:** When two different keys produce the same hash index, it's called a collision.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q8. Queue Operation
**Question:** Which operation is used to add an element to a queue?
- A) Push
- B) Dequeue
- **C) Enqueue** ✓
- D) Insert

**Explanation:** Enqueue adds elements to the rear of the queue.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q9. Heap Property
**Question:** In a Max Heap, what property is satisfied?
- A) Parent < Children
- **B) Parent ≥ Children** ✓
- C) Siblings are ordered
- D) All leaves are equal

**Explanation:** In a Max Heap, every parent node is greater than or equal to its children.
**CO Mapped:** CO1 - Understand fundamental data structures

---

### Q10. Sorting Stability
**Question:** What does "stable" mean in the context of sorting algorithms?
- A) The algorithm never fails
- **B) Equal elements maintain their relative order** ✓
- C) The algorithm uses constant space
- D) The algorithm is deterministic

**Explanation:** A stable sort preserves the relative order of elements with equal keys.
**CO Mapped:** CO1 - Understand fundamental data structures

---

## Section B: Algorithm Analysis (2 Marks Each) - 10 Questions

### Q11. Merge Sort Complexity
**Question:** What is the space complexity of Merge Sort?
- A) O(1)
- B) O(log n)
- **C) O(n)** ✓
- D) O(n log n)

**Explanation:** Merge sort requires O(n) auxiliary space for merging operations.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q12. Quick Sort Worst Case
**Question:** When does Quick Sort perform worst-case O(n²) time complexity?
- A) When the array is sorted
- B) When the array is reverse sorted
- **C) When the pivot is always the smallest or largest element** ✓
- D) When duplicates are present

**Explanation:** Quick sort degrades to O(n²) when pivot selection results in highly unbalanced partitions.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q13. BFS vs DFS
**Question:** Which traversal is useful for finding the shortest path in an unweighted graph?
- **A) BFS (Breadth First Search)** ✓
- B) DFS (Depth First Search)
- C) Both equally
- D) In-order traversal

**Explanation:** BFS explores level by level and guarantees the shortest path in unweighted graphs.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q14. Dijkstra's Algorithm
**Question:** Dijkstra's algorithm can be used on graphs with:
- A) Negative edge weights
- **B) Non-negative edge weights** ✓
- C) Both positive and negative
- D) Only positive integers

**Explanation:** Dijkstra's algorithm requires non-negative edge weights to work correctly.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q15. Dynamic Programming Definition
**Question:** Dynamic Programming is an optimization technique that uses:
- A) Recursion with backtracking
- **B) Memoization to store subproblem solutions** ✓
- C) Greedy approach
- D) Brute force enumeration

**Explanation:** DP solves problems by storing solutions of overlapping subproblems to avoid recalculation.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q16. Longest Common Subsequence
**Question:** The Longest Common Subsequence (LCS) problem can be solved using:
- A) Greedy algorithm
- B) Divide and conquer
- **C) Dynamic Programming** ✓
- D) Hashing

**Explanation:** LCS is a classic DP problem that builds a table of subproblem solutions.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q17. 0/1 Knapsack
**Question:** The 0/1 Knapsack problem requires:
- A) Each item can be taken fraction
- **B) Each item is taken fully or not at all** ✓
- C) Items can be replaced
- D) Greedy selection

**Explanation:** In 0/1 Knapsack, items are either fully included or excluded.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q18. Red-Black Tree Property
**Question:** What is a property of Red-Black Trees?
- A) All nodes must be red or blue
- **B) The path from root to leaf has same number of black nodes** ✓
- C) Maximum height is always even
- D) All leaves must be red

**Explanation:** Red-Black trees maintain color properties to ensure balanced operations.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q19. AVL Tree Balance
**Question:** An AVL tree maintains balance by ensuring:
- A) Equal number of nodes on both sides
- B) Height difference ≤ 1 between subtrees** ✓
- C) All nodes at even depth are balanced
- D) Maximum height is log n

**Explanation:** AVL trees maintain the invariant that height difference of any node's subtrees is at most 1.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q20. Topological Sort
**Question:** Topological sort is applicable on:
- A) Any graph
- **B) Directed Acyclic Graphs (DAG)** ✓
- C) Undirected graphs only
- D) Complete graphs

**Explanation:** Topological sort requires a DAG to produce a valid linear ordering.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

## Section C: Implementation & Problem Solving (4 Marks Each) - 10 Questions

### Q21. Stack Implementation
**Question:** Implementing a stack using a queue requires:
- A) One queue
- **B) Two queues** ✓
- C) Two stacks
- D) Three queues

**Explanation:** Using two queues, we can implement push (enqueue both), and pop (dequeue from one after transferring).
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q22. Circular Queue Advantage
**Question:** What is the main advantage of Circular Queue over Linear Queue?
- A) Faster insertion
- B) Less memory usage
- **C) Reuses the freed space** ✓
- D) Better cache locality

**Explanation:** Circular queues reuse the space of dequeued elements, maximizing memory efficiency.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q23. Infix to Postfix Conversion
**Question:** Converting Infix expression "A+B*C" to Postfix gives:
- A) ABC+*
- **B) ABC*+** ✓
- C) AB+C*
- D) A+BC*

**Explanation:** Using operator precedence (* before +), Postfix form is ABC*+.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q24. Subset Sum Problem
**Question:** The Subset Sum problem can be solved in pseudo-polynomial time using:
- A) Greedy approach
- **B) Dynamic Programming** ✓
- C) Brute force
- D) Hashing

**Explanation:** DP approach has time complexity O(n*sum), making it pseudo-polynomial.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q25. Minimum Spanning Tree
**Question:** Kruskal's algorithm for MST sorts edges by:
- A) Source node
- **B) Weight** ✓
- C) Destination node
- D) Frequency

**Explanation:** Kruskal's algorithm sorts edges in increasing order of weight.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q26. Graph Representation
**Question:** Adjacency matrix representation of a graph requires space:
- A) O(V)
- B) O(E)
- **C) O(V²)** ✓
- D) O(V log V)

**Explanation:** Adjacency matrix is V×V matrix, requiring O(V²) space.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q27. Strongly Connected Components
**Question:** Tarjan's algorithm finds SCC in:
- A) O(V² log V)
- **B) O(V + E)** ✓
- C) O(V² + E)
- D) O((V+E) log V)

**Explanation:** Tarjan's algorithm performs DFS once, achieving O(V+E) time complexity.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q28. Edit Distance
**Question:** Edit Distance (Levenshtein distance) between "cat" and "dog" is:
- A) 2
- **B) 3** ✓
- C) 1
- D) 4

**Explanation:** Requires 3 substitutions: c→d, a→o, t→g.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q29. Next Greater Element
**Question:** For finding Next Greater Element of all array elements, optimal approach uses:
- A) Sorting and searching
- B) Nested loops
- **C) Stack** ✓
- D) Hashing

**Explanation:** Stack can solve this in O(n) time by maintaining decreasing order.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q30. Segment Tree Construction
**Question:** Building a Segment Tree for range queries takes:
- A) O(n) time and O(n) space
- **B) O(n) time and O(n) space** ✓
- C) O(n log n) time and O(n) space
- D) O(n²) time and O(n²) space

**Explanation:** Segment Tree construction is O(n) time and requires O(n) space.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

## Section D: Advanced Concepts (3 Marks Each) - 10 Questions

### Q31. Skip List Performance
**Question:** Skip List provides search operation in expected:
- A) O(n²)
- B) O(n)
- **C) O(log n)** ✓
- D) O(1)

**Explanation:** Skip Lists achieve O(log n) expected search time through probabilistic balancing.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q32. B-Tree Order
**Question:** In a B-Tree of order m, internal nodes have at most:
- A) m-1 keys
- **B) m keys** ✓
- C) m+1 keys
- D) 2m keys

**Explanation:** A B-Tree of order m has maximum m children and m-1 keys per node.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q33. Bloom Filter
**Question:** Bloom Filter is best used for:
- A) Exact searching
- **B) Membership testing** ✓
- C) Sorting
- D) Path finding

**Explanation:** Bloom Filters excel at membership testing with O(1) lookup time and minimal space.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q34. Trie Complexity
**Question:** Search in a Trie has time complexity:
- A) O(log n)
- **B) O(m) where m is key length** ✓
- C) O(n)
- D) O(n log n)

**Explanation:** Trie search time depends on the length of the key, not the number of keys.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q35. Suffix Array
**Question:** Suffix Array can be constructed in:
- A) O(n² log n)
- **B) O(n log n)** ✓
- C) O(n²)
- D) O(n)

**Explanation:** Efficient algorithms like SA-IS can construct suffix arrays in O(n) or O(n log n).
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q36. Fenwick Tree Update
**Question:** Fenwick Tree update operation takes:
- A) O(1)
- B) O(n)
- **C) O(log n)** ✓
- D) O(n log n)

**Explanation:** Fenwick Tree (Binary Indexed Tree) allows O(log n) updates and prefix sum queries.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q37. Cuckoo Hashing
**Question:** Cuckoo Hashing uses:
- A) One hash function
- **B) Two hash functions** ✓
- C) Three hash functions
- D) Variable number of hash functions

**Explanation:** Cuckoo Hashing resolves collisions by maintaining two hash functions.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q38. Graph Coloring Complexity
**Question:** Graph Coloring problem is:
- A) Polynomial time solvable
- **B) NP-Complete** ✓
- C) Linear time solvable
- D) O(n log n) solvable

**Explanation:** Graph Coloring is a classic NP-Complete problem.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q39. Recursion Stack Depth
**Question:** Maximum recursion depth for a balanced BST of n nodes is:
- A) O(n)
- **B) O(log n)** ✓
- C) O(√n)
- D) O(1)

**Explanation:** For a balanced BST, the maximum depth is logarithmic in the number of nodes.
**CO Mapped:** CO2 - Implement and analyze algorithms

---

### Q40. Matrix Chain Multiplication
**Question:** Matrix Chain Multiplication problem requires:
- A) Greedy algorithm
- B) Brute force
- **C) Dynamic Programming** ✓
- D) Linear search

**Explanation:** MCM is solved using DP with time complexity O(n³).
**CO Mapped:** CO2 - Implement and analyze algorithms

---

## Answer Key

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|-------|--------|-------|--------|-------|--------|-------|--------|
| 1 | C | 11 | C | 21 | B | 31 | C |
| 2 | B | 12 | C | 22 | C | 32 | B |
| 3 | A | 13 | A | 23 | B | 33 | B |
| 4 | C | 14 | B | 24 | B | 34 | B |
| 5 | B | 15 | B | 25 | B | 35 | B |
| 6 | B | 16 | C | 26 | C | 36 | C |
| 7 | B | 17 | B | 27 | B | 37 | B |
| 8 | C | 18 | B | 28 | B | 38 | B |
| 9 | B | 19 | B | 29 | C | 39 | B |
| 10 | B | 20 | B | 30 | B | 40 | C |

---

## Marking Scheme
- **Section A (Q1-10):** 1 mark each = 10 marks
- **Section B (Q11-20):** 2 marks each = 20 marks
- **Section C (Q21-30):** 4 marks each = 40 marks
- **Section D (Q31-40):** 3 marks each = 30 marks
- **Total:** 100 marks

---

## Instructions for Students
1. All questions are compulsory
2. Negative marking enabled: -0.25 per wrong answer
3. Read questions carefully before answering
4. You can review your answers before final submission
5. Time limit: 120 minutes
6. Once submitted, you cannot edit your answers

