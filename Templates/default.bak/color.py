import sys
import traceback
import re
class Color:
    """
    Use this class to color text.  Just write the color id of your choice.  You can use the ColorPalette class to see
    available colors with their id (number).  Then, place the Color object initialized with its color id at the
    begining of the string needed to be colored, and add the ResetColor object initialized without parameters at the end
    to avoid coloring all the text.

    Example:
        >>>print(f"{Color(154)}I am colored :) {ResetColor()} And I am not colored :(")
    """
    def __init__(self, i):
        self.value = f"\033[38;5;{i}m"
    def __str__(self):
        return self.value

class ResetColor(Color):

    def __init__(self):
        self.value = "\033[0m"


class RGBColor(Color):
    """
    This class is a subclass of Color, but using rgb colors.  Just pass the red value, green value and blue value
    to the constructor.  Values must be between 0 and 255
    """
    def __init__(self, r, g, b):
        """

        :param r: Red [0-255]
        :param g: Green [0-255]
        :param b: Blue [0-255]
        """
        self.value = f"\033[38;2;{r};{g};{b}m"

class ColorPalette:
    """
    Show the color available with their id.  To use it, it is only needed to print the initialized object.

    Example:
        >>>print(f"{ColorPalette()}")
    """
    def __init__(self):
        self.colors = []
        for i in range(255):
            self.colors.append(Color(i))
    def __str__(self):
        values = []
        max_len = 0
        for i, color in enumerate(self.colors):
            name = f"{color}color_{i}"
            if len(name) > max_len:
                max_len = len(name)
            values.append(name)
        s = ""
        counter = 0
        while counter < len(values):
            for _ in range(min(len(values) - counter, 7)):
                s += f"{values[counter]}{' '*(max_len - len(values[counter]))}\t"
                counter += 1
            s += "\n"
        return s

class TraceBackColor:
    """
    Useful class to color traceback with desired colors.
    It is really easy to use, it is only needed to type this line at the top of you main file after importing the class:

    Examples:

        >>> sys.excepthook = TraceBackColor(tb_color=Color(196), path_color=Color(33), line_color=Color(251))

        or use default colors by just writing:

        >>> sys.excepthook = TraceBackColor()

    Note:
        Colors might look different on different systems.
    """
    def __init__(self, tb_color=Color(203), path_color=Color(33), line_color=Color(251)):
        self.tb_color = tb_color
        self.path_color = path_color
        self.line_color = line_color
    def __call__(self, t, value, tb):
        """
        Called by system's exception hook to color tracebacks
        :param t: type
        :param value: value
        :param tb: traceback object
        :return: None
        """
        tb = ''.join(traceback.format_exception(t, value, tb))
        tb = tb.split("\n")
        tb = [self._colorPathLine(line) for line in tb]
        tb = [self._colorLineNumber(line) + "\n" for line in tb]
        tb = "".join(tb)
        print(f"{self.tb_color}{tb}{ResetColor()}")
    def _colorPathLine(self, line: str) -> str:
        """
        Need to be applied to each line.  Will color in the desired color the path in the line
        :param line: the line
        :return: line
        """
        regexp = re.compile(r'File ".*",')
        if regexp.search(line):
            f_idx = line.index(" \"") + 2
            l_idx = line.index("\",")
            return line[:f_idx] + str(self.path_color) + line[f_idx:l_idx] + str(self.tb_color) + line[l_idx:]
        else:
            return line

    def _colorLineNumber(self, line: str) -> str:
        """
        Need to be applied to each line.  Will color in the desired color the line number in the line
        :param line: the line
        :return: line
        """
        regexp = re.compile(r'File ".*",')
        if regexp.search(line):
            f_idx = line.index(", line ") + 7
            l_idx = line.index(", in")
            return line[:f_idx] + str(self.line_color) + line[f_idx:l_idx] + str(self.tb_color) + line[l_idx:]
        else:
            return line



#### Delete this function, it is only used for development
def main_func():
    fn = lambda x: x / 0
    print(fn(10))

if __name__ == '__main__':
    print(ColorPalette())
    # print(f"{Color(154)}I am colored :) {ResetColor()} And I am not colored :(")
    # sys.excepthook = TraceBackColor(tb_color=Color(203))
    # main_func()
    # print(f"{RGBColor(106,206,92)}Hello world!!!{ResetColor()}")




