from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty

app = App.get_running_app()


class SpeakerDetails(Factory.ScrollGrid):

    speaker = ObjectProperty(None)

    Builder.load_string('''
<SpeakerDetails>
    AsyncImage:
        source: root.speaker['photo']
        allow_stretch: True
        size_hint_y: None
        height: dp(150)
        mipmap: True
    BackLabel
        text: root.speaker['name']
    BackLabel
        text: root.speaker['info']
        ''')

class ScreenTalks(Screen):
    '''
    Screen to display the talk schedule as per talks.json generated by
    pydelhiconf.network every time the app is started. A default
    talk schedule is provided.

    Screen looks like:

    -----------------------------------------
   |              ------------               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              ------------               |
   |              Speaker name               |
   |                                         |
   |About talk                               |
   |                                         |
   |About speaker                            |
   |Social links                             |
   |                                         | 
    -----------------------------------------

    '''

    talkid = StringProperty('')

    Builder.load_string('''
<ScreenTalks>
    spacing: dp(9)
    name: 'ScreenTalks'
    ScrollView
        ScrollGrid
            id: container
            BackLabel:
                id: talk_title
            BackLabel:
                id: talk_desc
    
<ImBut@ButtonBehavior+Image>
    text_size: self.size
    size_hint_y: None
    mipmap: True
    height: dp(45)
        ''')
    def on_pre_enter(self):
        container = self.ids.container
        container.opacity = 0

    def on_enter(self, onsuccess=False):
        container = self.ids.container
        if len(container.children) > 2:
                container.remove_widget(container.children[0])
        from network import get_data
        talks = get_data('tracks', onsuccess=False)
        gl = None
        if not talks:
            return
        talk_info = talks['0.0.1'][0][self.talkid]
        self.ids.talk_title.text = talk_info['title']
        self.ids.talk_desc.text = talk_info['description']
        if 'speaker' in talk_info.keys():
            speaker_class = SpeakerDetails(speaker=talk_info['speaker'])
            speaker=talk_info['speaker']
            if 'social' in speaker:
                speaker_social = speaker['social'][0]
                social_len = len(speaker_social)
                gl = GridLayout(cols=social_len,
                            size_hint_y=None,
                            padding='2dp',
                            spacing='2dp')
                import webbrowser
                for social_acc, social_link in speaker_social.items():
                    imbt = Factory.ImBut()
                    imbt.source = 'atlas://data/default/' + social_acc.lower()
                    imbt.on_release = lambda *x: webbrowser.open(social_link)
                    gl.add_widget(imbt)
            if gl is not None:
                speaker_class.add_widget(gl)
            self.ids.container.add_widget(speaker_class)
            Factory.Animation(opacity=1, d=.5).start(container)
      