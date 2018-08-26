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

class OpenSubtitlesExtension(Extension):

    def __init__(self):
        super(OpenSubtitlesExtension, self).__init__()

        # Subscribe to events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        #self.subscribe(PreferencesEvent, PreferencesEventListener()) # Set preferences to inner members
        #self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        #self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def show_example(self):
        items = []
        items.append(ExtensionResultItem(icon = 'images/tv_show.png',
                                         name = 'Westworld',
                                         description = 'An AI theme park',
                                         highlightable = True,
                                         on_enter = DoNothingAction()))
        return RenderResultListAction(items)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        argument = event.get_argument()
        return extension.show_example()

class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):
        return

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        return

class ItemEnterEventListener(EventListener):
    
    def on_event(self, event, extension):
        return

if __name__ == '__main__':
    OpenSubtitlesExtension().run()