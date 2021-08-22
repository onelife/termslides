# -*- coding: utf-8 -*-

import sys
from types import MethodType

import yaml
from asciimatics.exceptions import NextScene, ResizeScreenError, StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from click import group, argument

from termslides.widgets import (
    InvalidParameter, InputHandler, TitleView, SlideView, NoteView, ListView,
    _get_effects, _valid_start, _valid_end, _valid_page
)

__all__ = ['termslides']


def patch_draw_next_frame(self, repeat=True):
    """
    Draw the next frame in the currently configured Scenes. You must call
    :py:meth:`.set_scenes` before using this for the first time.

    :param repeat: Whether to repeat the Scenes once it has reached the end.
        Defaults to True.

    :raises StopApplication: if the application should be terminated.
    """
    scene = self._scenes[self._scene_index]
    try:
        # Check for an event now and remember for refresh reasons.
        event = self.get_event()
        got_event = event is not None

        # Now process all the input events
        while event is not None:
            event = scene.process_event(event)
            if event is not None and self._unhandled_input is not None:
                self._unhandled_input(event)
            event = self.get_event()

        # Only bother with a refresh if there was an event to process or
        # we have to refresh due to the refresh limit required for an
        # Effect.
        self._frame += 1
        self._idle_frame_count -= 1
        if got_event or self._idle_frame_count <= 0 or self._forced_update:
            self._forced_update = False
            self._idle_frame_count = 1000000
            for effect in scene.effects:
                # Update the effect and delete if needed.
                effect.update(self._frame)
                if effect.delete_count is not None:
                    effect.delete_count -= 1
                    if effect.delete_count <= 0:
                        scene.remove_effect(effect)

                # Sort out when we next _need_ to do a refresh.
                if effect.frame_update_count > 0:
                    self._idle_frame_count = min(self._idle_frame_count,
                                                 effect.frame_update_count)
            self.refresh()

        if 0 < scene.duration <= self._frame:
            raise NextScene()
    except NextScene as e:
        # Tidy up the current scene.
        scene.exit()

        # Find the specified next Scene
        if e.name is None:
            # Just allow next iteration of loop
            self._scene_index += 1
            if self._scene_index >= len(self._scenes):
                if repeat:
                    self._scene_index = 0
                else:
                    raise StopApplication("Repeat disabled")
        else:
            # Find the required scene.
            for i, scene in enumerate(self._scenes):
                if scene.name == e.name:
                    self._scene_index = i
                    break
            else:
                raise RuntimeError(
                    "Could not find Scene: '{}'".format(e.name))

        # Reset the screen if needed.
        scene = self._scenes[self._scene_index]
        scene.reset()
        self._frame = 0
        self._idle_frame_count = 0
        if scene.clear:
            self.clear()
        else:
            self._start_line = 0
            self._x = self._y = None
            self._reset()


@group()
def cli():
    pass


@cli.command()
@argument('file')
def termslides(file):
    from tqdm import tqdm

    with open(file, 'r') as stream:
        slides = yaml.full_load(stream)

    def slides_show(screen, scene):
        scenes = []
        screen.set_title(slides.pop('title', 'TermSlides'))
        screen.draw_next_frame = MethodType(patch_draw_next_frame, screen)

        # list view
        slide_view = SlideView(screen, slides)
        notes_view = NoteView(screen, slides)
        title_view = TitleView(screen)
        list_view = ListView(screen, slides, slide_view, notes_view, title_view)
        scenes.append(Scene(
            [title_view, notes_view, slide_view, list_view], -1, name="__slides_list__"))

        # slides
        progress = tqdm(slides.items())
        progress.set_description('Loading slides')
        for name, slide in progress:
            # get slide content
            content = slide.get('content', None)
            if content is None:
                raise InvalidParameter(f"Page {name} no 'content'")
            # get slide duration
            duration = slide.get('duration', -1)
            # get starting / ending / page animation
            start = slide.get('startAnimation', None)
            if start not in _valid_start:
                raise InvalidParameter(f'Invalid starting animation: {start}')
            end = slide.get('endAnimation', None)
            if end not in _valid_end:
                raise InvalidParameter(f'Invalid ending animation: {end}')
            page = slide.get('pageAnimation', None)
            if page not in _valid_page:
                raise InvalidParameter(f'Invalid page animation: {page}')
            # get slide effects
            effects = _get_effects(screen, content, start, end, page)
            # input handler
            effects.insert(0, InputHandler(screen, list_view))
            # add to scenes
            scenes.append(Scene(effects, duration, name=name, clear=(start is None)))

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
