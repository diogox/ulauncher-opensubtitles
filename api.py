from bs4 import BeautifulSoup
import requests

from languages import LANGUAGES
from preferences import PREF_MAIN_LANGUAGE

BASE_URL = 'https://www.opensubtitles.org'
    
def search(query):
    return

def get_media(_id, language, id_type = 'idmovie', is_media_hash = False):
    if language == '':
        language = PREF_MAIN_LANGUAGE
    
    if not is_media_hash:
        media_url = 'https://www.opensubtitles.org/en/search/sublanguageid-%s/%s-%s' % (language, id_type, _id)
    else:
        media_url = 'https://www.opensubtitles.org/en/search/sublanguageid-%s/moviehash-%s' % (language, _id)

    response_body = requests.get(media_url).text
    body = BeautifulSoup(response_body, 'html.parser').find('div', class_='content')

    # DON'T JUDGE ME! I just want to get this done...
    if is_media_hash:
        media_schema = 'http://schema.org/Movie'
    else:
        media_schema = body.find('h1').parent.parent['itemtype']

    if media_schema == 'http://schema.org/Movie':
        # Parse it as a movie
        result_list = body.find(id = 'search_results')
        results = parse_search_results(result_list)
    elif media_schema == 'http://schema.org/TVSeries':
        # Can't parse TV Shows, episode must be specified, in which case the 'Movie' parsing applies
        raise Exception('tv')

    return results

def search_movies(query):
    suggestions = suggest_media(query)
    movies = list( [item for item in suggestions if item.kind == MOVIE] )
    return movies

def search_shows(query):
    suggestions = suggest_media(query)
    tv_shows = list( [item for item in suggestions if item.kind == TV_SHOW] )
    return tv_shows

def get_episode(show_id, season_nr, episode_nr, language = PREF_MAIN_LANGUAGE):
    import re

    url = 'https://www.opensubtitles.org/en/ssearch/sublanguageid-%s/idmovie-%s' % (language, show_id)
    response_body = requests.get(url).text
    result_list = BeautifulSoup(response_body, 'html.parser').find(id = 'search_results')
    season_items = result_list.find(id = re.compile('^season-(0)*(%s)$' % season_nr)).parent.parent
    episode_item = None

    for _ in range( int(episode_nr) ):
        episode_item = season_items.next_sibling

    episode_url = episode_item.find('a')['href']

    extra = '/en/search/sublanguageid-%s/imdbid-' % language
    episode_id = episode_url.replace(extra, '')
    return get_media(episode_id, language, 'imdbid')

class SearchResultItem:
    url = ''
    video_source_name = 'untitled'
    language = ''
    uploader = ''
    uploader_badge = ''
    download_id = ''

def parse_search_results(search_results_node):
    import re
    from main import logger
    result_items = search_results_node.find_all(id = re.compile(r'^name(\d)*$'))
    # Get info from each item
    search_result_items = []
    for item in result_items:
        
        # Get columns
        columns = item.find_all('td')
        language_column = columns[1]
        download_column = columns[4]
        uploader_column = columns[8]

        # Find info
        url = item.find('strong').find('a')['href']
        video_source_name = item.find('br').next_sibling

        language = language_column.find('a')['title']

        uploader = uploader_column.text.strip()
        uploader_badge = uploader_column.find('img')
        if uploader_badge:
            uploader_badge = uploader_badge['title']
        else:
            uploader_badge = ''

        download_id = download_column.find('a')['href'].replace('/en/subtitleserve/sub/', '')
        # Create new item with info
        new_item = SearchResultItem()
        new_item.url = BASE_URL + url
        new_item.language = language
        new_item.uploader = uploader
        new_item.uploader_badge = uploader_badge
        new_item.download_id = download_id

        # Some entries have no name, in which case it should just keep the default (in the class)
        try:
            new_item.video_source_name = video_source_name.strip().replace('\n', '')
        except:
            pass

        # Append it to list
        search_result_items.append( new_item )
    return search_result_items


class Suggestion:
    _id = 0
    name = ''
    year = ''
    total = ''
    pic = ''
    kind = ''
    rating = ''

def suggest_media(query):
    suggestions = requests.get('https://www.opensubtitles.org/libs/suggest.php?format=json3&MovieName=%s&SubLanguageID=null' % query).json()

    suggestion_list = []
    for item in suggestions:
        suggestion = Suggestion()
        suggestion._id = item['id']
        suggestion.name = item['name']
        suggestion.year = item['year']
        suggestion.total = item['total']
        suggestion.pic = item['pic']
        suggestion.kind = item['kind']
        suggestion.rating = item['rating']
        
        suggestion_list.append(suggestion)
    
    return suggestion_list


# Fixtures
MOVIE = 'movie'
TV_SHOW = 'tv'

class MediaItem:
    def __init__(self):
        self.id = '12345'
        self.title = 'Westworld'
        self.description = 'An AI Theme Park'
        self.release_year = '2015'
        self.type = TV_SHOW