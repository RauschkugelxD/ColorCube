# ColorCube
![Collage](https://user-images.githubusercontent.com/18674912/139105132-e1416f99-8ea6-4d27-bfd9-854e69a89b1b.jpg)

### Game
The turn-based game is about occupying as many squares as possible on the cube. To do this, you can move the cursor on the sides of the cube with a joystick and assign your own player color to a white square by pressing a button. Enemy squares can be captured by occupying adjacent free squares.

👉 Demo on [YouTube](https://youtu.be/phO6X74dV8Q)

### Tech Details
The project was part of the university course 'Sketching With Hardware' at the LMU Munich and was about prototyping with MicroPython. We build a wooden base with a joystick and a button on top of it, as well as as QI wireless charge inside the base. The battery inside the cube can be charged just by putting the cube on top of the base. The communication between the cube and the base takes place via bluetooth. We used two ESP32, one inside the cube to handle all its components and one inside the base for user input and the overall game functionality.
