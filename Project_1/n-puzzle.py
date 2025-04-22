import heapq
import sys
import re

class NPuzzleSolver:
    def __init__(self, filename):
        self.grid, self.n = self.read_puzzle(filename)
        self.goal_state = self.generate_goal_state()
        self.blank_pos = self.find_blank()

    def read_puzzle(self, filename):
        """Reads the puzzle configuration from a file and returns the grid as a tuple of tuples.
        Now handles multiple separator types and skips empty lines."""
        try:
            with open(filename, "r") as f:
                # Read non-empty lines and split on any whitespace
                lines = [line.strip() for line in f if line.strip()]
                # Convert each number, handling multiple spaces/tabs
                grid = [tuple(map(int, re.split(r'\s+', line))) for line in lines]
                
                # Validate grid
                n = len(grid)
                if n == 0:
                    raise ValueError("Empty puzzle file")
                
                # Check if all rows have the same length and it's a square
                if not all(len(row) == n for row in grid):
                    raise ValueError("Puzzle must be square (same number of rows and columns)")
                
                # Convert to tuple of tuples for immutability
                return tuple(tuple(row) for row in grid), n
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except ValueError as e:
            if str(e).startswith("Empty puzzle"):
                print(str(e))
            elif str(e).startswith("Puzzle must be square"):
                print(str(e))
            else:
                print("Error: Invalid puzzle format. File should contain only numbers separated by spaces or tabs")
            sys.exit(1)

    def generate_goal_state(self):
        """Generates the goal state for an n*n puzzle."""
        return tuple(tuple((i * self.n + j + 1) % (self.n * self.n) for j in range(self.n)) for i in range(self.n))

    def find_blank(self):
        """Finds the position of the blank (0) in the grid."""
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def heuristic(self, state):
        """Calculates the Manhattan Distance heuristic."""
        distance = 0
        for i in range(self.n):
            for j in range(self.n):
                value = state[i][j]
                if value != 0:
                    goal_x, goal_y = (value - 1) // self.n, (value - 1) % self.n
                    distance += abs(goal_x - i) + abs(goal_y - j)
        return distance

    def get_neighbors(self, state, blank_pos):
        """Generates possible moves by swapping tiles."""
        x, y = blank_pos
        neighbors = []
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                new_state = [list(row) for row in state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                neighbors.append((tuple(tuple(row) for row in new_state), (nx, ny)))

        return neighbors

    def solve(self):
        """Solves the N-puzzle using A* search."""
        priority_queue = []
        heapq.heappush(priority_queue, (self.heuristic(self.grid), 0, self.grid, self.blank_pos, []))
        visited = set()

        while priority_queue:
            _, g, state, blank_pos, path = heapq.heappop(priority_queue)

            if state == self.goal_state:
                return path  # Return solution path

            if state in visited:
                continue
            visited.add(state)

            for neighbor, new_blank_pos in self.get_neighbors(state, blank_pos):
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_g = g + 1  # Cost to reach neighbor
                    f = new_g + self.heuristic(neighbor)  # f(n) = g(n) + h(n)
                    heapq.heappush(priority_queue, (f, new_g, neighbor, new_blank_pos, new_path))

        return None  # No solution found (shouldn't happen for valid inputs)

    def print_solution(self, path):
        """Prints the solution steps."""
        print("Initial State:")
        self.print_grid(self.grid)
        print("\nSolution Path:")
        for i, step in enumerate(path, 1):
            print(f"\nStep {i}:")
            self.print_grid(step)
        print(f"\nTotal Moves: {len(path)}")

    def print_grid(self, grid):
        """Prints the grid in a readable format."""
        max_width = max(len(str(x)) for row in grid for x in row)
        for row in grid:
            print(" ".join(str(x).rjust(max_width) if x != 0 else " " * max_width for x in row))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python npuzzle.py <filename>")
        sys.exit(1)

    solver = NPuzzleSolver(sys.argv[1])
    solution = solver.solve()

    if solution is None:
        print("No solution found.")
    else:
        solver.print_solution(solution)
