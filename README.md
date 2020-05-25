# BSZGW
### BeinSeZii Gtk Wrapper
Making the creation of GTK applications so simple, you'll think "wow, I just took a hour and a half python course on YouTube and am very underqualified for what I am trying to do, but now I can at least hide my crazy spaghetti code behind some fancy buttons that I don't understand at any fundamental level. this is amazing"

### Current Status
Features usable with low expectations. Breaking changes basically every relatively important commit.

## Description
Provides replacements for common GTK widgets intended to make dialog and
simple program creation take significantly less effort. Basically I got tired
of 70% of my lines being UI code and thought 'how can I be lazier'

Brief overview:
 - Data-entry widgets *all* have a read/write 'value' property and
   (eventually will) have reset() methods.
 - Tooltips for everything, labels where it makes sense.
 - Widgets are created more 'artistically'
   - Widgets can be created on initialization with common properties as kwargs.
   - The 'new()' method, if present, will create a fully functional widget
     entirely from regular Python types, generating buffers/models as needed.
     Create an entire ComboBox from a dict!

## Widgets
 - **Adjuster** - A combination of a scale and spinnbutton. Both can be enabled/disabled on creation, and the scale can operate in logarithm
 - **Button** - Create a button connected to a function in one line.
 - **CheckButton** - Literally just a Gtk.CheckButton with the .value property extras.
 - **ComboBox** - ComboBox that's easier to create. Notably can be created from a dictionary using ComboBox.new()
 - **Entry** - A single or multi-line text entry box
 - **RadioButtons** - A Box with a generated group of radio buttons.

<img src="./Example Apps/example_app.png" width="400">
Each widget of Example App is created with one line of code

```python
# Start val, min, max, increment, big/page increment.
# Can also be built with a Gtk.Adjustment using Adjuster() instead of Adjuster.new()
adjuster = bszgw.Adjuster.new("Adjuster", 30, 0, 1000, 5, 10,
                              decimals=1, logarithmic=True)
adjuster2 = bszgw.Adjuster.new("Adjuster2", 30, 0, 100, 5, 10,
                               scale=False)

check_button = bszgw.CheckButton("Check Button", True)

# Can be built with a dict using ComboBox.new(), or a Gtk.TreeModel using ComboBox()
# Sort of a WIP, as right now it's only useful for text.
combo_box = bszgw.ComboBox.new(
    {"Choice A": "a", "Choice B": "b", "Choice C": "c"}, "a",
    tooltip="Combo Box"
)

radio_buttons = bszgw.RadioButtons(
    "Radio Buttons",
    ["Choice A", "Choice B", "Choice C"], 0
)

entry = bszgw.Entry("Entry", "Text\nLine 2")

# yes I'm this lazy.
exec_button = bszgw.Button("Execute", Your_Function_Here)
```

## Containers & Other Features
### AutoBox
Automatically generates a layout for apps using boxes. Widgets are fed in via a multi-level list, with every "level" (sublist) switching the direction.

Again referring to Example App, the organization of the widgets goes as follows
 
```python
adjuster2_combo = bszgw.AutoBox([
    adjuster2,
    combo_box
])

left_side = bszgw.AutoBox([
    adjuster,
    [adjuster2_combo, radio_buttons]
])

right_side = bszgw.AutoBox([
    entry,
    [check_button, exec_button]
])

box = bszgw.AutoBox([[left_side, right_side]])
```
This method is maximum readability using one 'level' of recursion in the lists. It's basically the same thing PySimpleGUI does. AutoBox also supports any amount of 'depth' via lists *inside* lists, with each level of 'depth' switching orientation. Questionably useful, as readability drops off immensely.

### Grid
Gtk.Grid with extra methods for attaching widgets.
 - **GridChild** - Can be substituted in Grid's new methods in place of regular widgets. Contains additional properties to influence placement.

 The example app's layout looks like 
 ```python
grid = bszgw.Grid()
# GridChild just packs a widget with some extra properties for
# adding to the grid
GC = bszgw.GridChild

grid.attach_all(
    GC(adjuster, width=2),
    adjuster2, GC(radio_buttons, col_off=1, height=2),
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
 
### Message
Function that simply opens a pop-up displaying a message. Possible expansion. 

## Experimental Features
These features are still in conceptual stages and subject to many many reformats.
### App
A class that takes a widget/container and turns it into a single-window app with a .launch() function.

In Example App, the code to create the interactable window with the widget layout is only two lines
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
