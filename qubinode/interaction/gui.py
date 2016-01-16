from kivy.app import App
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from interaction import Interaction
from qubinode.settings import app


class GraphicalInteraction(Interaction, App):
    def __init__(self, config):
        Interaction.__init__(self, config=config)
        App.__init__(self)

    def setup(self):
        self.run()

    def build(self):
        self.title = 'qubinode v{}'.format(app.__version__)
        return SelectReleaseLayout()


class SelectReleaseBox(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectReleaseBox, self).__init__(**kwargs)

        self.size_hint_y = None
        self.height = 150

        with self.canvas.before:
            Color(0.2, 0.3, 0.4, 1)  # green; colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        image = Image(source='images/test.png')
        image.size_hint_x = None
        image.width = 150
        self.add_widget(image)

        details = BoxLayout()
        details.size_hint_x = 2
        details.orientation = 'vertical'
        details.add_widget(Label(text='Bitcoin Unlimited', font_size='32sp'))
        details.add_widget(Label(text_size=(500, None), text='The Bitcoin Unlimited client is not a competitive block scaling proposal like BIP-101, BIP-102, etc. Instead it tracks consensus. This means that it tracks the blockchain that the hash power majority follows, irrespective of blocksize, and signals its ability to accept larger blocks via protocol and block versioning fields.'))
        self.add_widget(details)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SelectReleaseLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectReleaseLayout, self).__init__(**kwargs)
        self.padding = 10
        self.orientation = 'vertical'
        self.add_widget(SelectReleaseBox())
