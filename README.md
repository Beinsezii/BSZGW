# BSZGW
### BeinSeZii Gtk Wrapper
Making the creation of GTK applications so simple, you'll think "wow, I just took a hour and a half python course on YouTube and am very underqualified for what I am trying to do, but now I can at least hide my crazy spaghetti code behind some fancy buttons that I don't understand at any fundamental level. this is amazing"

### Current Status
Features usable with low expectations.

## Description
The main purpose of this Python library is to simplify the creation and usage of many common GTK widgets.

### Main Design Goals
 * Widgets' values (text in a text box, selected option in a radio list, etc) are always get and set with the .value property
 * Creation of a widget usually uses nothing more than starting values
 * Include common features like tooltips and labels as creation options
 * Probably more to come (notably space reservation)

## Features
### Widgets
Current widgetes include
 * **"Adjuster"** - A combination of a slider and spinnbutton. Both can be enabled/disabled on creation.
 * **"Button"** - Create a button connected to a function in one line.
 * **"CheckBox"** - Literally just a Gtk.CheckButton with the .value property and tooltip.
 * **"DropDown"** - A Combo box that's easier to create. Can set return values independently of display options.
 * **"RadioButtons"** - A Box with a generated group of radio buttons. Functionally similar to DropDown
 * **"TextBox"** - A single or multi-line text entry box

<img src="https://github.com/Beinsezii/BSZGW/blob/master/Example%20Apps/example_app_1.png" width="330">
Each widget of Example App is created with one line of code

```python
test_adjuster = bszgw.Adjuster("Test Adjuster", 30, 0, 100, 5, 10)
test_adjuster2 = bszgw.Adjuster("Test Adjuster2", 30, 0, 100, 5, 10, decimals=1, slider=False)
test_check = bszgw.CheckBox("Test Check Box", True)
test_drop_down = bszgw.DropDown("Test Drop Down", [["Choice A", "A"], ["Choice B", "B"], ["Choice C", "C"]], "A", enums=True)
test_radio = bszgw.RadioButtons("Test Radio Buttons", ["Choice A", "Choice B", "Choice C"], 0)
test_text_box = bszgw.TextBox("Test Text Box", "Test Text\nLine 2")
exec_button = bszgw.Button("Execute", Your_Function_Here)
```

### Other Features
 * **"AutoBox"** - Automatically generates a layout for apps using boxes. Apps are fed in via a multi-level list, with every "level" (sublist) switching the direction.
 Again referring to Example App, the organization of the widgets goes as follows
 
 ```python
adjuster2_dropdown = bszgw.AutoBox([
    test_adjuster2,
    test_drop_down
    ])

left_side = bszgw.AutoBox([
    test_adjuster,
    [adjuster2_dropdown, test_radio]
    ])

right_side = bszgw.AutoBox([
    test_text_box,
    [test_check, exec_button]
    ])

final_box = bszgw.AutoBox([left_side, right_side],
    orientation=Gtk.Orientation.HORIZONTAL)
 ```
This method is maximum readability using one 'level' of recursion in the lists. It's basically the same thing PySimpleGUI does.

However, AutoBox supports any amount of 'depth' via lists *inside* lists, with each level of 'depth' switching orientation. The same code above can be re-written into something that's much smaller but also very hard to visualize
```python
final_box = bszgw.AutoBox([
    [test_adjuster,
    [[test_adjuster2,
    test_drop_down], test_radio]],
    [test_text_box,
    [test_check, exec_button]]
    ], orientation=Gtk.Orientation.HORIZONTAL)
```
Note you can also simply put the main list inside a list instead of manually switching the orientation, like [[widgets are horizontal now]], but I prefer setting the orientation property for readability.
### Experimental Features
These features are still in conceptual stages and subject to many many reformats.
* **"App"** - A class that takes a widget/container and turns it into a single-window app with a .launch() function.
In Example App, the code to create the interactable window with the widget layout is only two lines
```python
test_app = bszgw.App("Test App", final_box)
test_app.launch()
```

## Development
The previous offline development history was simply updating bszgw.py as I used it and thought of improvements. Future development will basically be the exact same thing except I push updates to git so I can be harshly judged by people.

## History
It's part of my vast collection of unreleased python scripts and utilities sitting around.

It initially started years ago in as a "core file" to share common info between my GIMP 2.8 scripts. Eventually my scripts outgrew what GIMP's automated script UI builder could do, so I started making my own, and realized I should keep common widgets in my "core library", too. Fast-forward to GIMP 2.10 and the library contained a "Beinsezii" version of every one of almost all of GIMPs default available widgets.

One day for reasons I shall never disclose, I was making a script with a lot of input parameters that was atrocious to use in the terminal, so I decided to try and make a GTK 3 app instead and ported over some of the more important, non-gimp-specific widgets from my old core library to GTK 3.

## FAQ
Question|Answer
--------|------
**Q.** Why is this Readme so long for an arguably useless library?|**A.** I'm trying to learn good git habits. *Trying*.
**Q.** Okay but why not use something else to learn git with?|**A.** The only "useful" program I've made that isn't a hundred-line simple script that anyone could write in a few hours is something that I can never put on a public Git ever. However, that program uses BSZGW to work, so I figured "cool next best thing"
**Q.** Do something more useful like a Tensowflow experiment.|**A.** Good question. See, that involves a lot of effort to learn. There's a reason why I put learning C on haitus after I reached pointers.
