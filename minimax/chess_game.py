import chess
import torch

from random import random
from game import Game
from chess import Board
from typing import List
from mlp import FlexibleMLP

try:
    from config import BOARD_SCORES, END_SCORES, LAYERS_SIZE, LAYERS_SIZE_2
except ModuleNotFoundError:
    from .config import BOARD_SCORES, END_SCORES, LAYERS_SIZE, LAYERS_SIZE_2

NAME_TO_SQUARE = dict(zip(chess.SQUARE_NAMES, chess.SQUARES))

class ChessGame(Game):
    def __init__(self):
        super().__init__()
        self.model = FlexibleMLP(LAYERS_SIZE)
        self.second_model = FlexibleMLP(LAYERS_SIZE_2)
        self.model.load_state_dict(torch.load("model.pth"))
    
    def predict_h(self, h0):
        return self.model(torch.tensor([[float(h0)]]))[0][0].item()
    
    def predict_h(self, h: list):
        return self.second_model(torch.tensor([[float(i) for i in h]]))[0][0].item()
    
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
    
    def game_score_with_h(self, board, player, end_scores_policy=END_SCORES, board_scores_policy=BOARD_SCORES) -> float:
        score = None

        if self.check_tie(board):
            score = [end_scores_policy["TIE"]] * 4
        elif self.check_win(board, player):
            score = [end_scores_policy["WIN"]] * 4
        elif self.check_win(board, not player):
            score = [end_scores_policy["LOSE"]] * 4
        else:
            score = [self.eval_board_state(board, player, board_scores_policy), 
                     self.eval_board_state_material_control(board, player, board_scores_policy=BOARD_SCORES),
                     self.eval_board_state_mobility(board, player, board_scores_policy=BOARD_SCORES),
                     self.eval_board_state_position(board, player, board_scores_policy=BOARD_SCORES)]

        return score
    
    def eval_board_state(self, board, player: bool, board_scores_policy: dict) -> float:
        total_score = random() 

        for piece, score in board_scores_policy.items():
            piece = getattr(chess, piece)

            true_score = len(board.pieces(piece, player)) * score
            false_score = len(board.pieces(piece, not player)) * score * -1

            total_score += (true_score + false_score)

        return total_score

    def sorted_moves(self, board: Board, player: bool, limit: int=-1) -> List[str]:
        moves = list(board.legal_moves)
        scores = []
        for move in moves:
            copy_board = board.copy()
            copy_board.push(move)
            scores.append(self.game_score(copy_board, player))

        moves = sorted(zip(moves, scores), key=lambda x: x[1], reverse=True)
        return moves if limit == -1 else moves[:limit]
    
    # SORT WITH MODEL PREDICTION with one H value
    def sorted_moves_prediction(self, board: Board, player: bool, limit: int=-1) -> List[str]:
        moves = list(board.legal_moves)
        scores = []
        for move in moves:
            copy_board = board.copy()
            copy_board.push(move)
            scores.append(self.predict_h(self.game_score(copy_board, player)))

        moves = sorted(zip(moves, scores), key=lambda x: x[1], reverse=True)
        return moves if limit == -1 else moves[:limit]
    
    def sorted_moves_with_h_function(self, board: Board, player: bool, limit: int=-1) -> List[str]:
        moves = list(board.legal_moves)
        scores = []
        for move in moves:
            copy_board = board.copy()
            copy_board.push(move)
            scores.append(self.game_score_with_h(copy_board, player))

        moves = sorted(zip(moves, scores), key=lambda x: sum(x[1]), reverse=True)
        return moves if limit == -1 else moves[:limit]
    
    def sorted_moves_with_h_function_prediction(self, board: Board, player: bool, limit: int=-1) -> List[str]:
        moves = list(board.legal_moves)
        scores = []
        for move in moves:
            copy_board = board.copy()
            copy_board.push(move)
            scores.append(self.predict_h(self.game_score_with_h(copy_board, player)))

        moves = sorted(zip(moves, scores), key=lambda x: x[1], reverse=True)
        return moves if limit == -1 else moves[:limit]
    
    def eval_board_state_material_control(self, board, player: bool, board_scores_policy: dict) -> float:
        total_score = random()

        # Material evaluation
        for piece, score in board_scores_policy.items():
            piece = getattr(chess, piece)

            true_score = len(board.pieces(piece, player)) * score
            false_score = len(board.pieces(piece, not player)) * score * -1

            total_score += (true_score + false_score)

        # Center control evaluation
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        for square in center_squares:
            if board.is_attacked_by(player, square):
                total_score += 0.5  # Bonus for controlling the center
            if board.is_attacked_by(not player, square):
                total_score -= 0.5  # Penalty for opponent controlling the center

        return total_score
    
    def eval_board_state_position(self, board, player: bool, board_scores_policy: dict) -> float:
        total_score = random()

        # Material evaluation
        for piece, score in board_scores_policy.items():
            piece = getattr(chess, piece)

            true_score = len(board.pieces(piece, player)) * score
            false_score = len(board.pieces(piece, not player)) * score * -1

            total_score += (true_score + false_score)

        # Positional evaluation
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == player:
                if piece.piece_type == chess.PAWN:
                    # Bonus for pawns closer to promotion
                    rank = chess.square_rank(square)
                    if player == chess.WHITE:
                        total_score += (rank - 1) * 0.1  # Closer to rank 7 for White
                    else:
                        total_score += (6 - rank) * 0.1  # Closer to rank 2 for Black
                elif piece.piece_type in {chess.KNIGHT, chess.BISHOP}:
                    # Bonus for central position
                    if square in [chess.D4, chess.D5, chess.E4, chess.E5]:
                        total_score += 0.3

        return total_score
    
    def eval_board_state_mobility(self, board, player: bool, board_scores_policy: dict) -> float:
        total_score = random()

        # Material evaluation
        for piece, score in board_scores_policy.items():
            piece = getattr(chess, piece)

            true_score = len(board.pieces(piece, player)) * score
            false_score = len(board.pieces(piece, not player)) * score * -1

            total_score += (true_score + false_score)

        # Mobility evaluation
        if board.turn == player:
            legal_moves = len(list(board.legal_moves))
            total_score += legal_moves * 0.1  # Bonus for mobility
        else:
            board.turn = not player
            opponent_legal_moves = len(list(board.legal_moves))
            total_score -= opponent_legal_moves * 0.1
            board.turn = player  # Restore the turn

        return total_score

    def square_name(self, move):
        return move.uci()[:2]


    def turn_side(self, board):
        side = "White" if board.turn == True else "Black"
        
        return side
    
if __name__ == "__main__":
    test_board = chess.Board()
    game = ChessGame()

    print(game.sorted_moves(test_board, False))
    # print(eval_board_state(test_board, True, BOARD_SCORES))
    # print(game_score(test_board, True))