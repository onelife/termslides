# -*- coding: utf-8 -*-

from asciimatics.effects import Effect, Matrix
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from string import whitespace


class Typing(Effect):
    """
    Special effect that simulate typewriter to print the specified text (from a
    Renderer) at the required location.
    """

    def __init__(self, screen, renderer, y, x=None, colour=7, attr=0, bg=0,
                 clear=False, transparent=True, step=1, speed=2, **kwargs):
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
        if self._go and (self._current < self._count) and \
           (frame_no - self._last_frame) >= self._rate:
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

    def __init__(self, screen, duration=30, is_ending=False, next_fn=False, **kwargs):
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
            if isinstance(event, KeyboardEvent) and event.key_code in \
               [ord(' '), Screen.KEY_RIGHT]:
                self._go = True
                return None
        return event
