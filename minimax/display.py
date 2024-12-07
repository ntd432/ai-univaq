import pandas as pd

from chess import Board 

from itertools import count
from time import sleep, time
from random import choice
from tqdm.notebook import tqdm
from chess_game import ChessGame

from IPython.display import display, clear_output, HTML

try:
    from config import BOARD_SCORES
except ModuleNotFoundError:
    from .config import BOARD_SCORES


class GameVisualize:
    def __init__(self, board: Board=None):
        # for games with specific starting point
        if board:
            self.board = board
        else:
            self.board = Board()
        self.game = ChessGame()

    def _game(self, white_p, black_p, visual=False, pause=1):
        board = self.board.copy()
        result = None
        start_time = time()
        white_time = []
        black_time = []
        white_win = False

        try:
            for i in count():
                if visual:
                    display(board)
                    white_score = self.game.eval_board_state(board, True, board_scores_policy=BOARD_SCORES)
                    black_score = self.game.eval_board_state(board, False, board_scores_policy=BOARD_SCORES)
                    display(HTML(f'<div>WHITE: {white_p.solver}  SCORE: {white_score}</div>'))
                    display(HTML(f'<div>BLACK: {black_p.solver} SCORE: {black_score}</div>'))
                    sleep(pause)

                if self.game.game_over(board, claim_draw=True):
                    white_win = white_score > black_score
                    break

                if board.turn:
                    tmp_time = time()
                    move = white_p.move(board)
                    white_time.append(time() - tmp_time)
                else:
                    tmp_time = time()
                    move = black_p.move(board)
                    black_time.append(time() - tmp_time)

                board.push_uci(move)
                if visual:
                    clear_output(wait=True)
        except KeyboardInterrupt:
            print("Game stopped!")
            
        if self.game.check_tie(board, claim_draw=False):
            result = -1
        else:
            result = int(self.game.check_win(board, True))

        if visual:
            display(HTML(f"<div>RESULT: {'WHITE' if white_win else 'BLACK'} wins</div>"))

        result_stat = {
            "white": white_p.solver, 
            "black": black_p.solver, 
            "FEN": board.fen(), 
            "last_move": board.peek(), 
            "moves_history": [move.uci() for move in board.move_stack],
            "moves": i, "time": round(time() - start_time, 2),
            "black_time": black_time,
            "white_time": white_time,
            "white_win": white_win,
            "result": result
            }
            
        return result_stat

    def start_game(self, player_1, player_2, visual=False, pause=1, random=False):
        if random:
            goes_first = choice([True, False])
            
            if goes_first:
                result = self._game(player_1, player_2, visual, pause)
            else:
                player_1.player = False
                player_2.player = True
                result = self._game(player_2, player_1, visual, pause)
        else:
            result = self._game(player_1, player_2, visual, pause)
                
        return result

    def start_games(self, player_1, player_2, n=10):
        results = {}

        for i in tqdm(range(n)):
            result = self.start_game(player_1, player_2)
            results[i] = result

        return pd.DataFrame.from_dict(results, orient="index")