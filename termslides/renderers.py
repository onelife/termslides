# -*- coding: utf-8 -*-

from os import path
from subprocess import Popen, PIPE
from asciimatics.renderers import StaticRenderer
from tabulate import tabulate


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
    PLANTUML_PATH = path.join(path.dirname(__file__), 'lib', 'plantuml.1.2021.9.jar')
    PLANTUML_URL = 'http://www.plantuml.com/plantuml/txt/'
    _CACHE = {}

    def __init__(self, text: str) -> None:
        """
        :param text: The text string to show.
        """
        super(UMLText, self).__init__()
        self.uml = self.get_plantuml()
        self._images = [self.uml.processes(text).decode("utf-8")]

    @staticmethod
    def processes(text: str) -> str:
        key = hash(text)
        if key in UMLText._CACHE:
            return UMLText._CACHE[key]
        proc1 = Popen(['printf', text], stdout=PIPE, stderr=PIPE)
        proc2 = Popen(['java', '-jar', UMLText.PLANTUML_PATH, '-utxt', '-p'], stdin=proc1.stdout, stdout=PIPE, stderr=PIPE)
        output, error = proc2.communicate()
        if proc2.returncode:
            return error
        UMLText._CACHE[key] = output
        return output

    @staticmethod
    def get_plantuml() -> bool:
        from sys import platform
        from plantuml import PlantUML
        # check local lib
        proc = Popen(['java', '-jar', UMLText.PLANTUML_PATH, '-version'], stdout=PIPE, stderr=PIPE)
        _ = proc.communicate()
        if proc.returncode or platform != 'linux':
            return PlantUML(UMLText.PLANTUML_URL)
        return UMLText


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
