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

    def show_media_hash(self, media_hash, language):
        return RenderResultListAction( screens.render_media(media_hash, language, True))

    def show_episode(self, media_id, episode_designator, language):
        return RenderResultListAction( screens.render_episode(media_id, episode_designator, language) )

    def show_auto(self, query_list):
        VIDEO_FILE_FORMATS = [
            'mkv',
            'flv', 
            'vob', 
            'avi', 
            'wmv', 
            'mov', 
            'mp4', 
            'm4p', 
            'm4v', 
            'mpg', 
            'mp2', 
            'mpeg', 
            'mpe', 
            'mpv', 
            'm2v', 
            'm4v'
        ]

        # Create file regex
        regex = r'\.('

        for video_format in VIDEO_FILE_FORMATS[: len(VIDEO_FILE_FORMATS) - 1]:
            regex += video_format + '|'

        regex += VIDEO_FILE_FORMATS[len(VIDEO_FILE_FORMATS) - 1]
        regex += ')$'
        # Find default file manager
        import subprocess
        out = subprocess.Popen(["locate", "--regex", regex],  
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        file_paths = stdout.splitlines()
        
        import ntpath
        for query in query_list:
            file_paths = list( filter(lambda path: str(query) in ntpath.basename(path).lower(), file_paths))

        return RenderResultListAction( screens.render_auto_results(file_paths) )
        # TODO: Present files to the user, let him pick one, then form a hash and search opensubtitles

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
            
        elif commands[0] == 'auto':
            try:
                queries = commands[1:]
            except:
                queries = []
            return extension.show_auto(queries)

        # Check for video hash
        elif re.match(r'^-hash[^\s]+( )?(\w+)?$', argument, re.IGNORECASE):
            try:
                language = commands[1]
            except:
                language = None
            media_hash = commands[0].replace('-hash', '')
            return extension.show_media_hash(media_hash, language)

        elif re.match(r'^-(\d)+ s(0)?[1-9]+((0)?)+e(0)?[1-9]+((0)?)+( )?(\w+)?$', argument, re.IGNORECASE):
            try:
                language = commands[2]
            except:
                language = None
            media_id = commands[0].replace('-', '')
            return extension.show_episode(media_id, commands[1], language)

        elif re.match(r'^-(\d)+$( )?(\w+)?$', commands[0], re.IGNORECASE): # Match for id number lookups
            try:
                language = commands[1]
            except:
                language = None
            media_id = commands[0].replace('-', '')
            return extension.show_media(media_id, language)
        
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
            # Check for video hash search
            try:
                from video import hash_video
                from preferences import PREF_KEYWORD
                file_path = data['video_hash']
                file_hash = hash_video(file_path)
                return SetUserQueryAction(PREF_KEYWORD + ' -hash' + file_hash)
            except:
                # Do other feature
                pass

if __name__ == '__main__':
    OpenSubtitlesExtension().run()