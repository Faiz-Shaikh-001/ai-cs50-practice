import heapq
import sys

class Node():

    def __init__(self, parent, state, action):
        self.parent = parent
        self.state = state
        self.action = action
        self.g = 0  # Cost from start node to this node
        self.h = 0  # Cost to reach goal node from this node
        self.f = 0  # total cost

    def __lt__(self, other):
        return self.f < other.f
    

def heuristic(start, goal):
    return abs(goal[0] - start[0]) + abs(goal[1] - start[1])


class Maze():

    def __init__(self, filename):

        self.solution = None

        with open(filename) as f:
            contents = f.read()

        if contents.count('A') != 1:
            raise Exception(
                "There should only be one start point in the maze.")
        if contents.count('B') != 1:
            raise Exception("There should only be one goal point in the maze.")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []

            for j in range(self.width):
                try:
                    if contents[i][j] == 'A':
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == 'B':
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == ' ':
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print('-', end='')
                elif (i, j) == self.start:
                    print('A', end='')
                elif (i, j) == self.goal:
                    print('B', end='')
                elif solution is not None and (i, j) in solution:
                    print('*', end='')
                else:
                    print(' ', end="")
            print()
        print()

    def neighbours(self, state):
        row, col = state
        candidates = [
            ("up", (row+1, col)),
            ("down", (row-1, col)),
            ("left", (row, col-1)),
            ("right", (row, col+1)),
        ]

        result = []

        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))

        return result



    def solve(self):

        self.num_of_states_explored = 0

        start = Node(state=self.start, parent=None, action=None)
        open_list = [] 
        open_set = set()

        self.explored = set()

        heapq.heappush(open_list, start)
        open_set.add(start.state)

        while True:
            if len(open_list) == 0:
                raise Exception("No solution")
            
            node = heapq.heappop(open_list)
            open_set.remove(node.state)
            self.num_of_states_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []

                while node.parent is not None: 
                    actions.append(node.action)
                    cells.append(node.state)

                    node = node.parent
                
                actions.reverse()
                cells.reverse()
                self.solution = [actions, cells]
                return

            self.explored.add(node.state)

            for action, state in self.neighbours(node.state):
                if state not in open_set and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    child.g = node.g + 1
                    child.h = heuristic(state, self.goal)
                    child.f = child.g + child.h
                    heapq.heappush(open_list, child)
                    open_set.add(state)
                    

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )

        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)

                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 115)

                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                
                else:
                    fill = (237, 240, 252)
                
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j+1) * cell_size - cell_border, (i+1) * cell_size - cell_border)]),
                    fill = fill
                )
                
        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
filename = sys.argv[1].split('\\')[-1].split('.')[0]
print("Maze: \n")
# # m.print()
print("Solving...")
m.solve()
print(f"States explored: {m.num_of_states_explored}")
print("Solution: \n")
# # m.print()
m.output_image(f"./output/{filename}.png", show_explored=True)
