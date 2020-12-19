# TermSlides
Script your slides in YAML file and show it in terminal.

## Install
`pip install termslides`

## Show Slides
`termslides your_slides.yaml`

## Compose Slides
`termslides` parses YAML file input for slides, which is expected to contain key-value pairs.
Following is an example YAML file with one slide.

```
title: TermSlides Example

Diagram:
  notes: This is an example
  startAnimation: scroll
  endAnimation: matrix
  content:
    - type: text
      content: Hello world!
      animation: typing
      afterStart: true
      colour: rainbow
      y: 2
      x: 2
```

At the top level, `title` is reserved keyword. Its value will be set as the title of currnt terminal window. The rest of key-value pairs are treated as slide name-content pairs.

The slide content is another key-value pairs. `content` is compulsory. The following are optional.
- `notes`: Notes for current slide which is shown in *slides list mode*.
- `duration`: The time in frames before switching to next slide. There are 20 frames per second.
- `startAnimation`: Slide starting animation. `scroll` only.
- `endAnimation`: Slide ending animation. `scroll` or `matrix`.
- `star`: A whole screen effect. The value is number of stars.
- `snow`: A whole screen effect. Set value to `true` to enable.

The value of `content` is yet another key-value pairs. `type` and `content` are compulsory. Following are the available `type`s.
- `text`: Text, the most common type.
  - Other compulsory attributes:
    - None
  - Optional attributes:
    - `animation`: `typing` or `mirage`.
    - `afterStart`: Set value to `true` to start text animation after slide starting animation.
    - `colour`: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `rainbow` or `cycle`. `cycle` doesn't work with `animation`.
    - `y`: Default value is to put the text in the middle of y axis.
    - `x`: Default value is to put the text in the middle of x axis.
    - `attr`: `bold`, `normal`, `reverse` or `underline`
    - `bg`: The background colour. `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan` or `white`.

- `figlet`: [pyfiglet](https://github.com/pwaller/pyfiglet)
  - Other compulsory attributes:
    - `font`: [Font examples](http://www.figlet.org/examples.html)
  - Optional attributes:
    - `animation`: `typing`, `mirage` or `fire`.
    - `afterStart`: Same as `text`.
    - `colour`: Same as `text`.
    - `y`: Same as `text`.
    - `x`: Same as `text`.
    - `attr`: Same as `text`.
    - `bg`: Same as `text`.

- `uml`: Sequence diagram by [PlantUML](https://plantuml.com/sequence-diagram)
  - Other compulsory attributes:
    - None
  - Optional attributes:
    - `animation`: Same as `text`.
    - `afterStart`: Same as `text`.
    - `colour`: Same as `text`.
    - `y`: Same as `text`.
    - `x`: Same as `text`.
    - `attr`: Same as `text`.
    - `bg`: Same as `text`.

- `table`: Table by [python-tabulate](https://github.com/astanin/python-tabulate)
  - Other compulsory attributes:
    - None
  - Optional attributes:
    - `hasHeader`: Set value to `true` to interpret the first row of data as table header.
    - `tablefmt`: [Table format](https://github.com/astanin/python-tabulate#table-format).
    - `numalign`: [Number alignment](https://github.com/astanin/python-tabulate#column-alignment).
    - `floatfmt`: [Number formating](https://github.com/astanin/python-tabulate#number-formatting).
    - `animation`: Same as `text`.
    - `afterStart`: Same as `text`.
    - `colour`: Same as `text`.
    - `y`: Same as `text`.
    - `x`: Same as `text`.
    - `attr`: Same as `text`.
    - `bg`: Same as `text`.

## Key Binding
- Slides List Mode
  - <kbd>↓</kbd>: Next slide
  - <kbd>↑</kbd>: Previous slide
  - <kbd>Space</kbd>: Play ending animation if any
  - <kbd>Enter</kbd>: Switching to *presentation mode*
  - <kbd>q</kbd>: Quit
- Presentation Mode
  - <kbd>→</kbd>: Next slide
  - <kbd>←</kbd>: Previous slide
  - <kbd>Space</kbd>: Play ending animation or next slide
  - <kbd>Enter</kbd> or <kbd>q</kbd>: Switching to *slides list mode*

## Example

![sample.yaml](docs/termslides_sample.gif)

