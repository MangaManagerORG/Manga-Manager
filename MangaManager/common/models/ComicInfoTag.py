from common.models import AgeRating


class SeriesTag:
    default = ""
    tag_name = "Series"
    options = None


class AgeRatingTag:
    default = ""
    tag_name = "AgeRating"
    options = AgeRating.list()
