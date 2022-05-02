# figure_ground_segregation

This repository contains the implementation of a psychophyscial figure-ground segregation experiment. An eyetracking device (EyeLink) may be connected. 

**Requirements**

- python 3.6 (3.8 works as well)
- psychopy 2022.1.1
- exptools2 (installation instructions can be found on [this repository](https://github.com/VU-Cog-Sci/exptools2))
- pylink (included in psychopy standalone, but can be retreived on the [sr-research webpage](https://www.sr-support.com/thread-48.html) as well)

**Usage**

To execute the experiment run: ```python main.py sub-xxx ses-x False\True``` <br>
The boolean operator in the end indicates if we want to run it in connection with the eyetracking device.
<br>
Please check the ```settings.yml``` file for experiment settings that can be changed. Enter in the file what hand your subject is going to use! If you want to test if the eyetracker captures the gaze correctly, set ```Test eyetracker``` to ```True```. It is important to insert the correct refreshrate of the monitor, because it is used to calculate the transition speed.
<br>

**Format of stimulus folder**

The program loads the stimuli images by assuming a certain naming convention. 
- This is the structure: ```L{line_length}w{width}s{line_spacing}n{position_noise}_ori{line_orientation_ground}_loc{figure_location_ID}_rep{repetition}.bmp```

<br>
The parameters within the curly brackets can be specified in the settings file. The figure location ID is a number that specifies if the figure is present, and if so, specifying the position. Only left or right is possible. Furthermore, 'a' stands for a real figure and 'b'stands for a boarder figure. Thus, ```Right figure == 1a```, ```Right boarder figure == 1b```. ```Left figure == 2a``` and ```Left boarder figure == 2b```! 


## Code Structure
- ```main.py``` creates the session object.
- ```session.py``` creates the trials and blocks of the exeriment. Creates the stimuli, executes the trials end draws the stimuli.
- ```trial.py``` implements the trial object, which outlines how a trial should look like. Logs button presses and parameters for the trials. 
- ```settings.yml``` contains the experiment and task settings


## Trial Procedure
Example (timing can be changed in setting file): 
1. 300 ms mid grey, red fix dot
2. 100 ms line stimulus, red fix dot
3. 1200-1600 ms mid grey, green fix dot
=> takes 1800 ms on average

**Trial types and Randomization procedure**

- 7 conditions (7 line lengths)
- 75% with figure 25% without figure (pseudorandomized)
- 50% of the figure left, 50% right (pseudorandomized)
- 4 different orientations (fully randomized but prevented identical subsequent orientation)
- 12 different repetitions for figure stimulus, 8 different for no figure stimulus (fully randomized)
- The above values can be changed in the settings file according to needs
- It is important to check if the amount of trials requested for every location (no-figure/boarder-figure/figure) are whole numbers. If not then the right/left ratio will be imbalanced and/or the amount of no figure trials is rounded.



## TODO

- use os.path.join( for path loading!!!
- Add question about task difficulty in the end of each trial!
- scurrently one of the blocks has a couple of trials more, but number of trials conditions per condition is the same within each block
