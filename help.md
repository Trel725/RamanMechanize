# Stepper Control
This program is written to bring the capability of automated positioning and
program execution to microscope with stepper motors.

## Usage


1. At first, the connection with stepper controller (running GRBL firmware) need to
be estblished. For this, select the serial port of controller in the 
drop-down menu and click connect. If you can't see the port of controller,
make sure it is connected and re-run the  program.

2. If connection is succeffully established, string "Initializing grbl"
should appear and current state of controller will be displayed on the 
top of window.

3. If absolute coordinate system is enabled, after initialization 
state will be changed to Alarm, showing that homing need to be performed.
This could be done by pressing "Start homing cycle" button.

4. After homing cycle, button "Go to central position" could be pressed
to perform centering.

5. Arrow keys may be used to navigate system to desired location. By pressing
"Add position to queue" current position will be saved to program.

6. By pressing "Add Raman to queue" the program will add the command of
spectrum gathering to the file, name of which could be specified in the
input field above the button.

7. Program could be made by subseqent adding of coordinates and raman
execution commands. Commands could be deleted or moved by mouse. 
Editing of command is possible by double clicking but is not recommended.

8. Program is activated by pressing "Start!" button. Execution details
are visible in the log window on the bottom. Program could be stopped
by pressing "Stop" or paused by pressing "Pause" button. Pausing will
take some time as current cycle need to be finished before pausing.

9. Programs could be saved and loaded by "Program" submenu in the top.

## Extra features

###Circle

To automatically collect a few scans around one point, the circle mode could be used.
It is necessary to select number of point in the "points" window and corresponding 
radius in the nearby "rad" window. After this is done, by pressing "Circle" button
corresponding program will be added to the queue.

###Mapping

Mapping is a method of obtaining information about chemical composition of the surface.
For that, two corners of the desired rectangular area need to be selected. For this

1. Move to the first corner and press button "Corner 1"

2. Move to the second corner, press "Corner 2"

3. Modify, if necessary "dx" and "dy" values. which correspond to the step size
in X and Y direction respectivelly.

4. Press "Add Mapping" button and corresponding command will be generated and 
added to the queue.

After generating any of the programs it need be started by pressing "Start" button
## Trobleshooting

Sometimes controller may be overloaded, which may occur in case of sudden
pressing of different arrow buttons in the same time. In that case reset
may be performed by pressing on the "STOP" button in the bottom. After that,
re-homing may be necessary.
