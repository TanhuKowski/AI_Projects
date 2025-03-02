import numpy as np
import sys
import time
from collections import defaultdict, deque
import re


def parse_input_file(file_path):
    """Parses the input file for the tile placement problem."""
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    landscape, tile_counts, target_visible = [], [0, 0, 0], {}
    i = 0
    while i < len(lines) and not lines[i].startswith('{'):
        landscape.append([int(val) for val in re.findall(r'\d+', lines[i])])
        i += 1
    
    if i < len(lines) and lines[i].startswith('{'):
        tile_counts_dict = {match[0]: int(match[1]) for match in re.findall(r'(\w+)=(\d+)', lines[i])}
        tile_counts = [tile_counts_dict.get(k, 0) for k in ['FULL_BLOCK', 'OUTER_BOUNDARY', 'EL_SHAPE']]
        i += 1
    
    for line in lines[i:]:
        if ':' in line:
            color, count = map(int, line.split(':'))
            target_visible[color] = count
    
    max_width = max(map(len, landscape))
    landscape = [row + [0] * (max_width - len(row)) for row in landscape]
    
    return landscape, tile_counts, target_visible


class TilePlacementProblem:
    """Represents a tile placement problem instance."""
    FULL_BLOCK, OUTER_BOUNDARY, EL_SHAPE = 0, 1, 2
    TILE_SIZE = 4

    def __init__(self, landscape, tile_counts, target_visible):
        self.landscape = np.array(landscape)
        self.height, self.width = self.landscape.shape
        self.tile_counts = tile_counts
        self.target_visible = target_visible
        self.grid_height, self.grid_width = self.height // self.TILE_SIZE, self.width // self.TILE_SIZE
        self.bush_locations = self._find_bush_locations()

    def _find_bush_locations(self):
        locations = defaultdict(set)
        for i in range(self.height):
            for j in range(self.width):
                if self.landscape[i, j] > 0:
                    locations[self.landscape[i, j]].add((i, j))
        return locations


class TilePlacementCSP:
    """CSP solver for the tile placement problem."""

    def __init__(self, problem):
        self.problem = problem
        self.domains = {(i, j): [0, 1, 2] for i in range(problem.grid_height) for j in range(problem.grid_width)}
        self.assignment = {}
        self.visible_bushes = defaultdict(set)

    def solve(self):
        """Solves the CSP using backtracking search."""
        if not self._ac3():
            return None
        return self._backtrack()

    def print_solution(self):
        """Prints the final tile placement solution."""
        if not self.assignment:
            print("No solution available")
            return
        
        grid = np.full((self.problem.grid_height, self.problem.grid_width), " ")
        tile_symbols = {0: "F", 1: "O", 2: "L"}
        
        for (i, j), tile in self.assignment.items():
            grid[i, j] = tile_symbols[tile]
        
        print("Solution Grid:")
        for row in grid:
            print(" ".join(row))

    def _backtrack(self):
        if len(self.assignment) == len(self.domains):
            return self.assignment
        var = min(self.domains.keys() - self.assignment.keys(), key=lambda v: (len(self.domains[v]), -self._degree_heuristic(v)))
        for value in sorted(self.domains[var], key=self._least_constraining_value):
            if self._is_consistent(var, value):
                self.assignment[var] = value
                if self._backtrack():
                    return self.assignment
                del self.assignment[var]
        return None

    def _ac3(self):
        """Applies AC-3 algorithm for constraint propagation."""
        queue = deque(self.domains.keys())
        while queue:
            var = queue.popleft()
            revised = False
            for value in self.domains[var][:]:
                if not any(self._is_consistent(var, v) for v in self.domains[var]):
                    self.domains[var].remove(value)
                    revised = True
            if revised:
                queue.extend(self.domains.keys())
        return all(self.domains.values())

    def _is_consistent(self, var, value):
        """Checks if the assignment is consistent based on tile availability."""
        return self.problem.tile_counts[value] > sum(v == value for v in self.assignment.values())

    def _least_constraining_value(self, value):
        """Returns how constraining a value is based on the effect on other variables."""
        return sum(len(self.domains[neighbor]) for neighbor in self.domains if value in self.domains[neighbor])
    
    def _degree_heuristic(self, var):
        """Returns the number of unassigned neighbors to break ties in MRV heuristic."""
        return sum(1 for neighbor in self.domains if neighbor != var and neighbor not in self.assignment)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tile_placement.py <input_file>")
        return

    input_file = sys.argv[1]
    try:
        landscape, tile_counts, target_visible = parse_input_file(input_file)
        problem = TilePlacementProblem(landscape, tile_counts, target_visible)
        solver = TilePlacementCSP(problem)
        solution = solver.solve()
        if solution:
            print("Solution found!")
            solver.print_solution()
        else:
            print("No solution found")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
