import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)

import screens

class OpenSubtitlesExtension(Extension):

    def __init__(self):
        super(OpenSubtitlesExtension, self).__init__()

        # Subscribe to events
        self.subscribe(PreferencesEvent, PreferencesEventListener()) # Set preferences to inner members
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def show_menu(self):
        return RenderResultListAction( screens.render_menu() )

    def show_search_media_menu(self, command):
        if command == 'm':
            media_type = 'Movies'
        else:
            media_type = 'TV Shows'

        return RenderResultListAction( screens.render_menu(media_type) )

    def show_search_media(self, command, query):
        items = []
        if command == 'm':
            items = screens.render_search_movies(query)
        else:
            items = screens.render_search_tv(query)

        return RenderResultListAction( items )

    def show_media(self, media_id, language):
        return RenderResultListAction( screens.render_media(media_id, language) )

    def show_episode(self, media_id, episode_designator, language):
        return RenderResultListAction( screens.render_episode(media_id, episode_designator, language) )

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        import re

        argument = event.get_argument()
        if argument is None:
            return extension.show_menu()
        else:
            argument = argument.strip()
        
        commands = argument.split()

        # Search for media type
        if re.match(r'^(tv|m)$', commands[0], re.IGNORECASE):

            # There's nothing to search yet
            if len( commands ) is 1:
                
                # Show media type search menu 
                return extension.show_search_media_menu(commands[0].lower())
            else:
                # Get search query
                search_query = ''
                for command in commands[1:]:
                    search_query += command + ' '
                
                # Show media type search results
                return extension.show_search_media(commands[0].lower(), search_query)

        elif re.match(r'^-(\d)+$( )?(\w+)?$', commands[0], re.IGNORECASE): # Match for id number lookups
            try:
                language = commands[1]
            except:
                language = None
            media_id = commands[0].replace('-', '')
            return extension.show_media(media_id, language)

        elif re.match(r'^-(\d)+ s(0)?[1-9]+((0)?)+e(0)?[1-9]+((0)?)+( )?(\w+)?$', argument, re.IGNORECASE):
            try:
                language = commands[2]
            except:
                language = None
            media_id = commands[0].replace('-', '')
            return extension.show_episode(media_id, commands[1], language)
        
        # User is still specifying the episode number
        elif re.match(r'^-(\d)+$', commands[0]):
            return RenderResultListAction(screens.render_episode_not_specified())


class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):
        _preferences = event.preferences

        import preferences
        preferences.PREF_KEYWORD = _preferences['keyword']

        from languages import LANGUAGES
        preferences.PREF_MAIN_LANGUAGE = LANGUAGES[_preferences['main_language']]

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        _id = event.id
        new_value = event.new_value
        #old_value = event.old_value

        import preferences
        if _id == 'keyword':
            preferences.PREF_KEYWORD = new_value
        elif _id == 'main_language':
            from languages import LANGUAGES
            preferences.PREF_MAIN_LANGUAGE = LANGUAGES[new_value]

class ItemEnterEventListener(EventListener):
    
    def on_event(self, event, extension):
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('Notify', '0.7')
        from gi.repository import Notify
        Notify.init('Ulauncher-OpenSubtitles')
        data = event.get_data()
        
        # If it's a 'download' type
        try:
            import srt
            url = data['download']['url']
            download_id = data['download']['download_id']
            try:
                srt.download(url, download_id)
                Notify.Notification.new("OpenSubtitles", 'Subtitles downloaded!', 'images/opensubtitles.png').show()
            except:
                Notify.Notification.new("OpenSubtitles", 'Error downloading subtitles!', 'images/not_found.png').show()
        except:
            # Do other feature
            pass

if __name__ == '__main__':
    OpenSubtitlesExtension().run()