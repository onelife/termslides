# -*- coding: utf-8 -*-

from asciimatics.renderers import StaticRenderer
from tabulate import tabulate
from plantuml import PlantUML


class NormalText(StaticRenderer):
    """
    This class renders the supplied text without effect.
    """

    def __init__(self, text):
        """
        :param text: The text string to show.
        """
        super(NormalText, self).__init__([text])


class UMLText(StaticRenderer):
    """
    This class renders the supplied text to UML diagram.
    """
    UML = PlantUML('http://www.plantuml.com/plantuml/txt/')

    def __init__(self, text):
        """
        :param text: The text string to show.
        """
        super(UMLText, self).__init__()
        self._images = [self.UML.processes(text).decode("utf-8")]


class TableText(StaticRenderer):
    """
    This class renders the supplied text to table.
    """

    def __init__(self, data, hasHeader=False, tablefmt='grid', numalign="decimal", floatfmt='g'):
        """
        :param data: The table data to show.
        """
        super(TableText, self).__init__()
        headers = 'firstrow' if hasHeader else ()
        self._images = [
            tabulate(data, headers=headers, tablefmt=tablefmt, numalign=numalign, floatfmt=floatfmt)]
