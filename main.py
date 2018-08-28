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
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener()) # Set preferences to inner members
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
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

    """
    def show_example(self):
        search_result = self._api.get_episode(4145054, 1, 3)
        items = []

        for item in search_result[:5]:
            download_info = {
                'url': item.url,
                'id': item.download_id
            }
            from languages import LANGUAGES
            items.append(ExtensionResultItem(icon = 'images/languages/%s.svg' % LANGUAGES[item.language],
                                         name = '%s - %s [%s]' % (item.uploader, item.uploader_badge, item.language),
                                         description = '%s' % item.video_source_name,
                                         highlightable = True,
                                         on_enter = ExtensionCustomAction(download_info)))
        return RenderResultListAction(items)
    """

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        argument = event.get_argument()
        if argument is None:
            return extension.show_menu()
        
        commands = argument.split()

        # Search for media type
        if commands[0] == 'm' or commands[0] == 'tv':

            # There's nothing to search yet
            if len( commands ) is 1:
                
                # Show media type search menu 
                return extension.show_search_media_menu(commands[0])
            else:
                # Get search query
                search_query = ''
                for command in commands[1:]:
                    search_query += command + ' '
                
                # Show media type search results
                return extension.show_search_media(commands[0], search_query)


class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):
        _preferences = event.preferences

        import preferences
        preferences.PREF_KEYWORD = _preferences['keyword']
        logger.info("Set 'keyword' preference as: %s" % preferences.PREF_KEYWORD)

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        _id = event.id
        new_value = event.new_value
        #old_value = event.old_value

        import preferences
        if _id == 'keyword':
            preferences.PREF_KEYWORD = new_value
            logger.info("Update 'keyword' preference to: %s" % preferences.PREF_KEYWORD)


class ItemEnterEventListener(EventListener):
    
    def on_event(self, event, extension):
        data = event.get_data()
        
        import srt
        srt.download(data['url'], data['id'])

if __name__ == '__main__':
    OpenSubtitlesExtension().run()