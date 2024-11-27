import random
from collections import deque

class Game:
    def __init__(self, n: int):
        self.n = n
        self.start = [0, 0]
        self.end = [n - 1, n - 1]
        self.map = [[0] * n for _ in range(n)]
        self.map[0][0] = 'S'
        self.map[self.n - 1][self.n - 1] = 'E'
    
    def reset_board(self):
        self.map = [[0] * self.n for _ in range(self.n)]
        self.map[0][0] = 'S'
        self.map[self.n - 1][self.n - 1] = 'E'

    def generate_obstacles(self, obstacles_count: int):
        if obstacles_count > self.n * self.n * 0.5:
            print('Number of obstacles should not exceed 50% of the board')
            return
        
        valid = False
        while not valid:
            obstacle_positions = set()
            self.reset_board()
            while len(obstacle_positions) < obstacles_count:
                x = random.randint(0, self.n - 1)
                y = random.randint(0, self.n - 1)
                if (x, y) not in [(0, 0), (self.n - 1, self.n - 1)]:
                    obstacle_positions.add((x, y))

            for x, y in obstacle_positions:
                self.map[x][y] = 1
            
            valid = self.is_path_exists()

    def is_path_exists(self):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = [[False for _ in range(self.n)] for _ in range(self.n)]
        queue = deque([(0, 0)])

        while queue:
            x, y = queue.popleft()

            if (x, y) == (self.n - 1, self.n - 1):
                return True

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.n and 0 <= ny < self.n and not visited[nx][ny] and self.map[nx][ny] in [0, 'E']:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

        return False
    
    def visualize(self):
        print('---' * self.n + '--')
        for i in range(self.n):
            print('|', end='')
            for j in range(self.n):
                if self.map[i][j] == 'S':
                    print(' S ', end='')
                elif self.map[i][j] == 'E':
                    print(' E ', end='')
                elif self.map[i][j] == 'P':
                    print(' . ', end='')
                elif self.map[i][j] == 1:
                    print(' | ', end='')
                else:
                    print(' - ', end='')
            print('|')
        print('---' * self.n + '--')

if __name__ == "__main__":
    game = Game(10)
    game.generate_obstacles(10)
    game.visualize()
