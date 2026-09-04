from enum import Enum, IntEnum, auto


class Player(IntEnum):
    """
    Represents the two players in a Quarto game.
    Underlying values (0 and 1) can be safely used as indices.
    """

    PLAYER_1 = 0
    PLAYER_2 = 1

    @property
    def opponent(self) -> "Player":
        """Returns the opposing player."""
        return Player.PLAYER_1 if self == Player.PLAYER_2 else Player.PLAYER_2


class GamePhase(Enum):
    """
    Represents the distinct phases of a single Quarto turn.
    In Quarto a turn is split in two actions:
        1. Place the given piece on the board.
        2. Select a piece for the opponent.
    """

    PLACEMENT = auto()
    SELECTION = auto()

    @property
    def change_phase(self) -> "GamePhase":
        """Returns the other phase."""
        return GamePhase.PLACEMENT if self == GamePhase.SELECTION else GamePhase.SELECTION


class GameResult(IntEnum):
    """
    Represents the final outcome of a completed Quarto game.
    """

    PLAYER_1 = Player.PLAYER_1.value
    PLAYER_2 = Player.PLAYER_2.value
    DRAW = auto()
