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
    feedback = FeedBack(1050, max_c=40)
    print(f"Epoch {epoch + 1}/10")
    for i in range(1050):
        # Do training stuff.  For the example, we only add a delay
        time.sleep(0.01)
        feedback(accuracy=((i + 1)/1000), loss=1.1234567)
    
    # Call once with the valid=True when validation steps are done
    feedback(valid=True, accuracy=0.42, loss=1.1234567)
```

## Notes
- To get tqdm kind of theme, use these parameters:
   FeedBack(len(datalaoder), max_c=40, cursor="█", cl="█", cu=" ", delim=("|","|"))
- It integrate well with the DynamicMetric object!

## Method Documentation
```python
    def __init__(self, 
                 total_steps, 
                 max_c=40, 
                 cursor=">", 
                 cl="=", 
                 cu="-", 
                 delim=("[", "]"), 
                 output_rate=10, 
                 float_prec=5, 
                 show_steps=True, 
                 show_eta=True):
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
```
