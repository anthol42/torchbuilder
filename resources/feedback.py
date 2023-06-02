import time
from datetime import datetime
from metrics.dynamicMetric import DynamicMetric

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

        >>> print(f"Epoch {epoch + 1}/10")

        >>> for i in range(1050):

        >>>    feedback(accuracy=((i + 1)/1000), loss=1.1234567)

        >>>    time.sleep(0.01)

        >>> feedback(valid=True, accuracy=0.42, loss=1.1234567)

    Notes:
        - To get tqdm kind of theme, use these parameters:
           FeedBack(1050, max_c=40, cursor="█", cl="█", cu=" ", delim=("|","|"))
        - It integrate well with the DynamicMetric object!
    """
    def __init__(self, total_steps, max_c=40, cursor=">", cl="=", cu="-", delim=("[", "]"), output_rate=10, float_prec=5, show_steps=True, show_eta=True):
        """
        Setup the parameters of the FeedBack object.
        :param total_steps: The total number of steps in the dataloader: usually len(dataloader)
        :param max_c: Maximum number of characters (Length of loading bar)
        :param cursor: The character designing where the progression is.  ( When the process is completed, it is at the complete right.)
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
        """
        self.total = total_steps
        self.max_c = max_c
        self.cursor = cursor
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

    def __call__(self, valid=False, **kwargs):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.current % self.output_rate == 0 or self.current + 1 >= self.total:
            metrics = self.format(valid, kwargs)
            cursor_pos = int(((self.current + 1) / self.total) * self.max_c)
            line = ""
            if self.show_steps:
                line += self.get_stepformat() # f"{self.current}/{self.total} "
            line += f"{self.delim[0]}{self.cl * cursor_pos}{self.cursor}{self.cu * (self.max_c  - cursor_pos)}{self.delim[1]}  "
            if self.show_eta:
                line += f"{self.get_eta(valid)}  "
            line += metrics
            #print(line)
            print("\r" + line, end="")
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

if __name__ == "__main__":
    for epoch in range(10):
        feedback = FeedBack(1050, max_c=40)
        print(f"Epoch {epoch + 1}/10")
        for i in range(1050):
            feedback(accuracy=((i + 1)/1000), loss=1.1234567)
            time.sleep(0.01)
        feedback(valid=True, accuracy=0.42, loss=1.1234567)