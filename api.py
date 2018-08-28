import requests

from languages import LANGUAGES

BASE_URL = 'https://www.opensubtitles.org'
    
def search(query):
    return

def search_movies(query):
    suggestions = suggest_media(query)
    movies = list( filter( lambda item: item.kind == MOVIE, suggestions) )
    return movies

def search_shows(query):
    suggestions = suggest_media(query)
    tv_shows = list( filter( lambda item: item.kind == TV_SHOW, suggestions) )
    return tv_shows

def get_episode(imdb_id, season_nr, episode_nr, language = LANGUAGES['ALL']):
    #TODO: Fix this
    #url = BASE_URL + '/en/search/sublanguageid-%s/pimdbid-%s/season-%d/episode-%d' % (language, imdb_id, season_nr, episode_nr) 
    url = 'https://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-4807334'
    response_body = requests.get(url).text
    
    # TODO: Check for season or episode number out of bounds
    # Parse HTML to find info
    from bs4 import BeautifulSoup
    import re
    body = BeautifulSoup(response_body, 'html.parser')
    result_list = body.find(id = 'search_results')
    result_items = result_list.find_all(id = re.compile(r'^name(\d)*$'))
    
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

        extra = '/en/ssearch/pimdbid-4145054/season-1/episode-3/sublanguageid-'
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
        new_item.video_source_name = video_source_name.strip().replace('\n', '')
        new_item.language = language
        new_item.uploader = uploader
        new_item.uploader_badge = uploader_badge
        new_item.download_id = download_id
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

        
class SearchResultItem:
    url = ''
    video_source_name = ''
    language = ''
    uploader = ''
    uploader_badge = ''
    download_link = ''


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