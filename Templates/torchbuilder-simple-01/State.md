# State Object
## Description
The State object is an object that exists across the whole application and can hold states.
In other words, the purpose of this object is to hold variable that can be accessed from anywhere
in the application without the need to pass the variable in parameters.  This means that I can
add a variable of pi, for example, in the state and this variable will be available anywhere in 
my code.  The advantage of this is that it can make way cleaner code because it helps to avoid passing
a lot of parameters in and out of functions.

## How it works
1. Import the State object in two files
2. In one file, set an attribute of this object (ex: pi)
3. In the second file, if it is run after the initialization of the variable, the pi attribute will be available.

It's that easy!

## Examples
```python
# File 1
from utils import State

State.train_loss = loss.mean()

# File 2
from utils import State

# It will print the value of the training loss without passing any parameters.
print(State.train_loss)
```

In addition, it calculates statistics such as the number of read and write to each state.
If a variable is written more times than it is read, this means that some information is generated and never used.
In this case, you can just call the warning method of the state, and it will output a string telling if
any variable was read less than it was written.
```python
from utils import State

# With the Color module (In yellow)
print(f"{utils.Color(11)}{State.warning()}{utils.ResetColor()}")

# Without color
print(State.warning())
```

See the default templates that uses this object for more examples!