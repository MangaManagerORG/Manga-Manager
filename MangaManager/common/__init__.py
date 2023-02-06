from .models import PeopleTags


def get_invalid_person_tag(people: str):
    """ Validates that a common separated list or single person is a valid Person tag"""
    invalid_people = []
    for person in people.split(","):
        if person.trim() not in list(PeopleTags):
            invalid_people.append(person.trim())
    return invalid_people