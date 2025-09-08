from dataclasses import dataclass


@dataclass(frozen=True)
class Piece:
    height: int
    color: int
    shape: int
    fill: int

    def to_bits(self) -> int:
        """Returns the Piece object as a 4 bits representation"""
        return (self.height << 3) | (self.color << 2) | (self.shape << 1) | self.fill

    def __str__(self) -> str:
        """Returns piece number (1 to 15)"""
        return f" {self.to_bits():02d}"


def generate_all_pieces() -> list[Piece]:
    """Generates all 16 unique pieces"""
    return [Piece((i>>3) & 1,
                  (i>>2) & 1,
                  (i>>1) & 1,
                  (i) & 1)
            for i in range(16)
    ]
