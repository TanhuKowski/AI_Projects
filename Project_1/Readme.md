# N-Puzzle Solver: Algorithm Choice and Approach

## Algorithm Choice: A* Search Algorithm with Manhattan Distance Heuristic

A* Search algorithm is one of the best and popular technique used in path-finding and graph traversals. Informally speaking, A* Search algorithms, unlike other traversal techniques, it has "brains". What it means is that it is really a smart algorithm which separates it from the other conventional algorithms.

It combines:

- **g(n):** The cost to reach the current state.
- **h(n):** An estimated cost from the current state to the goal.
- **f(n) = g(n) + h(n)**, the total estimated cost.

The algorithm ensures the shortest path using the reliable Manhattan Distance heuristic.

## Why Manhattan Distance as Heuristic?

Manhattan distance is a metric used to determine the distance between two points in a grid-like path. Unlike Euclidean distance, which measures the shortest possible line between two points, Manhattan distance measures the sum of the absolute differences between the coordinates of the points. This method is called "Manhattan distance" because, like a taxi driving through the grid-like streets of Manhattan, it must travel along the grid lines.

### Key Benefits:

- It never overestimates the cost, ensuring A* remains optimal.
- More efficient than simpler heuristics in guiding the search.

## Approach to Solving the N-Puzzle

1. Read the puzzle from a file and convert it into a tuple of tuples (immutable representation of the state).
2. Define the goal state as an n×n array where the numbers are arranged in ascending order.
3. Use the A* Search Algorithm:
   - Maintain a priority queue (min-heap) of states sorted by **f(n) = g(n) + h(n)**.
   - Expand the best state (Lowest **f(n)**) by moving tiles into the blank space.
   - Track visited states to avoid redundant searches.
   - Stop when the goal state is reached and return the shortest path.
4. Print the optimal steps to solve the puzzle.

## Time and Space Complexity

- **Time Complexity (Worst Case):** There may be **O(b^d)** states to be explored where:
  - **b** is roughly between **2 to 4** moves that may be taken from every given state.
  - **d** is the number of moves to reach the solution.
  - Hence, the deeper the solution is placed, the more time it takes to reach it.

- **Space Complexity:** All visited states must be retained in memory by the algorithm, which grows as **O(b^d)**. Higher puzzle difficulty requires more space to hold explored paths.
