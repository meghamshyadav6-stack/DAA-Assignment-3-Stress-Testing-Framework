"""Static complexity knowledge base: bounds + correct NP-class labels
(decision vs optimization form), used in reports and risk output."""

# (topic, problem form, class, time, space, note)
CLASSIFICATION = [
    ("Binomial Heap", "data structure", "P (no hardness)", "insert O(log n) worst / O(1) amortized; extract-min, decrease-key, merge O(log n)", "O(n)",
     "Merge is binary addition of root lists."),
    ("Fibonacci Heap", "data structure", "P (no hardness)", "insert, merge, find-min O(1); decrease-key O(1) amortized; extract-min O(log n) amortized (single call can be O(n))", "O(n)",
     "Bounds are AMORTIZED: one extract-min after n lazy inserts costs Theta(n)."),
    ("B-Tree (min degree t)", "data structure", "P (no hardness)", "search/insert O(t log_t n) CPU, O(log_t n) node accesses", "O(n)",
     "Height <= log_t((n+1)/2); sequential inserts leave nodes ~half full."),
    ("Red-Black Tree", "data structure", "P (no hardness)", "search/insert O(log n), <= 2 rotations per insert; height <= 2 log2(n+1)", "O(n)",
     "Recoloring can cascade O(log n) but rotations are O(1) per insert."),
    ("Kruskal MST", "optimization", "P", "O(E log E) = O(E log V)", "O(V + E)", "Sorting dominates; union-find ~ alpha(V)."),
    ("Prim MST (matrix)", "optimization", "P", "O(V^2)", "O(V^2)", "Best for dense graphs; ignores E."),
    ("Prim MST (Fibonacci heap)", "optimization", "P", "O(E + V log V)", "O(V + E)", "Best asymptotically for sparse-to-moderate density."),
    ("Fractional Knapsack", "optimization", "P", "O(n log n) greedy", "O(n)", "Greedy-choice property holds because items are divisible."),
    ("0/1 Knapsack", "decision: is value >= K reachable?", "NP-Complete (weakly)", "DP O(nW): PSEUDO-polynomial", "O(W) values / O(nW) with reconstruction",
     "Polynomial in the NUMBER W, exponential in its bit length log2 W."),
    ("0/1 Knapsack", "optimization", "NP-Hard (weakly)", "DP O(nW): PSEUDO-polynomial", "O(W)", "Admits an FPTAS."),
    ("Floyd-Warshall", "optimization (APSP)", "P", "Theta(V^3) regardless of density", "Theta(V^2)", "Input-insensitive: sparse graphs cost the same."),
    ("Matrix Chain Multiplication", "optimization", "P", "O(n^3) DP (O(n log n) Hu-Shing exists)", "O(n^2)", "n = number of matrices."),
    ("Hamiltonian Cycle", "decision", "NP-Complete", "backtracking O(n!) worst case", "O(n)", "No optimization version; the weighted analogue is TSP."),
    ("N-Queen (find one solution)", "search / constructive", "NOT NP-Complete as usually posed", "backtracking exponential worst case; explicit O(n) constructions exist for all n>=4", "O(n)",
     "Counting ALL solutions is output-exponential. Only the 'n-queens COMPLETION' variant (given a partial placement) is NP-Complete."),
    ("TSP", "decision: is there a tour of cost <= K?", "NP-Complete", "exact: O(n!) backtracking; B&B worst case O(n!)", "O(n) DFS / O(b^n) best-first queue", "Reduction from Hamiltonian Cycle."),
    ("TSP", "optimization: cheapest tour", "NP-Hard (not in NP as stated)", "same as above", "same as above", "Solving it solves the decision form."),
]

# theoretical bound per measured series (algorithm key -> text)
THEORY = {
    "binomial_heap": "extract O(log n); decrease-key O(log n); merge O(log n)",
    "fibonacci_heap": "decrease-key O(1)* ; merge O(1); extract O(log n)* (*amortized)",
    "b_tree": "O(log_t n) node accesses per op",
    "red_black_tree": "O(log n) per op, height <= 2log2(n+1)",
    "kruskal": "O(E log E)", "prim_matrix": "O(V^2)", "prim_fibonacci": "O(E + V log V)",
    "fractional_knapsack": "O(n log n)", "knapsack_01_dp": "O(nW) pseudo-polynomial",
    "floyd_warshall": "Theta(V^3)", "matrix_chain": "Theta(n^3)",
    "n_queens": "O(n!) worst case", "hamiltonian_backtracking": "O(n!) worst case",
    "tsp_backtracking": "Theta((n-1)!)", "tsp_backtracking_pruned": "O(n!) worst case",
    "tsp_branch_and_bound": "O(n!) worst case, usually far less",
}
