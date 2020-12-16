# BSZGW
### BeinSeZii Gtk Wrapper
Making the creation of GTK applications so simple, you'll think "wow, I just took a hour and a half python course on YouTube and am very underqualified for what I am trying to do, but now I can at least hide my crazy spaghetti code behind some fancy buttons that I don't understand at any fundamental level. this is amazing"

### Current Status
Features usable with mild expectations. Breaking changes will be frequent but marked in semver.

## Description
Provides replacements for common GTK widgets intended to make dialog and
simple program creation take significantly less effort. Basically I got tired
of 70% of my lines being UI code and thought 'how can I be lazier'

Brief overview:
 - Data-entry widgets have many extra features courtesy of the DataWidget mixin
   - `value` property
   - `reset` method
   - `connect_changed` method
 - Labels for everything
 - Widgets are created more 'artistically'
   - The 'new()' method, if present, will create a fully functional widget
     entirely from regular Python types, generating buffers/models as needed

### Widgets
 - **Button** - Create a button connected to a function in one line
 - **CheckButton** - Literally just a Gtk.CheckButton with the DataWidget mixin
 - **ComboBox** - ComboBox that's easier to create
 - **Entry** - A single or multi-line text entry box
 - **RadioButtons** - A Box with a generated group of radio buttons
 - **SpinScale** - A combination of a scale and spinnbutton. The scale can operate in logarithm

### Containers
 - **App** - A Window extended to control the program state
 - **AutoBox** - A fuction that recursively boxes items in nested lists
 - **Grid** - A Gtk.Grid with extra methods for attaching widgets
   - **GridChild** - a simple struct around a widget that can be fed to Grid's attach
     functions in place of an actual widget to specify more precise placement
 - **Message** - A small function to display a message in a pop-up

### MixIns
  - **DataWidget** - Provides some uniform methods and properties for data-entry widgets.
    Allows for basic polymorphism.
<img src="./Example Apps/screenshot.png" width="400">
Each widget of Example App is created with one line of code

```python
# Start val, min, max, increment, big/page increment.
# Can also be built with a Gtk.Adjustment using
# SpinScale() instead of SpinScale.new()
spinscale = bszgw.SpinScale.new(
    30, -1000, 10000, 5, 10,
    label="SpinScale", digits=1, logarithmic=True
)
check_button = bszgw.CheckButton("Check Button", True)

# Logarithmic scale can be enabled/disabled at will
log_check = bszgw.CheckButton("Logarithmic", True)

# Creates a Gtk.TreeModel fom a dict
combo_box = bszgw.ComboBox.new(
    {"Choice A": "a", "Choice B": "b", "Choice C": "c"}, "a",
)

entry = bszgw.Entry("Entry", "Text\nLine 2", multi_line=True)

radio_buttons = bszgw.RadioButtons(
    "Radio Buttons",
    ["Choice A", "Choice B", "Choice C"], 0,

exec_button = bszgw.Button("Execute", get_vals)
)
```

And the widgets are easy to pack together using the containers using **AutoBox**
```python
logcheck_combo = bszgw.AutoBox([
    log_check,
    combo_box
])

left_side = bszgw.AutoBox([
    adjuster,
    [logcheck_combo, radio_buttons]
])

right_side = bszgw.AutoBox([
    entry,
    [check_button, exec_button]
])

box = bszgw.AutoBox([[left_side, right_side]])
```
or **Grid**
 ```python
grid = bszgw.Grid()
# GridChild just packs a widget with some extra properties for
# adding to the grid
GC = bszgw.GridChild

grid.attach_all(
    GC(spinscale, width=2),
    log_check, GC(radio_buttons, col_off=1, height=2),
    combo_box,
)

# nothing stopping you from using GridChild to attach these all at once
# but I think it looks nicer this way.
grid.attach_all(
    GC(entry, width=2, height=2),
    check_button, GC(exec_button, col_off=1),
    column=3
)

 ```
 
And finally, in Example App, the code to create the interactable window with the widget layout is only two lines
```python
app = bszgw.App("App Name", grid)
app.launch()
```

## Development
The previous offline development history was simply updating bszgw.py as I used it and thought of improvements. Future development will basically be the exact same thing except I push updates to git so I can disappoint people.

## History
It's part of my vast collection of unreleased python scripts and utilities sitting around.

It initially started years ago in as a "core file" to share common info between my GIMP 2.8 scripts. Eventually my scripts outgrew what GIMP's automated script UI builder could do, so I started making my own, and realized I should keep common widgets in my "core library", too. Fast-forward to GIMP 2.10 and the library contained a "Beinsezii" version of every one of almost all of GIMPs/GTK2s common widgets.

One day I was making a script with a lot of input parameters that was atrocious to use in the terminal, so I decided to try and make a GTK 3 app instead and ported over some of the more important, non-gimp-specific widgets from my old core library to GTK 3.

## FAQ
Question|Answer
--------|------
**Q.** Do something more useful like a Tensowflow experiment.|**A.** Good question. See, that involves a lot of effort to learn. There's a reason why I put learning C on haitus after I reached pointers.
