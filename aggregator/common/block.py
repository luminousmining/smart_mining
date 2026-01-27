class BLOCK_STATUS:

    UNKNOWN = None
    CANDIDATE: str = 'candidate'
    IMMATURE: str = 'immature'
    MATURED: str = 'matured'


class Block:

    def __init__(self):
        self.tag = None
        self.height = None
        self.timestamp = None
        self.difficulty = None
        self.luck = None
        self.status = BLOCK_STATUS.UNKNOWN

    def merge(self, other, new_assign: bool=False) -> None:
        #######################################################################
        if not new_assign:
            self.tag = self.tag if self.tag else other.tag
            self.height = self.height if self.height else other.height
            self.timestamp = self.timestamp if self.timestamp else other.timestamp
            self.difficulty = self.difficulty if self.difficulty else other.difficulty
            self.luck = self.luck if self.luck else other.luck
            self.status = self.status if self.status else other.status
        else:
            self.tag = other.tag if other.tag else self.tag
            self.height = other.height if other.height else self.height
            self.timestamp = other.timestamp if other.timestamp else self.timestamp
            self.difficulty = other.difficulty if other.difficulty else self.difficulty
            self.luck = other.luck if other.luck else self.luck
            self.status = other.status if other.status else self.status

        #######################################################################
        if self.status != BLOCK_STATUS.UNKNOWN:
            if self.status != BLOCK_STATUS.CANDIDATE and self.status != BLOCK_STATUS.IMMATURE and self.status != BLOCK_STATUS.MATURED:
                self.status = BLOCK_STATUS.UNKNOWN

    def to_dict(self) -> dict:
        data = {
            'height': self.height,
            'timestamp': self.timestamp,
            'difficulty': self.difficulty,
            'luck': self.luck,
            'status': self.status
        }
        return data
