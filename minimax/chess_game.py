import chess

from random import random
from game import Game
from chess import Board
from typing import List

try:
    from config import BOARD_SCORES, END_SCORES
except ModuleNotFoundError:
    from .config import BOARD_SCORES, END_SCORES

NAME_TO_SQUARE = dict(zip(chess.SQUARE_NAMES, chess.SQUARES))

class ChessGame(Game):
    def __init__(self):
        super().__init__()
    
    def game_over(self, board: Board, claim_draw: bool=False):
        if board.is_game_over(claim_draw=claim_draw):
            return True

        return False
    
    def check_win(self, board: Board, player: bool) -> bool:
        if board.is_checkmate() and board.turn == (not player):
            return True

        return False


    def check_tie(self, board: Board, claim_draw: bool=False) -> bool:
        tie = (board.is_stalemate() or
                board.is_fivefold_repetition() or
                board.is_insufficient_material())

        if claim_draw:
            tie = tie or board.can_claim_draw()

        if tie:
            return True

        return False
    
    def game_score(self, board, player, end_scores_policy=END_SCORES, board_scores_policy=BOARD_SCORES) -> float:
        score = None

        if self.check_tie(board):
            score = end_scores_policy["TIE"]
        elif self.check_win(board, player):
            score = end_scores_policy["WIN"]
        elif self.check_win(board, not player):
            score = end_scores_policy["LOSE"]
        else:
            score = self.eval_board_state(board, player, board_scores_policy)

        return score
    
    def eval_board_state(self, board, player: bool, board_scores_policy: dict) -> float:
        total_score = random() 

        for piece, score in board_scores_policy.items():
            piece = getattr(chess, piece)

            true_score = len(board.pieces(piece, player)) * score
            false_score = len(board.pieces(piece, not player)) * score * -1

            total_score += (true_score + false_score)

        return total_score


    def sorted_moves(self, board: Board, limit: int=-1) -> List[str]:
        moves = list(board.legal_moves)

        squares = [NAME_TO_SQUARE[name] for name in map(self.square_name, moves)]
        pieces = [board.piece_type_at(square) for square in squares]

        moves = sorted(zip(moves, pieces), key=lambda x: x[1], reverse=True)
        return moves if limit == -1 else moves[:limit]
    
    # SORT WITH MODEL PREDICTION
    # def sorted_moves(self, board: Board, limit: int=-1) -> List[str]:
    #     moves = list(board.legal_moves)

    #     squares = [NAME_TO_SQUARE[name] for name in map(self.square_name, moves)]
    #     pieces = [board.piece_type_at(square) for square in squares]

    #     moves = sorted(zip(moves, pieces), key=lambda x: x[1], reverse=True)
    #     return moves if limit == -1 else moves[:limit]
    
    def square_name(self, move):
        return move.uci()[:2]


    def turn_side(self, board):
        side = "White" if board.turn == True else "Black"
        
        return side
    
if __name__ == "__main__":
    test_board = chess.Board()
    game = ChessGame()

    print(game.sorted_moves(test_board))
    # print(eval_board_state(test_board, True, BOARD_SCORES))
    # print(game_score(test_board, True))