from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
# Actions
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction


def render_menu(media_type = None):

    from preferences import PREF_KEYWORD

    items = []

    description = 'This will show you the same results as browsing OpenSubtitles!'

    if media_type is not None:
        description = 'This will filter the results to match only with ' + media_type

    # Render info item
    items.append( ExtensionResultItem(icon = 'images/.svg',
                                    name = 'Start typing to search...',
                                    description = description,
                                    highlightable = False,
                                    on_enter = DoNothingAction()) )

    # No need to show the media types that can be searched
    if media_type:
        return items

    _MENU_ITEMS = [
        ('Search Movies', 'm'),
        ('Search TV Shows', 'tv')
    ]

    # Render menu items
    for menu_item in _MENU_ITEMS:
        action_query = PREF_KEYWORD + ' ' + menu_item[1] + ' '
        media_type = menu_item[0].replace("Search ", "")
        items.append( ExtensionResultItem(icon = 'images/%s.png' % menu_item[1],
                                    name = menu_item[0],
                                    description = "Filters the search results to %s" % media_type,
                                    highlightable = True,
                                    on_enter = SetUserQueryAction(action_query)) )

    return items

def render_search_tv(query):
    from preferences import PREF_KEYWORD
    import api
    items = []
    tv_shows = api.search_shows(query)
    
    for show in tv_shows:
        if show.rating:
            description = 'IMDB rating: %s' % show.rating
        else:
            description = ''
        items.append( ExtensionResultItem(icon = 'images/tv.png',
                                name = '%s (%s)' % (show.name, show.year),
                                description = description,
                                highlightable = True,
                                on_enter = SetUserQueryAction(PREF_KEYWORD + ' -' + str(show._id) + ' s')) )

    # If it's empty
    if not items:
        items.append( not_found_item(query) )   

    return items

def render_search_movies(query):
    from preferences import PREF_KEYWORD
    import api
    items = []
    movies = api.search_movies(query)
    
    for movie in movies:
        if movie.rating:
            description = 'IMDB rating: %s' % movie.rating
        else:
            description = ''
        items.append( ExtensionResultItem(icon = 'images/m.png',
                                name = '%s (%s)' % (movie.name, movie.year),
                                description = description,
                                highlightable = True,
                                on_enter = SetUserQueryAction(PREF_KEYWORD + ' -' + str(movie._id) + ' ')) )

    # If it's empty
    if not items:
        items.append( not_found_item(query) )        

    return items

def not_found_item(query):
    return ExtensionResultItem(icon = 'images/not_found.png',
                               name = "No results were found for '%s'" % query.rstrip(),
                               description = 'Maybe there are no subtitles for this?',
                               highlightable = False,
                               on_enter = DoNothingAction())

def render_media(media_id):
    from languages import LANGUAGES
    import api
    
    try:
        media_results = api.get_media(media_id)
    except Exception:
        # It's a TV Show
        return render_episode_not_specified()

    items = []
    for result in media_results:
        uploader = result.uploader or 'UNKOWN'
        uploader_badge = ''
        if result.uploader_badge:
            uploader_badge = '[%s]' % result.uploader_badge
        items.append(
            ExtensionResultItem(icon = 'images/languages/%s.svg' % LANGUAGES[result.language],
                                name = 'Uploaded by %s [%s]' % (uploader, uploader_badge),
                                description = '%s | (%s)' % (result.video_source_name, result.language),
                                highlightable = True,
                                on_enter = ExtensionCustomAction(data = {'download': {'url': result.url, 'download_id': result.download_id}}, keep_app_open=True))
        )

    # If there are no results
    if not items:
        return [ ExtensionResultItem(icon = 'images/not_found.png',
                               name = "No results were found for '%s'" % media_id,
                               description = 'Maybe there are no subtitles for this?',
                               highlightable = False,
                               on_enter = DoNothingAction()) ]

    return items[:5]

def render_episode_not_specified():
    return [ ExtensionResultItem(icon = 'images/tv.png',
                               name = "You need to specify an episode. (Eg. 's01e01')",
                               description = "Try typing 's' followed by the number of the season.",
                               highlightable = False,
                               on_enter = DoNothingAction()) ]

def render_episode(media_id, episode_designator):
    from languages import LANGUAGES
    import re
    import api

    info = re.findall(r'\d+', episode_designator)
    season = str(int(info[0]))
    episode = info[1]
    try:
        episode_results = api.get_episode(media_id, season, episode)
    except:
        # TODO Render error message
        pass

    items = []
    for result in episode_results:
        uploader = result.uploader or 'UNKOWN'
        uploader_badge = ''
        if result.uploader_badge:
            uploader_badge = '[%s]' % result.uploader_badge

        items.append( ExtensionResultItem(icon = 'images/languages/%s.svg' % LANGUAGES[result.language],
                                name = 'Uploaded by %s [%s]' % (uploader, uploader_badge),
                                description = '%s | (%s)' % (result.video_source_name, result.language),
                                highlightable = True,
                                on_enter = ExtensionCustomAction(data = {'download': {'url': result.url, 'download_id': result.download_id}}, keep_app_open=True)))

    # If it's empty
    if not items:
        items.append( not_found_item(episode_designator) )   

    return items[:5]
    