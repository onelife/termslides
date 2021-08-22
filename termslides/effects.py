# -*- coding: utf-8 -*-

from random import random

from asciimatics.effects import Effect, Matrix, Wipe
from asciimatics.particles import Particle, DropEmitter, DropScreen, ShotEmitter, ShootScreen
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from string import whitespace


class Mirage(Effect):
    """
    Special effect to make bits of the specified text appear over time.  This
    text is automatically centred on the screen.
    """

    def __init__(self, screen, renderer, y, x, colour, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param renderer: The renderer to be displayed.
        :param y: The line (y coordinate) for the start of the text.
        :param colour: The colour attribute to use for the text.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(Mirage, self).__init__(screen, **kwargs)
        self._renderer = renderer
        self._y = y
        self._x = x
        self._colour = colour
        self._count = 0

    def reset(self):
        self._count = 0

    def _update(self, frame_no):
        if frame_no % 2 == 0:
            return

        y = self._y
        image, colours = self._renderer.rendered_text
        for i, line in enumerate(image):
            if self._screen.is_visible(0, y):
                if self._x is None:
                    x = (self._screen.width - len(line)) // 2
                else:
                    x = self._x
                for j, c in enumerate(line):
                    if c != " " and random() > 0.85:
                        if colours[i][j][0] is not None:
                            self._screen.print_at(c, x, y,
                                                  colours[i][j][0],
                                                  colours[i][j][1])
                        else:
                            self._screen.print_at(c, x, y, self._colour)
                    x += 1
            y += 1

    @property
    def stop_frame(self):
        return self._stop_frame


class Typing(Effect):
    """
    Special effect that simulate typewriter to print the specified text (from a
    Renderer) at the required location.
    """

    def __init__(self, screen, renderer, y, x=None, colour=7, attr=0, bg=0,
                 clear=False, transparent=True, step=2, speed=2, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param renderer: The renderer to be printed.
        :param x: The column (x coordinate) for the start of the text.
            If not specified, defaults to centring the text on screen.
        :param y: The line (y coordinate) for the start of the text.
        :param colour: The foreground colour to use for the text.
        :param attr: The colour attribute to use for the text.
        :param bg: The background colour to use for the text.
        :param clear: Whether to clear the text before stopping.
        :param transparent: Whether to print spaces (and so be able to overlay other Effects).
            If False, this will redraw all characters and so replace any Effect underneath it.
        :param step: The number of charaters appearing for each refresh.
        :param speed: The refresh rate in frames between refreshes.

        Note that a speed of 1 will force the Screen to redraw the Effect every frame update, while a value
        of 0 will redraw on demand - i.e. will redraw every time that an update is required by another Effect.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(Typing, self).__init__(screen, **kwargs)
        self._renderer = renderer
        self._transparent = transparent
        self._y = y
        self._x = ((self._screen.width - renderer.max_width) // 2 if x is None
                   else x)
        self._colour = colour
        self._attr = attr
        self._bg = bg
        self._clear = clear
        self._step = step
        self._speed = speed
        self._frame_no = 0
        self._frame_cnt = (sum([len(line) for line in self._renderer.rendered_text[0]]
                               ) + self._step - 1) // self._step * self._speed
        self._image_idx = 0
        self._line_idx = 0

    def reset(self):
        self._image_idx = 0
        self._line_idx = 0

    def _update(self, frame_no):
        self._frame_no = frame_no
        if self._clear and (frame_no == self._stop_frame - 1) or (self._delete_count == 1):
            for i in range(0, self._renderer.max_height):
                self._screen.print_at(" " * self._renderer.max_width,
                                      self._x,
                                      self._y + i,
                                      bg=self._bg)
        elif (self._speed == 0) or (frame_no % self._speed == 0):
            image, colours = self._renderer.rendered_text
            # goto next line
            while (self._image_idx < len(image)) and (self._line_idx >= len(image[self._image_idx])):
                self._line_idx = 0
                self._image_idx += 1
            if self._image_idx < len(image):
                # goto next position
                while (self._line_idx < len(image[self._image_idx])) and \
                        (image[self._image_idx][self._line_idx] in whitespace):
                    self._line_idx += 1
                self._screen.paint(
                    image[self._image_idx][: self._line_idx + self._step + 1],
                    self._x, self._y + self._image_idx,
                    self._colour,
                    attr=self._attr,
                    bg=self._bg,
                    transparent=self._transparent,
                    colour_map=colours[self._image_idx][: self._line_idx + self._step + 1])
                self._line_idx += self._step

    @property
    def stop_frame(self):
        if self._stop_frame != 0:
            return self._stop_frame
        return self._start_frame + self._frame_cnt

    @property
    def frame_update_count(self):
        # Only demand update for next update frame.
        return self._speed - (self._frame_no % self._speed) if self._speed > 0 else 1


class ScrollSlide(Effect):
    """
    Special effect to scroll the slide up at a required rate.
    """

    def __init__(self, screen, rate=1, is_ending=False, next_fn=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param rate: How many frames to wait between scrolling the screen.
        :param is_ending: At the starting or ending of a show.
        :param next_fn: If at the ending, what to do after the last frame.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(ScrollSlide, self).__init__(screen, **kwargs)
        self._rate = rate
        self._isEnding = is_ending
        self._next_fn = next_fn
        self._count = screen.height // self._rate
        self._current = 0
        self._last_frame = 0
        self._go = not self._isEnding

    def reset(self):
        self._current = 0
        self._last_frame = 0
        self._go = not self._isEnding

    def _update(self, frame_no):
        if self._isEnding and (self._current >= self._count):
            self.reset()
            if self._next_fn:
                self._next_fn()
            else:
                raise NextScene()
        if self._go and (self._current < self._count) and (frame_no - self._last_frame) >= self._rate:
            self._screen.scroll(self._rate)
            self._current += 1
            self._last_frame = frame_no

    @property
    def stop_frame(self):
        return self._start_frame + self._count * self._rate

    def process_event(self, event):
        """
        Process any input event.

        :param event: The event that was triggered.
        :returns: None if the Effect processed the event, else the original
                  event.
        """
        if not self._go and not self._current:
            if isinstance(event, KeyboardEvent) and event.key_code in \
               [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event


class MatrixSlide(Matrix):
    """
    Matrix-like effect.
    """

    def __init__(self, screen, duration=100, is_ending=False, next_fn=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param duration: How many frames to show.
        :param is_ending: At the starting or ending of a show.
        :param next_fn: If at the ending, what to do after the last frame.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(MatrixSlide, self).__init__(screen, **kwargs)
        self._isEnding = is_ending
        self._next_fn = next_fn
        self._count = duration
        self._current = 0
        self._go = not self._isEnding

    def reset(self):
        super(MatrixSlide, self).reset()
        self._current = 0
        self._go = not self._isEnding

    def _update(self, frame_no):
        if self._isEnding and (self._current >= self._count):
            self.reset()
            if self._next_fn:
                self._next_fn()
            else:
                raise NextScene()
        if self._go and (self._current < self._count):
            super(MatrixSlide, self)._update(frame_no)
            self._current += 1

    @property
    def stop_frame(self):
        if self._stop_frame:
            return self._stop_frame
        return self._start_frame + self._count

    def process_event(self, event):
        """
        Process any input event.

        :param event: The event that was triggered.
        :returns: None if the Effect processed the event, else the original
                  event.
        """
        if not self._go and not self._current:
            if isinstance(event, KeyboardEvent) and event.key_code in [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event


class WipeSlide(Wipe):
    """
    Wipe the screen down from top to bottom.
    """

    def __init__(self, screen, next_fn=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param duration: How many frames to show.
        :param next_fn: If at the ending, what to do after the last frame.

        """
        super(WipeSlide, self).__init__(screen, bg=0, **kwargs)
        self._isEnding = True
        self._next_fn = next_fn
        self._count = screen.height * 2
        self._current = 0
        self._go = not self._isEnding

    def reset(self):
        super(WipeSlide, self).reset()
        self._y += self._screen.height
        self._current = 0
        self._go = not self._isEnding

    def _update(self, frame_no):
        if self._isEnding and (self._current >= self._count):
            self.reset()
            if self._next_fn:
                self._next_fn()
            else:
                raise NextScene()
        if self._go and (self._current < self._count):
            super(WipeSlide, self)._update(frame_no)
            self._current += 1

    @property
    def stop_frame(self):
        if self._stop_frame:
            return self._stop_frame
        return self._start_frame + self._count

    def process_event(self, event):
        """
        Process any input event.

        :param event: The event that was triggered.
        :returns: None if the Effect processed the event, else the original
                  event.
        """
        if not self._go and not self._current:
            if isinstance(event, KeyboardEvent) and event.key_code in [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event


def patch_drop_next_particle(self):
    from random import randint
    # Find all particles on the Screen when we create our first particle.
    if self._particles is None:
        self._particles = []
        for x in range(self._screen.width):
            for y in range(self._screen.height):
                y += self._screen._start_line
                ch, fg, attr, bg = self._screen.get_from(x, y)
                if ch != 32:
                    self._particles.insert(randint(0, len(self._particles)), (x, y, ch, fg, attr, bg))

    # Stop now if there were no more particles to move.
    if len(self._particles) == 0:
        return None

    # We got here, so there must still be some screen estate to move.
    x, y, ch, fg, attr, bg = self._particles.pop()
    return Particle(chr(ch), x, y, 0.0, 0.0, [(fg, attr, bg)], self._life_time, self._move)


DropEmitter._next_particle = patch_drop_next_particle


def patch_shoot_next_particle(self):
    from math import sqrt
    # Find all particles on the Screen when we create our first particle
    # and sort by distance from the origin.
    if self._particles is None:
        self._particles = []
        for x in range(self._screen.width):
            for y in range(self._screen.height):
                y += self._screen._start_line
                ch, fg, attr, bg = self._screen.get_from(x, y)
                if ch != 32:
                    self._particles.append((x, y, ch, fg, attr, bg))
        self._particles = sorted(self._particles, key=self._sort, reverse=True)

    # Stop now if there were no more particles to move.
    if len(self._particles) == 0:
        return None

    # We got here, so there must still be some screen estate to move.
    x, y, ch, fg, attr, bg = self._particles.pop()
    r = min(10,
            max(0.001,
                sqrt(((x - self._x) ** 2) + ((y - self._y) ** 2))))
    return Particle(chr(ch), x, y, (x - self._x) * 40.0 / r ** 2, (y - self._y) * 20.0 / r ** 2,
                    [(fg, attr, bg)], self._life_time, self._move)


ShotEmitter._next_particle = patch_shoot_next_particle


class DropSlide(DropScreen):
    """
    Drop all the text on the screen as if it was subject to gravity.
    """

    def __init__(self, screen, duration=100, next_fn=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param duration: How many frames to show.
        :param next_fn: If at the ending, what to do after the last frame.
        """
        self._isEnding = True
        self._next_fn = next_fn
        self._count = duration
        self._current = 0
        self._go = not self._isEnding
        super(DropSlide, self).__init__(screen, duration, **kwargs)

    def reset(self):
        self._active_systems = []
        self._active_systems.append(DropEmitter(self._screen, self._life_time))
        self._current = 0
        self._go = not self._isEnding

    def _update(self, frame_no):
        if self._isEnding and (self._current >= self._count):
            self.reset()
            if self._next_fn:
                self._next_fn()
            else:
                raise NextScene()
        if self._go and (self._current < self._count):
            super(DropSlide, self)._update(frame_no)
            self._current += 1

    @property
    def stop_frame(self):
        if self._stop_frame:
            return self._stop_frame
        return self._start_frame + self._count

    def process_event(self, event):
        """
        Process any input event.

        :param event: The event that was triggered.
        :returns: None if the Effect processed the event, else the original
                  event.
        """
        if not self._go and not self._current:
            if isinstance(event, KeyboardEvent) and event.key_code in [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event


class ShootSlide(ShootScreen):
    """
    Shoot the screen out like a massive gunshot.
    """

    def __init__(self, screen, y_offset=0, duration=60, next_fn=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param duration: How many frames to show.
        :param next_fn: If at the ending, what to do after the last frame.
        """
        self._isEnding = True
        self._next_fn = next_fn
        self._count = duration
        self._current = 0
        self._go = not self._isEnding
        super(ShootSlide, self).__init__(screen, screen.width // 2, y_offset + screen.height // 2, duration, **kwargs)

    def reset(self):
        self._active_systems = []
        self._active_systems.append(ShotEmitter(self._screen, self._x, self._y, self._life_time))
        self._current = 0
        self._go = not self._isEnding

    def _update(self, frame_no):
        if self._isEnding and (self._current >= self._count):
            self.reset()
            if self._next_fn:
                self._next_fn()
            else:
                raise NextScene()
        if self._go and (self._current < self._count):
            super(ShootSlide, self)._update(frame_no)
            self._current += 1

    @property
    def stop_frame(self):
        if self._stop_frame:
            return self._stop_frame
        return self._start_frame + self._count

    def process_event(self, event):
        """
        Process any input event.

        :param event: The event that was triggered.
        :returns: None if the Effect processed the event, else the original
                  event.
        """
        if not self._go and not self._current:
            if isinstance(event, KeyboardEvent) and event.key_code in [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event
