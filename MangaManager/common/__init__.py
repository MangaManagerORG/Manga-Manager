from ComicInfo.models import PeopleTags


def get_invalid_person_tag(people: str):
    """ Validates that a common separated list or single person is a valid Person tag"""
    invalid_people = []
    for person in [p.strip() for p in people.split(",") if p != ""]:
        if person not in list(PeopleTags):
            invalid_people.append(person)
    return invalid_people
