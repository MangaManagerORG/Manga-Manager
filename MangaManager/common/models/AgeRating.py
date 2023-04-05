from enum import Enum


class AgeRating(str, Enum):
    UNKNOWN = 'Unknown'
    ADULTS_ONLY_18 = 'Adults Only 18+'
    EARLY_CHILDHOOD = 'Early Childhood'
    EVERYONE = 'Everyone'
    EVERYONE_10 = 'Everyone 10+'
    G = 'G'
    KIDSTO_ADULTS = 'Kids to Adults'
    M = 'M'
    MA_15 = 'MA15+'
    MATURE_17 = 'Mature 17+'
    PG = 'PG'
    R_18 = 'R18+'
    RATING_PENDING = 'Rating Pending'
    TEEN = 'Teen'
    X_18 = 'X18+'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
