import time
from datetime import datetime
import sys
from .color import ResetColor, Color
import math
from utils.dynamicMetric import DynamicMetric
from typing import List, Callable
from concurrent.futures import ThreadPoolExecutor

class FeedBack:
    """
    Class to make a fully customisable and informative loading bar that looks like this:
    Epoch 1/20
    520/1050 [===================>---------------------]  eta 28  s      accuracy=0.52000    loss=1.12346

    How to use:
        1. Create a feedback object with desired parameters. (See init documentation)
        2. Call feedback at each steps with the metrics as kwargs
        3. Call ONCE the feedback object and setting the validation parameter to True at the end of the validation steps

    Examples:
        >>>for epoch in range(10):

        >>> feedback = FeedBack(1050, max_c=40)

        >>> eprint(f"Epoch {epoch + 1}/10")

        >>> for i in range(1050):

        >>>    feedback(accuracy=((i + 1)/1000), loss=1.1234567)

        >>>    time.sleep(0.01)

        >>> feedback(valid=True, accuracy=0.42, loss=1.1234567)

    Notes:
        - To get tqdm kind of theme, use these parameters:
           FeedBack(1050, max_c=40, cursors=(" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"), cl="█", cu=" ", delim=("|","|"))
        - It integrate well with the DynamicMetric object!
    """
    def __init__(self, total_steps: int, max_c: int = 40, cursors: tuple = (">", ), cl: str = "=", cu: str = "-",
                 delim: tuple = ("[", "]"), output_rate: int = 10, float_prec: int = 5, show_steps: bool = True,
                 show_eta: bool = True, color: Color = ResetColor()):
        """
        Setup the parameters of the FeedBack object.
        :param total_steps: The total number of steps in the dataloader: usually len(dataloader)
        :param max_c: Maximum number of characters (Length of loading bar)
        :param cursors: The character designing where the progression is.  ( When the process is completed, it is at the
         total right.)
        :param cl: The characters at the left of the cursor
        :param cu: The characters at the right of the cursor
        :param delim: tuple of length 2.  The first element is the character initiating the loading bar and the second
                      one is the character at the end of the loading bar.
        :param output_rate: Since we call feedback at each steps, output migh be too fast.  Instead of calling feedback
                            once in a while, you can reduce it's output rate by increasing the number: output_rate. This
                            might seems counterintuitive but the output_rate parameter correspond to the number of
                            call the feedback needs to be call before it outputs something.
        :param float_prec: The float precision to display
        :param show_steps: Whether to show at which step the process is
        :param show_eta: Whether to show the eta
        :param color: The color of the text and the progress bar
        """
        self.total = total_steps
        self.max_c = max_c
        self.cursors = cursors
        self.cl = cl
        self.cu = cu
        self.delim = delim
        self.output_rate = output_rate
        self.float_prec = float_prec
        self.show_steps = show_steps
        self.show_eta = show_eta
        self.current = 0
        self.metrics = {}
        self.start_time = None
        self.max_eta_len = 0
        self.color = color

    def __call__(self, valid=False, **kwargs):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.current % self.output_rate == 0 or self.current + 1 >= self.total:
            metrics = self.format(valid, kwargs)
            cursor_pos = int(((self.current) / self.total) * self.max_c)
            cursor_progress = (self.current / self.total) * self.max_c - cursor_pos
            cursor = self.cursors[math.floor(cursor_progress * len(self.cursors))]
            if self.current == self.total:
                cursor = self.cl
            line = ""
            if self.show_steps:
                line += self.get_stepformat() # f"{self.current}/{self.total} "
            line += f"{self.delim[0]}{self.cl * cursor_pos}{cursor}{self.cu * (self.max_c  - cursor_pos)}{self.delim[1]}  "
            if self.show_eta:
                line += f"{self.get_eta(valid)}  "
            line += metrics
            #print(line)
            sys.stderr.write("\r" + str(self.color) + line + str(ResetColor()))
            if valid:
                sys.stderr.write("\n")
            sys.stderr.flush()
        self.current += 1

    def get_stepformat(self):
        total = f"{self.total}"
        current_str = f"{self.current}"
        return f"{' '*(len(total) - len(current_str))}{current_str}/{total} "


    def format(self, valid, kwargs):
        if not valid:
            for key, value in kwargs.items():
                self.metrics[key] = value

        s = ""
        for key, value in self.metrics.items():
            if isinstance(value, DynamicMetric):
                s += f"    {key}={value.avg:.{self.float_prec}f}"
            else:
                s += f"    {key}={value:.{self.float_prec}f}"

        if valid:
            s += "   ||"
            for key, value in kwargs.items():
                if isinstance(value, DynamicMetric):
                    s += f"    val_{key}={value.avg:.{self.float_prec}f}"
                else:
                    s += f"    val_{key}={value:.{self.float_prec}f}"

        return s

    def get_eta(self, valid):
        if valid:
            return f"total {round((datetime.now() - self.start_time).total_seconds())}s"
        if self.current > 10:
            now = datetime.now()
            epoch_wall_time = (now - self.start_time).total_seconds()
            time_per_steps = epoch_wall_time / self.current
            eta = f"{round(time_per_steps * (self.total - self.current))}"
        else:    # 10 first steps are used for calibration
            eta = "s "

        if len(eta) > self.max_eta_len:
            self.max_eta_len = len(eta)
        else:
            eta += " " * (self.max_eta_len - len(eta))

        return f"eta {eta}s"

def eprint(*args, sep=" ", end="\n", color: Color = ResetColor()):
    """
    Analog to print, but to print in the stderr file instead of stdout.  In addition, it auto flush the input.
    In fact, it is only a shortcut since the exact same thing could be done with the print function:

    >>> print("Hello world", file=sys.stderr, flush=True)

    >>># Equivalent to:

    >>> eprint("Hello world")

    :param args: args to print
    :param sep: the separator
    :param end: What to put at the end
    :param color: The color to write the text in.
    :return: None
    """
    args = [str(arg) for arg in args]
    sys.stderr.write(str(color) + sep.join(args) + str(ResetColor()))
    sys.stderr.write(end)
    sys.stderr.flush()

class Loading:
    """
    This class will display an animated loading for undefined progress.  Example:
    Loading [|]    Time Elapsed: 3s

    Examples:
        >>># Initialise the object

        >>>loader = Loading(icons=["[\\]", "[|]", "[/]", "[-]"])

        >>># Run the long-running function and get the results

        >>>results = loader("Loading", high_compute_fn, param1, param2=boo)

        >>>print(results)
    """

    def __init__(self, *, icons: List[str] = ["", ".", "..", "..."],
                 colors: List[Color] = [Color(34), Color(40), Color(46), Color(190), Color(226), Color(220),
                                        Color(214), Color(208), Color(166), Color(202), Color(160), Color(124),
                                        Color(88), Color(52), Color(15)],
                 color_times: List[float] = [5 * (i + 1) for i in range(14)], delay: float = 0.5, sep: str = "\n",
                 show_time: bool = True, console=sys.stdout):
        """
        This is where it is possible to set up the appearance of the loading.
        :param icons: A list of successive strings to display during loading. Must have a len of at least 1.
        :param colors: A list of color to change in function of elapsed time.  Must have a len of at least 1.
        :param color_times: A list of timestamp in seconds over which the color of the text will change for the next
                            color in the color argument.  Since the timestamp change for the NEXT color, this list
                            must have a length shorter by 1 from colors.  Len = len(colors) - 1.
        :param delay: The delay between each screen refresh.  The shorter the delay is, the quicker the refresh rate
                        will be.
        :param sep: The separator to be displayed at the end of the loading.
        :param show_time: If True, it will display the elapsed time.
        :param console: The console on which to write the loading.
        """
        assert len(colors) > 0
        assert len(color_times) == len(colors) - 1, f"{len(color_times)}, {len(colors)}"
        self.icons = icons
        self.sep = sep
        self.colors = colors
        self.colors_times = color_times
        self.console = console
        self.delay = delay
        self.show_time = show_time

    def __call__(self, message: str, fn: Callable, *args, **kwargs):
        """
        This method is used to run a long-running function that doesn't or can't have a progress bar.  It will show
        undefined loading progress.  (Example three dots moving.)

        Note:
            Using this function might add up to the delay(given in __init__) to runtime.
        :param message: The message to be written
        :param fn: The long-running function
        :param args: The arguments of the function
        :param kwargs: The keywords argument of the function.
        :return: The return value of the function.
        """

        def loading(isLoading: List[bool]):
            i = 0
            color_idx = 0
            start = datetime.now()
            while isLoading[0]:
                time_since_start = (datetime.now() - start).total_seconds()
                if self.show_time:
                    self.console.write(f"\r{self.colors[color_idx]}{message} "
                                       f"{self.icons[i % len(self.icons)]}    "
                                       f"Time Elapsed: {round(time_since_start)}s{ResetColor()}")
                else:
                    self.console.write(f"\r{self.colors[color_idx]}{message} "
                                       f"{self.icons[i % len(self.icons)]}{ResetColor()}")
                self.console.flush()
                if color_idx < len(self.colors_times):
                    if time_since_start > self.colors_times[color_idx]:
                        color_idx += 1
                time.sleep(self.delay)
                i += 1
            self.console.write(self.sep)
            self.console.flush()

        isLoading = [True]

        def main(*args, **kwargs):
            result = fn(*args, **kwargs)
            isLoading[0] = False
            return result

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(loading, isLoading)
            results = main(*args, **kwargs)
        return results



