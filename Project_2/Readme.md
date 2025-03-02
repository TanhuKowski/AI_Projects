# Tile Placement Problem

## Introduction
In this problem, a square landscape contains bushes of different colors, and tiles must be placed in such a way that a specific number of bushes remain visible. Three different tile shapes were used: Full Block, Outer Boundary, and EL Shape. The solution was developed using CSP techniques including search algorithms, heuristics, and constraint propagation.

## Problem Description
The landscape is represented as a grid where each cell contains a bush of color 1, 2, 3, or 4, or remains empty. Tiles (4x4 in size) must be placed over the landscape.

Three types of tiles were available:
- **Full Block:** Covers the entire 4x4 area, making bushes in that area invisible.
- **Outer Boundary:** Covers the outer edges of a 4x4 area but leaves the inner bushes visible.
- **EL Shape:** Covers two sides of a 4x4 area, leaving part of it visible.

The goal was to place these tiles so that exactly the right number of each colored bush would remain visible.

## Algorithm Design
A backtracking search approach was implemented for this solution. The algorithm assigns tiles to grid cells recursively, and when a conflict is encountered, backtracking occurs to try alternative options.

Several heuristics were employed to optimize the search process:
- **Minimum Remaining Values (MRV):** This selects the grid cell with the fewest valid tile options remaining. By targeting the most constrained spots first, the search space is narrowed more efficiently.
- **Least Constraining Value (LCV):** When placing a tile, preference is given to options that restrict future placements the least, essentially keeping more possibilities open.
- **Degree Heuristic:** In cases where MRV results in a tie between cells, this heuristic breaks the tie by selecting the cell that constrains the most neighbors, focusing on spots with the greatest impact.

The **AC3 algorithm** was also implemented for constraint propagation. This technique examines the problem ahead of time and eliminates invalid options before beginning the main search.

## Implementation Details
- **Input Parsing:** The program reads a file containing the landscape layout, available tile quantities, and visibility targets for each colored bush.
- **Tile Placement CSP Class:** A class was created to manage constraint satisfaction functions including domain filtering, consistency checking, and heuristic selection.
- **Solution Representation:** The solution is represented as a grid where `F` represents Full Block tiles, `O` indicates Outer Boundary tiles, and `L` shows where EL Shape tiles are placed.

## Results
The program outputs the solution grid showing where each tile should be placed. If no valid configuration can be found that satisfies all constraints, **"No solution found"** is returned.
