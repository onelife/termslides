# -*- coding: utf-8 -*-

from asciimatics.constants import (
    COLOUR_BLACK, COLOUR_RED, COLOUR_GREEN, COLOUR_YELLOW,
    COLOUR_BLUE, COLOUR_MAGENTA, COLOUR_CYAN, COLOUR_WHITE,
    A_BOLD, A_NORMAL, A_REVERSE, A_UNDERLINE,
)
from asciimatics.effects import Cycle, Print, Stars, Snow, Mirage
from asciimatics.renderers import FigletText, Rainbow
from asciimatics.widgets import Frame, Layout, Widget, ListBox, TextBox, PopUpDialog
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.exceptions import NextScene, StopApplication

from termslides.effects import Typing, ScrollSlide, MatrixSlide
from termslides.renderers import NormalText, UMLText, TableText


_type_map = {
    'figlet': FigletText,
    'text': NormalText,
    'uml': UMLText,
    'table': TableText,
    None: None
}

_required_param_map = {
    'figlet': set(['text', 'font']),
    'text': set(['text']),
    'uml': set(['text']),
    'table': set(['data']),
}

_param_map = {
    'figlet': set(['text', 'font']),
    'text': set(['text']),
    'uml': set(['text']),
    'table': set(['data', 'hasHeader', 'tablefmt', 'numalign', 'floatfmt']),
}

_colour_map = {
    'black': COLOUR_BLACK,
    'red': COLOUR_RED,
    'green': COLOUR_GREEN,
    'yellow': COLOUR_YELLOW,
    'blue': COLOUR_BLUE,
    'magenta': COLOUR_MAGENTA,
    'cyan': COLOUR_CYAN,
    'white': COLOUR_WHITE,
    'rainbow': 'rainbow',
    'cycle': 'cycle',
}

_attr_map = {
    'bold': A_BOLD,
    'normal': A_NORMAL,
    'reverse': A_REVERSE,
    'underline': A_UNDERLINE,
}

_valid_start = [None, 'scroll']
_valid_end = [None, 'scroll', 'matrix']


class InvalidParameter(Exception):
    pass


def _get_effects(screen, content, start_animation=None, end_animation=None, next_fn=None):
    effects = []
    for item in content:
        # get type and required param
        type_ = item.get('type', None)
        content = item.get('content', None)
        if type_ is None or content is None:
            raise InvalidParameter(str(item.items()))

        # check required param
        if type_ in ['figlet', 'text', 'uml']:
            item['text'] = content
        elif type_ in ['table']:
            item['data'] = content
        if _required_param_map[type_].intersection(item.keys()) != _required_param_map[type_]:
            raise InvalidParameter(
                f'{type_}: require {_required_param_map[type_].difference(item.keys())}')

        # optional param
        # - afterStart: default is False
        # - animation: default if None
        # - colour: default is white
        # - y: default is middle of the screen
        afterStart = item.get('afterStart', False)
        animation = item.get('animation', None)
        colour = _colour_map[item.get('colour', 'white')]
        y = int(item.get('y', screen.height / 2))

        # check conflict
        if colour == 'cycle' and animation in ['typing', 'mirage']:
            raise InvalidParameter(
                f"'{colour}' and '{animation}' can't be used together")

        # get render
        render = _type_map[type_](**{k: item[k] for k in _param_map[type_] if k in item})

        # modify "start_frame" and "y"
        start_frame = 0
        if start_animation == 'scroll':
            y += screen.height
            if afterStart:
                start_frame = screen.height

        # get effect
        if colour == 'cycle':
            effect = Cycle(screen, render, y, start_frame=start_frame)
        else:
            if colour == 'rainbow':
                render = Rainbow(screen, render)
                colour = COLOUR_WHITE
            # optional param
            # - x: default is middle of the screen
            # - attr: default is None
            # - bg: default is black
            x = item.get('x', None)
            if x is not None:
                x = int(x)
            attr = _attr_map[item.get('attr', 'normal')]
            bg = _colour_map[item.get('bg', 'black')]

            if animation == 'mirage':
                duration = 30
                effect = Mirage(screen, render, y, colour,
                                start_frame=start_frame,
                                stop_frame=start_frame + duration)
                effects.append(effect)
                effect = Print(screen, render, y, x, colour, attr, bg,
                               start_frame=start_frame + duration,
                               stop_frame=start_frame + duration + 10)
            else:
                if animation == 'typing':
                    effect_ = Typing
                else:
                    effect_ = Print
                effect = effect_(screen, render, y, x, colour,
                                 attr, bg, start_frame=start_frame)
        effects.append(effect)

    # starting / ending animation
    if start_animation == 'scroll':
        effects.append(ScrollSlide(screen, start_frame=0))
    elif start_animation == 'matrix':
        effects.append(MatrixSlide(screen, start_frame=0))
    if end_animation:
        last_frame = max([effect.stop_frame for effect in effects])
        if end_animation == 'scroll':
            effects.append(ScrollSlide(screen, is_ending=True, next_fn=next_fn, start_frame=last_frame))
        elif end_animation == 'matrix':
            effects.append(MatrixSlide(screen, is_ending=True, next_fn=next_fn, start_frame=last_frame))

    return effects


class InputHandler(Frame):
    """
    Invisible frame to handle user input.
    """

    def __init__(self, screen, list_view):
        super(InputHandler, self).__init__(
            screen, 1, 1,
            x=screen.width - 1, y=0,
            has_border=False, can_scroll=False)
        self._screen = screen
        self._list_view = list_view
        self.fix()
        self.set_theme('monochrome')

    def process_event(self, event):
        super(InputHandler, self).process_event(event)
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('\r'), ord('\n'), Screen.KEY_ESCAPE]:
                self._list_view.index = self._screen._scene_index - 1
                raise NextScene('__slides_list__')
            elif event.key_code in [ord(' '), Screen.KEY_RIGHT]:
                if self._screen._scene_index >= len(self._screen._scenes) - 1:
                    return None
                raise NextScene()
            elif event.key_code in [Screen.KEY_LEFT]:
                if self._screen._scene_index <= 1:
                    return None
                raise NextScene(self._screen._scenes[self._screen._scene_index - 1].name)

        return event


class TitleView(Frame):
    """
    A frame to show slide name as title.
    """

    def __init__(self, screen):
        super(TitleView, self).__init__(
            screen,
            screen.height - screen.height // 5,
            screen.width - screen.width // 6 + 1,
            x=screen.width // 6 - 1, y=0,
            can_scroll=False)
        self.fix()
        self.set_theme('monochrome')


class SlideView(Frame):
    """
    A frame to show slides.
    """

    def __init__(self, screen, slides):
        super(SlideView, self).__init__(
            screen,
            screen.height - screen.height // 5 - 2,
            screen.width - screen.width // 6 - 1,
            x=screen.width // 6, y=1,
            has_border=False, can_scroll=False)
        self.slides = slides
        self.show_slide()
        self.fix()
        self.set_theme('monochrome')

    def _update(self, frame_no):
        # disable "_clear" to avoid flicker
        _clear = self._clear
        self._clear = lambda: None
        super(SlideView, self)._update(frame_no)
        self._clear = _clear

    def process_event(self, event):
        super(SlideView, self).process_event(event)
        # if event is not None:
        for effect in self._effects:
            event = effect.process_event(event)
            if event is None:
                break
        return event

    def show_slide(self, name=None):
        if name not in self.slides:
            name = list(self.slides.keys())[0]
        slide = self.slides[name]

        # clear current effects
        self._effects = []
        self._clear()
        self._canvas.scroll_to(0)

        # get slide content
        content = slide.get('content', None)
        if content is None:
            raise InvalidParameter(f"Page {name} no 'content'")
        # get starting / ending animation
        start = slide.get('startAnimation', None)
        if start not in _valid_start:
            raise InvalidParameter(f'Invalid starting animation: {start}')
        end = slide.get('endAnimation', None)
        if end not in _valid_end:
            raise InvalidParameter(f'Invalid ending animation: {end}')
        # get slide effects
        effects = _get_effects(
            self._canvas, content, start, end, lambda: self.show_slide(name))
        # get slide animation
        stars = slide.get('stars', None)
        if stars:
            effects.insert(0, Stars(self._canvas, stars))
        snow = slide.get('snow', False)
        if snow:
            effects.insert(0, Snow(self._canvas))

        # add effects
        for effect in effects:
            effect.reset()
            self.add_effect(effect)


class NoteView(Frame):
    """
    A frame to show notes as text box.
    """

    def __init__(self, screen, slides):
        super(NoteView, self).__init__(
            screen, screen.height // 5 + 1, screen.width - screen.width // 6 + 1,
            x=screen.width // 6 - 1, y=screen.height - screen.height // 5 - 1,
            can_scroll=True,
            title="Notes")
        self._notes = {k: v['notes'] for k, v in slides.items()}
        self._notes_view = TextBox(
            Widget.FILL_FRAME,
            as_string=True, line_wrap=True,
            on_change=None, readonly=True)
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._notes_view)
        self.fix()
        self.set_theme('monochrome')

    def show_notes(self, name):
        self._notes_view.value = self._notes[name]


class ListView(Frame):
    """
    A list frame to show slides list.
    """

    def __init__(self, screen, slides, slide_view, notes_view, title_view):
        super(ListView, self).__init__(
            screen, screen.height, screen.width // 6,
            x=0,
            on_load=self._reload_list,
            hover_focus=True, can_scroll=False,
            title="Slides List")
        model = [(name, idx) for idx, name in enumerate(slides.keys())]
        self._model = model
        self._index = -1
        self._slide_view = slide_view
        self._notes_view = notes_view
        self._title_view = title_view
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model,
            name="slides",
            add_scroll_bar=True,
            on_change=self._on_pick,
            on_select=self._on_select)
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        self.fix()
        self.set_theme('monochrome')
        self._on_pick()

    def _on_pick(self):
        if self._list_view.value is None:
            self._list_view.value = 0
        name = self._list_view.options[self._list_view.value][0]
        self._slide_view.show_slide(name)
        self._notes_view.show_notes(name)
        self._title_view.title = name

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model
        self._list_view.value = 0 if new_value is None else new_value

    def _on_select(self):
        # self.save()
        if self._list_view.value is None:
            self._list_view.value = 0
        name = self._list_view.options[self._list_view.value][0]
        raise NextScene(name)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if value < 0:
            self._index = 0
        elif value >= len(self._model):
            self._index = len(self._model) - 1
        else:
            self._index = value

    def reset(self):
        super(ListView, self).reset()
        self._list_view.value = self._index
        if self._index == 1000:
            raise ValueError(self._index)

    def process_event(self, event):
        super(ListView, self).process_event(event)
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), Screen.KEY_ESCAPE]:
                self._quit()
                return None
        return event

    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(
                self._screen, "Exit TermSlides?", ["Yes", "No"],
                on_close=self._quit_on_yes))

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            raise StopApplication("User requested exit")
