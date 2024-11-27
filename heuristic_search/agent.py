from game import Game
from collections import deque

class Agent:
    def __init__(self):
        self.state = 0
        self.moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.solution = []

    def reset(self):
        self.solution = []
    
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

if __name__ == "__main__":
    game = Game(10)
    game.generate_obstacles(40)
    game.visualize()
    agent = Agent()
    result = agent.bfs(game)
    # print(game.map)
    game.visualize()