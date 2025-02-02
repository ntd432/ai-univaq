from game import Game
from collections import deque
import heapq, math

class Agent:
    def __init__(self):
        self.state = (0, 0)
        self.moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.solution = []

    def reset_solution(self):
        self.state = (0, 0)
        self.solution = []

    def heuristic(self, option: int, game: Game, move=None):
        n = game.n
        # -distance to the nearest obstacle
        if option == 0:
            return -self.distance_to_obstacle(game, move) - sum(move)
        # Manhattan distance of new state to the ending point
        if option == 1:
            x, y = self.state
            dx, dy = move
            nx, ny = x + dx, y + dy
            return abs(nx - (n - 1)) + abs(ny - (n - 1)) 
        # Euclidean distance of new state to the ending point
        if option == 2:
            x, y = self.state
            dx, dy = move
            nx, ny = x + dx, y + dy
            return math.sqrt((nx - (n - 1))**2 + (ny - (n - 1))**2)

    def distance_to_obstacle(self, game: Game, move: tuple):
        if move == None or game == None:
            return 0
        x, y = self.state
        dx, dy = move
        n = game.n
        count = 0
        
        while True:
            x, y = x + dx, y + dy
            if 0 <= x < n and 0 <= y < n and game.map[x][y] == 'E':
                return float('inf')
            if 0 <= x < n and 0 <= y < n and game.map[x][y] != 1:
                count += 1
            else:
                break
        return count
    
    def mark_solution(self, game: Game):
        for point in self.solution:
            if game.map[point[0]][point[1]] not in ['S', 'E']:
                game.map[point[0]][point[1]] = 'P'

    def bfs(self, game: Game):
        self.reset_solution()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        queue = deque([(0, 0)])
        parent = {}

        while queue:
            x, y = queue.popleft()
            self.state = (x, y)

            if (x, y) == (n - 1, n - 1):
                current = (x, y)
                while current is not None:
                    self.solution.append(current)
                    current = parent.get(current)
                self.solution = self.solution[::-1]
                self.mark_solution(game)
                return True

            for dx, dy in self.moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and game.map[nx][ny] in [0, 'E']:
                    visited[nx][ny] = True
                    queue.append((nx, ny))
                    parent[(nx, ny)] = (x, y)

        return False
    
    def dfs(self, game: Game):
        self.reset_solution()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        parent = {}

        def dfs(x, y):
            self.state = (x, y)
            if (x, y) == (n - 1, n - 1):
                self.solution.append((x, y))
                self.mark_solution(game)
                return True

            visited[x][y] = True
            self.solution.append((x, y))

            for dx, dy in self.moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and game.map[nx][ny] in [0, 'E']:
                    if dfs(nx, ny):
                        return True

            self.solution.pop()
            return False

        if dfs(0, 0):
            return True

    def best_first_search(self, game: Game, heuristic_option=0):
        self.reset_solution()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, 0)) # h, x, y
        parent = {(0, 0): (-1, -1)}

        while priority_queue:
            _, x, y = heapq.heappop(priority_queue)
            self.state = (x, y)

            if visited[x][y]:
                continue

            visited[x][y] = True

            if (x, y) == (n - 1, n - 1):
                # Reconstruct path
                while (x, y) != (-1, -1):
                    self.solution.append((x, y))
                    x, y = parent[(x, y)]
                self.solution = self.solution[::-1]  # Reverse the path
                self.mark_solution(game)
                return True

            for dx, dy in self.moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and game.map[nx][ny] in [0, 'E']:
                    heapq.heappush(priority_queue, (self.heuristic(heuristic_option, game, (dx, dy)), nx, ny))
                    if (nx, ny) not in parent:
                        parent[(nx, ny)] = (x, y)
        return False
    
    def a_star_search(self, game: Game, heuristic_option=0):
        self.reset_solution()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, 0, 0)) # f, g, x, y
        parent = {(0, 0): (-1, -1)}
        g_scores = {(0, 0): 0}

        while priority_queue:
            f, g, x, y = heapq.heappop(priority_queue)
            self.state = (x, y)

            if visited[x][y]:
                continue
                
            visited[x][y] = True

            if (x, y) == (n - 1, n - 1):
                # Reconstruct path
                while (x, y) != (-1, -1):
                    self.solution.append((x, y))
                    x, y = parent[(x, y)]
                self.solution = self.solution[::-1]  # Reverse the path
                self.mark_solution(game)
                return True
            
            for dx, dy in self.moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and game.map[nx][ny] in [0, 'E']:
                    g_score = g + 1
                    # update only if the path to nx, ny is smaller
                    if g_score < g_scores.get((nx, ny), float("inf")):
                        g_scores[(nx, ny)] = g_score
                        f_score = g_score + self.heuristic(heuristic_option, game, move=(dx, dy))
                        heapq.heappush(priority_queue, (f_score, g_score, nx, ny))
                        parent[(nx, ny)] = (x, y)
        return False