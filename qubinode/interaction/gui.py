from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from interaction import Interaction
from qubinode.settings import app


class GraphicalInteraction(Interaction, App):
    def __init__(self, cfg):
        Interaction.__init__(self, cfg=cfg)
        App.__init__(self)

    def setup(self):
        self.run()

    def build(self):
        self.title = 'qubinode v{}'.format(app.__version__)
        return SelectVariantLayout(self.cfg)


class SelectVariantBox(BoxLayout):
    def __init__(self, variant, **kwargs):
        super(SelectVariantBox, self).__init__(**kwargs)

        self.variant = variant
        self.size_hint_y = None
        self.height = 150

        self.set_background_colour()
        self.add_logo()
        self.add_description()

    def add_description(self):
        details = BoxLayout()
        details.size_hint_x = 2
        details.orientation = 'vertical'
        details.add_widget(Label(text=self.variant['title'], font_size='32sp'))
        details.add_widget(Label(
                text_size=(500, None),
                text=self.variant.get('description', ''),
        ))
        self.add_widget(details)

    def add_logo(self):
        source = self.variant.get('logo', 'test.png')
        image = Image(source='images/{}'.format(source))
        image.size_hint_x = None
        image.width = 150
        self.add_widget(image)

    def set_background_colour(self):
        with self.canvas.before:
            Color(0.2, 0.3, 0.4, 1)  # green; colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SelectVariantLayout(BoxLayout):
    def __init__(self, cfg, **kwargs):
        super(SelectVariantLayout, self).__init__(**kwargs)
        self.cfg = cfg
        self.padding = 10
        self.orientation = 'vertical'
        for code, variant in self.cfg.settings['variants'].iteritems():
            self.add_widget(SelectVariantBox(variant))
