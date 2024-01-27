from enum import Enum

# Keep this ordered in terms of progressing ratings, rather than alphabetical
class AgeRating(str, Enum):
    UNKNOWN = 'Unknown'
    RATING_PENDING = 'Rating Pending'
    EARLY_CHILDHOOD = 'Early Childhood'
    EVERYONE = 'Everyone'
    G = 'G'
    EVERYONE_10 = 'Everyone 10+'
    PG = 'PG'
    KIDSTO_ADULTS = 'Kids to Adults'
    TEEN = 'Teen'
    MA_15 = 'MA15+'
    MATURE_17 = 'Mature 17+'
    M = 'M'
    R_18 = 'R18+'
    ADULTS_ONLY_18 = 'Adults Only 18+'
    X_18 = 'X18+'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
