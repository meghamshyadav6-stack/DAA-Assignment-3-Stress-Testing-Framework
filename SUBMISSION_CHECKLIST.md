# Handbook checklist - Assignment 3 (tick before submitting)

## Minimum expectations for every team
| # | Requirement | Where it is satisfied |
|---|---|---|
| 1 | Entities, constraints, objective, input-size parameters | Report section 3 |
| 2 | Implement required DAA techniques | `daalab/*.py` (all 16 topics) |
| 3 | Compare >= 2 syllabus choices for a major decision | Binomial vs Fibonacci, B-Tree vs RB, Prim vs Kruskal, BT vs B&B |
| 4 | Time + space analysis for every major algorithm | Report section 5 (table) |
| 5 | Normal, large, boundary, difficult tests | `tests/test_correctness.py` + `daalab/suites.py` (report section 7) |
| 6 | Behaviour change when input changes + NP-Hard/NP-Complete implications | Report sections 6, 9 |

## Assignment 3 mandatory test families
1 data structures | 2 MST sparse/dense | 3 knapsack matched datasets | 4 Floyd-Warshall + MCM growth |
5 Hamiltonian/N-Queen/TSP with states generated/pruned/time/queue | 6 decision vs optimization classification
-> all in `daalab/suites.py`, results in `results/`.

## Required risk output: Low / Moderate / High -> `results/risk_report.csv`

## Submission requirements (GitHub + LeetCode)
- [ ] Framework architecture diagram -> `results/plots/architecture.png` (also in report)
- [ ] Working code -> this repo
- [ ] DAA analysis (time, space, correctness, assumptions, alternative) -> report
- [ ] Experiments + interpretation -> `results/`, report section 6
- [ ] Report (abstraction, representation, design, results, limitations, change with inputs) -> `DAA_Assignment3_Report.docx`
- [ ] Demonstration of a changed choice -> `python lab.py run --suite heaps` / knapsack / mst (report section 8)
- [ ] **YOU must still do:** push to GitHub, fill in names/roll numbers in the report, solve + submit LeetCode problems, prepare for VIVA.

## Suggested LeetCode problems (verify numbers on the site; premium ones marked *)
- Heaps: 23 Merge k Sorted Lists, 295 Find Median from Data Stream, 703 Kth Largest in a Stream
- Balanced trees: 729 My Calendar I, 220 Contains Duplicate III, 450 Delete Node in a BST
- MST: 1584 Min Cost to Connect All Points, 1135* Connecting Cities With Minimum Cost, 1489 Critical and Pseudo-Critical Edges
- Floyd-Warshall: 1334 City With Smallest Number of Neighbors at a Threshold Distance, 743 Network Delay Time
- Knapsack: 416 Partition Equal Subset Sum, 474 Ones and Zeroes, 494 Target Sum, 1710 Maximum Units on a Truck (greedy)
- Matrix-chain pattern: 1039 Min Score Triangulation of Polygon, 312 Burst Balloons, 1547 Min Cost to Cut a Stick
- Backtracking: 51 N-Queens, 52 N-Queens II, 980 Unique Paths III (Hamiltonian-path flavour)
- TSP flavour: 847 Shortest Path Visiting All Nodes, 943 Find the Shortest Superstring

## VIVA quick answers
- Why is 0/1 knapsack DP not polynomial? O(nW) is polynomial in the value W, not in its bit-length.
- Optimization TSP = NP-Hard; decision TSP = NP-Complete. Standard N-Queen is NOT NP-Complete.
- Fibonacci heap was *worse* on extract-all (578k vs 324k work at n=8000) but 3x better on decrease-key storms and 3.5x on merges.
- Fibonacci amortized O(log n) extract still allows one O(n) operation (observed spike 664x average).
