# ColorCube
![Collage](https://user-images.githubusercontent.com/18674912/138877773-3f846253-6058-4639-965c-d2dfc5879df8.jpg)

### Game
The turn-based game is about occupying as many squares as possible on the cube. To do this, you can move the cursor on the sides of the cube with a joystick and assign your own player color by pressing a button. Enemy squares can be captured by occupying adjacent free squares.

Check out the project on YouTube: ...

### Tech Details
The project was part of the university course 'Sketching With Hardware' at the LMU Munich and was about prototyping with MicroPython. We build a base with the joystick and button on top of it, as well as as QI wireless charge inside the base. The battery inside the cube can be charged just by putting the cube on top of the base. The communication between the cube and the base takes place via bluetooth. We used two ESP32, one inside the cube for the game funktionality and one inside the base to control the user input.
