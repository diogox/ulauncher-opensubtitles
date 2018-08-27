BASE_URL = 'https://www.opensubtitles.org'

class API:
    
    def get_episode(self, imdb_id, season_nr, episode_nr, language = 'all'):
        import requests
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

            extra = '/en/search/pimdbid-4145054/season-1/episode-3/sublanguageid-'
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
        
class SearchResultItem:
    url = ''
    video_source_name = ''
    language = ''
    uploader = ''
    uploader_badge = ''
    download_link = ''


# Fixtures
MOVIE = 'movie'
TV_SHOW = 'tv_show'

class MediaItem:
    def __init__(self):
        self.id = '12345'
        self.title = 'Westworld'
        self.description = 'An AI Theme Park'
        self.release_year = '2015'
        self.type = TV_SHOW