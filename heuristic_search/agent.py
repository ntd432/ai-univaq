from game import Game
from collections import deque
import heapq

class Agent:
    def __init__(self):
        self.state = (0, 0)
        self.moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.solution = []

    def reset(self):
        self.solution = []

    def heuristic(self, option: int, game: Game, move=None):
        n = game.n
        # Manhattan distance
        if option == 0:
            x, y = self.state
            return abs(x - (n - 1)) + abs(y - (n - 1)) 
        # -distance to the nearest obstacle
        if option == 1:
            return -self.distance_to_obstacle(game, move)


    def distance_to_obstacle(self, game: Game, move: tuple):
        if move == None or game == None:
            return 0
        x, y = self.state
        dx, dy = move
        n = game.n
        count = 0
        
        while True:
            x, y = x + dx, y + dy
            if game.map[x][y] == 'E':
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
        self.reset()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        queue = deque([(0, 0)])
        parent = {}

        while queue:
            x, y = queue.popleft()

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
        self.reset()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        parent = {}

        def dfs(x, y):
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

    def best_first_search(self, game: Game, heuristic_option=1):
        self.reset()
        n = game.n
        visited = [[False for _ in range(n)] for _ in range(n)]
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, 0))
        parent = {(0, 0): (-1, -1)}

        while priority_queue:
            _, x, y = heapq.heappop(priority_queue)

            if visited[x][y]:
                continue

            visited[x][y] = True

            if (x, y) == (n - 1, n - 1):
                # Reconstruct path
                while (x, y) != (-1, -1):
                    self.solution.append((x, y))
                    x, y = parent[(x, y)]
                self.solution = self.solution[::-1]  # Reverse the path
                print(self.solution)
                self.mark_solution(game)
                return True

            for dx, dy in self.moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and game.map[nx][ny] in [0, 'E']:
                    heapq.heappush(priority_queue, (self.heuristic(heuristic_option, game, (dx, dy)), nx, ny))
                    if (nx, ny) not in parent:
                        parent[(nx, ny)] = (x, y)
        return False


if __name__ == "__main__":
    game = Game(10)
    game.generate_obstacles(40)
    game.visualize()
    agent = Agent()
    # agent.state = (5, 5)
    # for move in agent.moves:
    #     print(move, agent.distance_to_obstacle(game, move))
    result = agent.best_first_search(game, heuristic_option=0)
    game.visualize()
    agent.bfs(game)
    game.visualize()