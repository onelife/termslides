# -*- coding: utf-8 -*-

import sys

import yaml
from asciimatics.exceptions import ResizeScreenError
from asciimatics.effects import Stars, Snow
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from click import group, argument

from termslides.widgets import (
    InvalidParameter, InputHandler, TitleView, SlideView, NoteView, ListView,
    _get_effects, _valid_start, _valid_end
)

__all__ = ['termslides']


@group()
def cli():
    pass


@cli.command()
@argument('file')
def termslides(file):
    with open(file, 'r') as stream:
        slides = yaml.full_load(stream)

    def slides_show(screen, scene):
        scenes = []
        screen.set_title(slides.pop('title', 'TermSlides'))

        # list view
        slide_view = SlideView(screen, slides)
        notes_view = NoteView(screen, slides)
        title_view = TitleView(screen)
        list_view = ListView(screen, slides, slide_view, notes_view, title_view)
        scenes.append(Scene(
            [title_view, notes_view, slide_view, list_view], -1, name="__slides_list__"))

        # slides
        for name, slide in slides.items():
            # get slide content
            content = slide.get('content', None)
            if content is None:
                raise InvalidParameter(f"Page {name} no 'content'")
            # get slide duration
            duration = slide.get('duration', -1)
            # get starting / ending animation
            start = slide.get('startAnimation', None)
            if start not in _valid_start:
                raise InvalidParameter(f'Invalid starting animation: {start}')
            end = slide.get('endAnimation', None)
            if end not in _valid_end:
                raise InvalidParameter(f'Invalid ending animation: {end}')
            # get slide effects
            effects = _get_effects(screen, content, start, end)
            # get slide animation
            stars = slide.get('stars', None)
            if stars:
                effects.insert(0, Stars(screen, stars))
            snow = slide.get('snow', False)
            if snow:
                effects.insert(0, Snow(screen))
            # input handler
            effects.insert(0, InputHandler(screen, list_view))
            # add to scenes
            scenes.append(Scene(effects, duration, name=name))

        screen.play(scenes, stop_on_resize=True, start_scene=scene)

    last_scene = None
    while True:
        try:
            Screen.wrapper(slides_show, catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene


if __name__ == '__main__':
    cli()
