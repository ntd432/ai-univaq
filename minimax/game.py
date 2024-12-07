from abc import abstractmethod

class Game():
    def __init__(self):
        return
    
    @abstractmethod
    def game_over(self, claim_draw: bool=False):
        pass

    @abstractmethod
    def game_score(self):
        pass

    @abstractmethod
    def sorted_moves(self):
        pass

    @abstractmethod
    def turn_side(self):
        pass