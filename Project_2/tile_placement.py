import numpy as np
import sys
import time
from collections import defaultdict, deque
import re


def parse_input_file(file_path):
    """Parses the input file for the tile placement problem.
    
    Expected format:
    - First lines: landscape grid with numbers separated by any whitespace
    - Line with tile counts in format {FULL_BLOCK=X,OUTER_BOUNDARY=Y,EL_SHAPE=Z}
    - Lines with target visibility in format color:count
    """
    with open(file_path, 'r') as f:
        # Read and clean lines, removing comments and empty lines
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    landscape = []
    tile_counts = [0, 0, 0]  # [FULL_BLOCK, OUTER_BOUNDARY, EL_SHAPE]
    target_visible = {}
    
    # Parse the file line by line
    i = 0
    # Parse landscape until we hit a line with curly braces
    while i < len(lines) and not lines[i].startswith('{'):
        # Split on any whitespace and convert to integers
        try:
            row = [int(x) for x in re.split(r'\s+', lines[i].strip())]
            landscape.append(row)
            i += 1
        except ValueError as e:
            raise ValueError(f"Invalid landscape data on line {i+1}: {lines[i]}")
    
    # Parse tile counts
    if i < len(lines) and lines[i].startswith('{'):
        try:
            # Remove curly braces and split on comma
            tile_data = lines[i].strip('{}').split(',')
            tile_dict = {}
            for item in tile_data:
                name, count = item.split('=')
                tile_dict[name.strip()] = int(count)
            
            # Map to ordered list [FULL_BLOCK, OUTER_BOUNDARY, EL_SHAPE]
            tile_counts = [
                tile_dict.get('FULL_BLOCK', 0),
                tile_dict.get('OUTER_BOUNDARY', 0),
                tile_dict.get('EL_SHAPE', 0)
            ]
            i += 1
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid tile count format on line {i+1}: {lines[i]}")
    
    # Parse target visibility
    for line in lines[i:]:
        try:
            if ':' in line:
                color, count = map(int, line.strip().split(':'))
                target_visible[color] = count
        except ValueError:
            raise ValueError(f"Invalid visibility format: {line}")
    
    # Validate the parsed data
    if not landscape:
        raise ValueError("No landscape data found in input file")
    
    # Make landscape rectangular by padding with zeros
    max_width = max(len(row) for row in landscape)
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
        # Calculate grid dimensions, rounding up to handle partial tiles
        self.grid_height = (self.height + self.TILE_SIZE - 1) // self.TILE_SIZE
        self.grid_width = (self.width + self.TILE_SIZE - 1) // self.TILE_SIZE
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
        """Prints the final tile placement solution with a detailed visual representation."""
        if not self.assignment:
            print("No solution available")
            return
        
        # Define tile patterns for visual representation
        tile_patterns = {
            0: [  # FULL_BLOCK
                "████",
                "████",
                "████",
                "████"
            ],
            1: [  # OUTER_BOUNDARY
                "████",
                "█  █",
                "█  █",
                "████"
            ],
            2: [  # EL_SHAPE
                "██  ",
                "██  ",
                "██  ",
                "████"
            ]
        }
        
        # Create a grid to hold the visual representation
        visual_grid = []
        for i in range(self.problem.grid_height):
            for row_in_tile in range(4):  # Each tile is 4x4
                visual_row = []
                for j in range(self.problem.grid_width):
                    tile = self.assignment.get((i, j), -1)
                    if tile == -1:
                        visual_row.append("    ")  # Empty space
                    else:
                        # Check if we're at the edge of the landscape
                        if (i * 4 + row_in_tile) < self.problem.height:
                            pattern = tile_patterns[tile][row_in_tile]
                            # Adjust pattern width if at the right edge
                            if (j * 4 + 4) > self.problem.width:
                                pattern = pattern[:self.problem.width - j * 4]
                            visual_row.append(pattern)
                if visual_row:  # Only add row if it's within landscape bounds
                    visual_grid.append(" ".join(visual_row))
        
        # Print the solution with a header
        print("\nTile Placement Solution:")
        print("F = Full Block, O = Outer Boundary, L = El Shape")
        print("\nVisual Representation:")
        print("\n".join(visual_grid))
        
        # Print the symbolic representation
        print("\nSymbolic Representation:")
        grid = np.full((self.problem.grid_height, self.problem.grid_width), " ")
        tile_symbols = {0: "F", 1: "O", 2: "L"}
        
        for (i, j), tile in self.assignment.items():
            grid[i, j] = tile_symbols[tile]
        
        for row in grid:
            print(" ".join(row))
        
        # Print tile usage statistics
        print("\nTile Usage:")
        tile_names = ["Full Block", "Outer Boundary", "El Shape"]
        for i, count in enumerate(self.problem.tile_counts):
            used = sum(1 for v in self.assignment.values() if v == i)
            print(f"{tile_names[i]}: {used}/{count} used")

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
        """Checks if the assignment is consistent based on tile availability and landscape boundaries."""
        # Check tile availability
        if self.problem.tile_counts[value] <= sum(v == value for v in self.assignment.values()):
            return False
            
        # Check if tile fits within landscape boundaries
        i, j = var
        if (i * self.problem.TILE_SIZE >= self.problem.height or 
            j * self.problem.TILE_SIZE >= self.problem.width):
            return False
            
        return True

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
