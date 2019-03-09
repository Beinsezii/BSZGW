# BSZGW
BeinSeZii Gtk Wrapper

Current status: Basic features usable with low expectations and a lot of caution. This is beginner-level Python, noob-level GTK, and almost incompetent-level git paired with unpredictable levels of development motivation.

## Description
The main purpose of this Python library is to simplify the creation and usage of many common GTK widgets.
The two main design points are (WIP warning):
 * Widgets' values (text in a text box, selected option in a radio list, etc) are always get and set with the .value property
 * Creation of a widget usually uses nothing more than common options and a default value
 * Include common features like tooltips and labels as creation options
 * Probably more to come

## Features
Current widgetes include
 * "Adjuster" - A combination of a slider and spinnbutton. Both can be enabled/disabled on creation.
 * "CheckBox" - Literally just a Gtk.CheckButton with the .value property and tooltip. Questionably useful.
 * "DropDown" - A Combo box that's easier to create. Can set return values independent of display options.
 * "RadioButtons" - A Box with a generated group of radio buttons. Functionally similar to DropDown
 * "TextBox" - A single or multi-line text entry box

<img src="https://github.com/Beinsezii/BSZGW/blob/master/Example%20Apps/example_app_1.png" width="330">

6 widgets (excluding Execute button) made with 6 lines of code.

### Experimental Features
These features have severe problems in usability or practicality at the moment and are subject to scrapping, reformatting, or other major changes
 * "AutoBox" - Automatically generates a layout for apps using boxes. Apps are fed in via a multi-level list, with every "level" (sublist) switching the direction. So if you start off with horizontal orientation the list [[a, b],[c,d]] will create a layout looking like
```
a    c

b    d
```

Which can be visualized like
```
[ (a {c ]

   b) d}
```
  The main [] is the initial horizontal box. (a,b) and {c,d} are vertical boxes inside the horizontal box. The orientation flipping can go on for any number of levels.
Problem is it's nigh unreadable at a glance in the code unless the user gets very creative with their lists, which is extra effort and kinda defeats the point. On the bright side, it also has a mini-feature to accept strings like "50x50" to create blank spaces.

 * "App" - A class that takes a widget/container and turns it into a single-window app with a .launch() function. Questionably useful.

## Development
The previous offline development history was simply updating bszgw.py as I used it and thought of improvements. For now, I don't think that'll change, and as I'm not developing and graphical apps at the moment, it'll probably just recieve small updates to practice Github until I get the motivation to do otherwise.

## History
It's part of my vast collection of unreleased python scripts and utilities sitting around.

It initially started years ago in as a "core file" to share common info between my GIMP 2.8 scripts. Eventually my scripts outgrew what GIMP's automated script UI builder could do, so I started making my own, and realized I should keep common widgets in my "core library", too. Fast-forward to GIMP 2.10 and the library contained a "Beinsezii" version of every one of almost all of GIMPs default available widgets.

One day for reasons I shall never disclose, I was making a script with a lot of input parameters that was atrocious to use in the terminal, so I decided to try and make a GTK 3 app instead and ported over some of the more important, non-gimp-specific widgets from my old core library to GTK 3.

## FAQ
Question|Answer
--------|------
Q. Why is this Readme so long for an arguably useless library?|A. I'm trying to learn good git habits. *Trying*.
Q. Okay but why not use something else to learn git with?|A. The only "useful" program I've made that isn't a hundred-line simple script that anyone could write in a few hours is something that I can never put on a public Git ever. However, that program uses BSZGW to work, so I figured "cool next best thing"
Q. Do something more useful like a Tensowflow experiment.|A. Good question. See, that involves a lot of effort to learn. There's a reason why I put learning C on haitus after I reached pointers despite the app freezing nightmare that is Python.
