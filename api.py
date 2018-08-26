class API:
    def __init__(self):
        pass
    
    def search(self):
        pass

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