# Color API
## Description
Add color to your life, or to your scripts.  This api helps you add color to the console.

It has four classes.

## Classes:

### Color
#### Description
Use this class to color text.  Just write the color id of your choice.  You can use the ColorPalette class to see
available colors with their id (number).  Then, place the Color object initialized with its color id at the
begining of the string needed to be colored, and add the ResetColor object initialized without parameters at the end
to avoid coloring all the text.

#### Example:
```python
print(f"{Color(154)}I am colored :) {ResetColor()} And I am not colored :(")
```

### ResetColor
#### Description
Use this class to reset the color to the default one of the terminal.

#### Example:
```python
print(f"{Color(154)}I am colored :) {ResetColor()} And I am not colored :(")
```

### RGBColor
#### Description
This class is a subclass of Color, but using rgb colors.  Just pass the red value, green value and blue value
to the constructor.  Values must be between 0 and 255

#### Example:
```python
print(f"{RGBColor(106,206,92)}I am colored green :) {ResetColor()}")
```

### ColorPalette
#### Description
Show the color available with their id.  To use it, it is only needed to print the initialized object.

#### Example
```python
print(f"{ColorPalette()}")
```

### TraceBackColor
#### Description
Useful class to color traceback with desired colors.
It is really easy to use, it is only needed to type one line at the top of you main file after importing the class

#### Example
```python
# With full control of colors:
sys.excepthook = TraceBackColor(tb_color=Color(196), path_color=Color(33), line_color=Color(251))

# With default colors (text:red, files:blue, lines:grey)
sys.excepthook = TraceBackColor()
```