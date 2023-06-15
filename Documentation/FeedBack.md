# FeedBack API
## Description
Class to make a fully customisable and informative loading bar that looks like this:
    
Epoch 1/20
    
520/1050 [===================>---------------------]  eta 28  s      accuracy=0.52000    loss=1.12346

## How to use
1. Create a feedback object with desired parameters. (See init documentation)
2. Call feedback at each steps with the metrics as kwargs
3. Call ONCE the feedback object and setting the validation parameter to True at the end of the validation steps

## Examples
```python
 for epoch in range(10):
     feedback = FeedBack(1000, max_c=40, color=RGBColor(106,206,92))
     eprint(f"Epoch {epoch + 1}/10", color=RGBColor(200,200,200))
     for i in range(1000):
         feedback(accuracy=((i + 1)/1000), loss=1.1234567)
         
         # ######################
         # Do training stuff here
         time.sleep(0.01)
         # ######################
     
      # ######################
      # Do evaluation stuff here
      time.sleep(0.01)
      # ######################   
     feedback(valid=True, accuracy=0.42, loss=1.1234567)
     eprint()
```

## Notes
- To get tqdm kind of theme, use these parameters:
```python
FeedBack(1050, max_c=40, cursors=[" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"], cl="█", cu=" ", delim=("|","|"))
```

- It integrate well with the DynamicMetric object!

## Method Documentation
```python
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
```

## Bonus:

### Description
The feedback package comes with a built-in function that can print to the stderr output, and
automatically flush the data.  It is strongly suggested to use this function instead of
the original print function for lines over a feedback bar.  This will assure a good format.
In addition, the function is real;y easy to use since its interface is exactly like the original
print.

### eprint

The function is called eprint.  Here is its signature and documentation:
```python
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
```

