import logging as log
import csv
import os

from time import time
from abc import ABC, abstractmethod
from math import inf
from random import choice
from chess_game import ChessGame
from game import Game
from chess import Board, Move

try:
    from config import BOARD_SCORES, END_SCORES, DEFAULT_DEPTH, DATA, DATA_2
except ModuleNotFoundError:
    from .config import BOARD_SCORES, END_SCORES, DEFAULT_DEPTH, DATA, DATA_2


# Change the working directory to the directory containing this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
file = open(DATA, mode='a', newline='')
writer = csv.writer(file)

file_2 = open(DATA_2, mode='a', newline='')
writer_2 = csv.writer(file_2)

def write_to_csv(input_value: float, output_value: float):
    if input_value == 100 and output_value == 100:
        return
    # Write the data row
    writer.writerow([input_value, output_value])
    print(f"Added row: {input_value}, {output_value}")

def write_to_csv_list(row: list):
    if row == [0] * len(row) or row == [100] * len(row):
        return
    # Write the data row
    writer_2.writerow(row)
    print(f"Added row: {row}")

class Player(ABC):
    def __init__(self, player: bool, game: Game=ChessGame(), solver: str=None):
        self.player = player
        self.solver = solver
        self.game = game

    @abstractmethod
    def move(self):
        pass

class RandomPlayer(Player):
    def __init__(self, player: bool, game: Game=ChessGame()):
        super().__init__(player, game, "random")

    def move(self, board: Board) -> str:
        assert board.turn == self.player, "Not bot turn to move!"
        
        moves = list(board.legal_moves)
        move = choice(moves).uci()

        return move

class MiniMaxPlayer(Player):
    def __init__(self, player, game: Game=ChessGame(), depth=DEFAULT_DEPTH, 
                 choice_limit=-1, verbose=False, generate_data=False):
        super().__init__(player, game, f"minimax, depth = {depth}, limit = {choice_limit}")
        self.depth = depth
        self.verbose = verbose
        # limit number of choices
        self.limit = choice_limit
        self.generate_data = generate_data

    def _minimax(self, board: Board, player: bool, depth: int, alpha: float=-inf, beta: float=inf):
        # base case
        if depth == 0 or self.game.game_over(board):
            return [self.game.game_score(board, self.player, END_SCORES, BOARD_SCORES), None]

        # first move for white
        if len(board.move_stack) == 0:
            white_opening = choice(("e2e4", "d2d4", "c2c4", "g1f3"))
            return white_opening

        moves = self.game.sorted_moves(board, player, self.limit)

        if board.turn == player:
            maxScore, bestMove = -inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, not player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)
                if self.generate_data and depth == DEFAULT_DEPTH:
                    write_to_csv(h_value, score[0])
                
                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")

                alpha = max(alpha, score[0])
                if beta <= alpha:
                    break

                if score[0] >= maxScore:
                    maxScore = score[0]
                    bestMove = move

            return [maxScore, bestMove]
        else:
            minScore, bestMove = inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)
                if self.generate_data and depth == DEFAULT_DEPTH:
                    write_to_csv(h_value, score[0])

                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")
                
                beta = min(beta, score[0])
                if beta <= alpha:
                    break

                if score[0] <= minScore:
                    minScore = score[0]
                    bestMove = move

            return [minScore, bestMove]

    def move(self, board: Board) -> str:
        best_move = self._minimax(board, self.player, self.depth)
        if type(best_move) == str:
            return best_move
        return best_move[1].uci()
    
class MiniMaxPlayerWithRegressor(Player):
    def __init__(self, player, game: Game=ChessGame(), depth=DEFAULT_DEPTH, choice_limit=-1, verbose=False):
        super().__init__(player, game, f"minimax with regressor, depth = {depth}, limit = {choice_limit}")
        self.depth = depth
        self.verbose = verbose
        # limit number of choices
        self.limit = choice_limit

    def _minimax(self, board: Board, player: bool, depth: int, alpha: float=-inf, beta: float=inf):
        # base case
        if depth == 0 or self.game.game_over(board):
            return [self.game.game_score(board, self.player, END_SCORES, BOARD_SCORES), None]

        # first move for white
        if len(board.move_stack) == 0:
            white_opening = choice(("e2e4", "d2d4", "c2c4", "g1f3"))
            return white_opening

        moves = self.game.sorted_moves_prediction(board, player, self.limit)
        print(moves)
        return moves[0][::-1]

        if board.turn == player:
            maxScore, bestMove = -inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, not player, depth - 1, alpha, beta)
                
                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")

                alpha = max(alpha, score[0])
                if beta <= alpha:
                    break

                if score[0] >= maxScore:
                    maxScore = score[0]
                    bestMove = move

            return [maxScore, bestMove]
        else:
            minScore, bestMove = inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, player, depth - 1, alpha, beta)

                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")
                
                beta = min(beta, score[0])
                if beta <= alpha:
                    break

                if score[0] <= minScore:
                    minScore = score[0]
                    bestMove = move

            return [minScore, bestMove]

    def move(self, board: Board) -> str:
        best_move = self._minimax(board, self.player, self.depth)
        print(best_move)
        if type(best_move) == str:
            return best_move
        return best_move[1].uci()
    
class MiniMaxPlayerWithHFunction(Player):
    def __init__(self, player, game: Game=ChessGame(), depth=DEFAULT_DEPTH, choice_limit=-1, verbose=False, generate_data=False):
        super().__init__(player, game, f"minimax with new H function, depth = {depth}, limit = {choice_limit}")
        self.depth = depth
        self.verbose = verbose
        # limit number of choices
        self.limit = choice_limit
        self.generate_data = generate_data

    def _minimax(self, board: Board, player: bool, depth: int, alpha: float=-inf, beta: float=inf):
        # base case
        if depth == 0 or self.game.game_over(board):
            return [self.game.game_score(board, self.player, END_SCORES, BOARD_SCORES), None]

        # first move for white
        if len(board.move_stack) == 0:
            white_opening = choice(("e2e4", "d2d4", "c2c4", "g1f3"))
            return white_opening

        moves = self.game.sorted_moves_with_h_function(board, player, self.limit)

        if board.turn == player:
            maxScore, bestMove = -inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, not player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)
                if self.generate_data and depth == DEFAULT_DEPTH:
                    write_to_csv_list(h_value + [score[0]])
                
                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")

                alpha = max(alpha, score[0])
                if beta <= alpha:
                    break

                if score[0] >= maxScore:
                    maxScore = score[0]
                    bestMove = move

            return [maxScore, bestMove]
        else:
            minScore, bestMove = inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)
                if self.generate_data and depth == DEFAULT_DEPTH:
                    write_to_csv_list(h_value + [score[0]])

                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")
                
                beta = min(beta, score[0])
                if beta <= alpha:
                    break

                if score[0] <= minScore:
                    minScore = score[0]
                    bestMove = move

            return [minScore, bestMove]

    def move(self, board: Board) -> str:
        best_move = self._minimax(board, self.player, self.depth)
        if type(best_move) == str:
            return best_move
        return best_move[1].uci()
    
class MiniMaxPlayerWithHFunctionPrediction(Player):
    def __init__(self, player, game: Game=ChessGame(), depth=DEFAULT_DEPTH, choice_limit=-1, verbose=False, generate_data=False):
        super().__init__(player, game, f"minimax with new H function prediction, depth = {depth}, limit = {choice_limit}")
        self.depth = depth
        self.verbose = verbose
        # limit number of choices
        self.limit = choice_limit
        self.generate_data = generate_data

    def _minimax(self, board: Board, player: bool, depth: int, alpha: float=-inf, beta: float=inf):
        # base case
        if depth == 0 or self.game.game_over(board):
            return [self.game.game_score(board, self.player, END_SCORES, BOARD_SCORES), None]

        # first move for white
        if len(board.move_stack) == 0:
            white_opening = choice(("e2e4", "d2d4", "c2c4", "g1f3"))
            return white_opening

        moves = self.game.sorted_moves_with_h_function_prediction(board, player, self.limit)
        return moves[0][::-1]

        if board.turn == player:
            maxScore, bestMove = -inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, not player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)
                
                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")

                alpha = max(alpha, score[0])
                if beta <= alpha:
                    break

                if score[0] >= maxScore:
                    maxScore = score[0]
                    bestMove = move

            return [maxScore, bestMove]
        else:
            minScore, bestMove = inf, None

            for move, h_value in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self._minimax(test_board, player, depth - 1, alpha, beta)
                # print('score', score, 'H' + str(DEFAULT_DEPTH - depth), h_value, depth)

                if self.verbose:
                    log.info(f"{self.game.turn_side(test_board)}, M{len(moves)}, D{depth}:{move} - SCORE: {score}")
                
                beta = min(beta, score[0])
                if beta <= alpha:
                    break

                if score[0] <= minScore:
                    minScore = score[0]
                    bestMove = move

            return [minScore, bestMove]

    def move(self, board: Board) -> str:
        best_move = self._minimax(board, self.player, self.depth)
        if type(best_move) == str:
            return best_move
        return best_move[1].uci()
    
if __name__ == "__main__":
    test_board = Board()
    chess_game = ChessGame()
    test_bot = MiniMaxPlayerWithRegressor(player=True, game=chess_game, verbose=False)

    start_time = time()
    print(test_bot._minimax(test_board, True, 5))
    # print(test_bot.move(test_board))
    print(time() - start_time)