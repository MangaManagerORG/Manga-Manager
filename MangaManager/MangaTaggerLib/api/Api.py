import logging
import requests

class AniList:
    _log = None

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _post(cls, query, variables, logging_info):
        try:
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Tagger is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None

        cls._log.debug(f'Query: {query}')
        cls._log.debug(f'Variables: {variables}')
        cls._log.debug(f'Response JSON: {response.json()}')

        return response.json()['data']['Media']

    @classmethod
    def search_staff_by_mal_id(cls, mal_id, logging_info):
        query = '''
        query search_staff_by_mal_id ($mal_id: Int) {
          Media (idMal: $mal_id, type: MANGA) {
            siteUrl
            staff {
              edges {
                node{
                  name {
                    first
                    last
                    full
                    alternative
                  }
                  siteUrl
                }
                role
              }
            }
          }
        }
        '''

        variables = {
            'mal_id': mal_id
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def search_for_manga_title_by_mal_id(cls, mal_id, logging_info):
        query = '''
        query search_manga_by_mal_id ($mal_id: Int) {
          Media (idMal: $mal_id, type: MANGA) {
            title {
              romaji
              english
              native
            }
          }
        }
        '''

        variables = {
            'mal_id': mal_id
        }

        return cls._post(query, variables, logging_info)


if __name__ == "__main__":
    AniList.initialize()