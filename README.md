# HoverRulerPlugin
A function test package for klayout hover ruler

Functions will be merge to CenterRuler Plugin 

Forked from [s910324/HoverRulerPlugin](https://github.com/s910324/HoverRulerPlugin).

# Installation and setup
Currently not avaliable on Klayout.salt, package needs to be manual installed.
* Download the package as zip
* Unzip the file and place `HoverRuler` folder under `~/.klayout/salt/` (*nix) or `%USERPROFILE%\KLayout\salt\` (Windows) folder

# Functions 
* Shows edge length while hovered
* Drop ruler automatically on left click
* Show corner angle on hover
* Clicking right mouse button switches measure mode into
    - Total length (`d = length()`)
    - Horizontal and vertical length (`dx = dx()`, `dy = dy()`)
    - Angle (`a = atan( abs(dx()) / abs(dy()) )`)
    - Complimentary angle (`90 - a = atan( abs(dx()) / abs(dy()) )`)
  
# Upcomming features (Planning)
* Detect rounded corner radius on hover

# Remark
* Marker Text shows differently between Win/Linux platform (Win small box at text origin / Linux text with bound box)

# Changelog
### 0.1
* Clicking right mouse button switches measure mode

### 0.00
* Patch plugin fails to start up issue.
* Patch with Redo/undo for measurement

