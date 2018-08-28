from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
# Actions
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction


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
                                on_enter = SetUserQueryAction(PREF_KEYWORD + ' -' + str(show._id))) )

    # If it's empty
    if not items:
        # TODO: stylize
        items.append( ExtensionResultItem(icon = 'images/.png',
                                name = "No results were found for '%s'" % query.rstrip(),
                                description = 'Maybe there are no subtitles for this?',
                                highlightable = False,
                                on_enter = DoNothingAction()))

    return items

def render_search_movies(query):
    from preferences import PREF_KEYWORD
    import api
    items = []
    tv_shows = api.search_movies(query)
    
    for movie in tv_shows:
        if movie.rating:
            description = 'IMDB rating: %s' % movie.rating
        else:
            description = ''
        items.append( ExtensionResultItem(icon = 'images/m.png',
                                name = '%s (%s)' % (movie.name, movie.year),
                                description = description,
                                highlightable = True,
                                on_enter = SetUserQueryAction(PREF_KEYWORD + ' -' + str(movie._id))) )

    # If it's empty
    if not items:
        # TODO: stylize
        items.append( ExtensionResultItem(icon = 'images/.png',
                                name = "No results were found for '%s'" % query.rstrip(),
                                description = 'Maybe there are no subtitles for this?',
                                highlightable = False,
                                on_enter = DoNothingAction()))

    return items