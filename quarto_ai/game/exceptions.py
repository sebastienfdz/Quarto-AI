class QuartoError(Exception):
    """Common base class for all Quarto exceptions."""
    pass

class GameEndedError(QuartoError):
    pass

class BoardError(QuartoError):
    pass

class IllegalMoveError(QuartoError):
    pass

class InvalidPieceError(IllegalMoveError):
    pass

class InvalidSquareError(IllegalMoveError):
    pass
