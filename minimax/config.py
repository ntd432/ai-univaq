DEFAULT_DEPTH = 3
DATA = "data.csv"
LAYERS_SIZE=[1, 64, 32, 16, 1]
DATA_2 = "data2.csv"
LAYERS_SIZE_2=[4, 64, 32, 16, 1]
NUMBER_OF_GAMES=1

BOARD_SCORES = {
    "PAWN": 1,
    "BISHOP": 4,
    "KING": 0,
    "QUEEN": 10,
    "KNIGHT": 5,
    "ROOK": 3
}

# max board score for player == 42 < WIN
END_SCORES = {
    "WIN": 100,
    "LOSE": -100,
    "TIE": 0,
}


PIECES = {
    1: "PAWN",
    2: "KNIGHT",
    3: "BISHOP",
    4: "ROOK",
    5: "QUEEN",
    6: "KING"
}