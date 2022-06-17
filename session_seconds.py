#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/03 13:44:52
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

from urllib import response
import numpy as np
from psychopy.hardware import keyboard
import os
import re
import time
from psychopy import visual
from exptools2.core import PylinkEyetrackerSession
from trial import FGSegTrial
import random

opj = os.path.join

class FigureGroundSession(PylinkEyetrackerSession):

    def __init__(self, output_str, output_dir, settings_file, subject_ID, eyetracker_on):
        """
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs)
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        subject_ID : int
            ID of the current participant
        eyetracker_on : bool 
            Determines if the cablibration process is getting started.
        """

        super().__init__(output_str, output_dir, settings_file, eyetracker_on=eyetracker_on)

        self.fixation_ready_duration = self.settings['Task settings']['Fixation ready duration']
        self.nr_of_trials = self.settings['Task settings']['Number of trials']
        self.line_lengths = self.settings['Task settings']['Line lengths']
        self.line_widths = self.settings['Task settings']['Line widths']
        self.line_spacings = self.settings['Task settings']['Line spacing']
        self.position_noises = self.settings['Task settings']['Position noise']
        self.line_orientations = self.settings['Task settings']['Line orientations']
        self.stim_size = self.settings['Task settings']['Stimulus size']
        self.trial_no_figure = self.settings['Task settings']['No figure trials']
        self.trial_figure = self.settings['Task settings']['Figure trials']
        self.trial_boarder_figure = self.settings['Task settings']['Boarder figure trials']        
        self.repetitions = self.settings['Task settings']['Repetitions']    
        self.nr_blocks = self.settings['Task settings']['Blocks']    
        self.break_duration = self.settings['Task settings']['Break duration']
        self.after_break = self.settings['Task settings']['After break duration']
        self.stimulus_path = self.settings['Task settings']['Stimulus path']
        self.test_stimulus_path = self.settings['Task settings']['Test stimulus path']
        self.test_stimulus_file = self.settings['Task settings']['Test stimulus file']
        self.test_stimulus_duration = self.settings['Task settings']['Test stimulus duration']
        self.stimulus_duration = self.settings['Task settings']['Stimulus duration']
        self.response_window_duration = self.settings['Task settings']['Response window']
        self.break_buttons = self.settings['Task settings']['Break buttons']
        self.exit_key = self.settings['Task settings']['Exit key']
        self.monitor_refreshrate = self.settings['Task settings']['Monitor refreshrate']
        self.load_background_stimuli = self.settings['Task settings']['Load background stimuli']
        self.grey_value = self.settings['Task settings']['Grey value']
        self.red_value = self.settings['Task settings']['Red value']
        self.green_value = self.settings['Task settings']['Green value']

        if self.settings['Task settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)

        # check if the trial separation (in the different locations, no figure, boarder figure,...) add up to 1
        all_location_check = self.trial_boarder_figure + self.trial_figure + self.trial_no_figure
        if not all_location_check == 1:
            raise Exception("Warning! The percentage of no-figure/figure/boarder-figure trials have to add up to 1!")

        # randomly choose if the participant responds with upper for no lower for yes or vice versa
        if random.uniform(1,100) < 50:
            self.response_button = 'upper_yes'
            self.button_instructions = 'Upper Button - YES\n Lower Button - NO'
        else:
            self.response_button = 'upper_no'
            self.button_instructions = 'Upper Button - NO\n Lower Button - YES'

        # initialize keyboard for the button presses 
        self.kb = keyboard.Keyboard()

        # list to create the stimuli and random backgrounds 
        self.stimuli_list = []
        self.background_list = []

        self.create_trials()
        self.create_stimuli()

                                                                                                                                                                                                                                                                          
    def create_trials(self):
        """
        Creates the trials with its phase durations and randomization. 
        One trial looks like the following:
        1) Fixation period: background stimulus only, together with fixation dot 
        2) Figure stimulus (e.g., in 40% right/left from fixation, 20% no stimulus)
        3) Response window 
        """

        self.trial_list = []
 
        # create array with all figure locations (0 - no figure, 1 - right, 2 - left)
        # this array should be there fore every condition\linelength
        all_figure_locations = []
        
        amount_figures_right = self.trial_figure*0.5*self.nr_of_trials
        amount_figures_left = self.trial_figure*0.5*self.nr_of_trials
        amount_boarder_figures_right = self.trial_boarder_figure*0.5*self.nr_of_trials
        amount_boarder_figures_left = self.trial_boarder_figure*0.5*self.nr_of_trials
        trial_no_figure = self.trial_no_figure*self.nr_of_trials

        print('suggested nr of trials with figures left/right', amount_figures_right)
        print('suggested amount of trials with boarder figures left/right', amount_boarder_figures_right)
        print('suggested nr of trials with no figure', trial_no_figure)

        # check if the trial distribution is equal/ all whole numbers. If not, append one more trial (left or right trial randomly chosen)
        raise_exp = False

        if not (amount_figures_right % 1) == 0:
            if random.uniform(1,100) < 50:
                amount_figures_right = int(amount_figures_right)
                amount_figures_left = int(amount_figures_left) + 1
            else:
                amount_figures_right = int(amount_figures_right) + 1
                amount_figures_left = int(amount_figures_left) 
            raise_exp = True
        if not (trial_no_figure % 1) == 0:
            trial_no_figure = round(trial_no_figure)
            raise_exp = True
        if not (amount_boarder_figures_right % 1) == 0:
            if random.uniform(1,100) < 50:
                amount_boarder_figures_right = int(amount_boarder_figures_right)
                amount_boarder_figures_left = int(amount_boarder_figures_left) + 1
            else:
                amount_boarder_figures_right = int(amount_boarder_figures_right) + 1
                amount_boarder_figures_left = int(amount_boarder_figures_left)
            raise_exp = True
            
        if raise_exp:
            print("The amount of no-figure/figure/boarder-figure trials each has to be a whole number.\n" 
                  "Will round the amount of trials!")
        
        actual_nr_of_trials = amount_boarder_figures_left + amount_boarder_figures_right + amount_figures_right + amount_figures_left + trial_no_figure

        print(f"Amount of trials:\nboarder figures right:{amount_boarder_figures_right}\nboarder figures left:{amount_boarder_figures_left}\nno figures: {trial_no_figure}\n"
               f"figures right:{amount_figures_right}\nfigures left:{amount_figures_left}\nall trials:{actual_nr_of_trials}\n")
        
        # We need as many figure locations as there are trials for each linelength
        for i in self.line_lengths:
            figure_locations_list = [*[0]*int(trial_no_figure), *['1a']*int(amount_figures_right),
                                    *['2a']*int(amount_figures_left), *['1b']*int(amount_boarder_figures_right), *['2b']*int(amount_boarder_figures_left)]
            all_figure_locations.append(figure_locations_list)

        # get the phase durations and names for every trial
        self.phase_duration = [self.fixation_ready_duration, self.stimulus_duration]
        self.phase_names = ["fixation", "stimulus", "response_window"]
        self.phase_duration_button_check = [0, self.break_duration, self.after_break, self.test_stimulus_duration, self.after_break, self.test_stimulus_duration]
        self.phase_names_break =  ['break', 'button_check', 'after_break', 'check_first', 'check_break', 'check_second']

        # depending on how many breaks the experiement has, the conditions are spread over the blocks equally
        append_rest = random.randint(0,2)
        indexes_all_blocks = []
        trial_count = 0
        previous_orientation = 0

        self.add_button_check()

        # only a 'please wait' and blank screen to get ready for the real block 
        pre_trial = FGSegTrial(self, 0, 0, [0, 0, self.after_break, 0, 0, 0], self.phase_names_break, 'break', -1, 'break', 0, 0, 0, 0, 0, 0, 'seconds')
        self.trial_list.append(pre_trial)

        for i in range(self.nr_blocks):
            
            # calculate the nr of trials per condition in this block
            # if the nummber of trials cannot equally be separated among the blocks, add the leftover to a random block
            if i == append_rest:
                trials_per_cond = int(actual_nr_of_trials/self.nr_blocks)+actual_nr_of_trials%self.nr_blocks
            else:
                trials_per_cond = int(actual_nr_of_trials/self.nr_blocks)
                
            # create an index list which keeps track of which combination we've already used 
            index_list = list(range(len(self.line_lengths)))
            indexes_current_block = np.repeat(index_list, trials_per_cond)                                          
            indexes_all_blocks.append(indexes_current_block)

            for trial_nr in range(len(indexes_current_block)):

                # randomly draw (we do this by first shuffeling and then picking the first element) an index, which choses the combination for this trial
                np.random.shuffle(indexes_current_block)
                trial_index = indexes_current_block[0]
                indexes_current_block = indexes_current_block[1:]

                # select the correct figure location list (each condition has an own one)  
                # randomly choose figure location (0 - no figure, 1 - right, 2 - left)
                # now get the figure location (choose the right array for this)
                line_length = self.line_lengths[trial_index]
                np.random.shuffle(all_figure_locations[trial_index])
                figure_location_ID = all_figure_locations[trial_index][0]
                all_figure_locations[trial_index] = all_figure_locations[trial_index][1:]
                
                # easier to recognize location in analysis and randomly draw repetition number
                if figure_location_ID == 0:
                    figure_location = 'no_figure'
                    repetition = random.randint(1, self.repetitions[1])
                elif figure_location_ID == '1a':
                    figure_location = 'figure_right'
                    repetition = random.randint(1, self.repetitions[0])
                elif figure_location_ID == '2a':
                    figure_location = 'figure_left'
                    repetition = random.randint(1, self.repetitions[0])
                elif figure_location_ID == '1b':
                    figure_location = 'boarder_figure_right'
                    repetition = random.randint(1, self.repetitions[0])
                elif figure_location_ID == '2b':
                    figure_location = 'boarder_figure_left'
                    repetition = random.randint(1, self.repetitions[0])

                # randomly set the line orientation for the background 
                # check if the orientation was like this before already, then shuffle again!
                while True:
                    np.random.shuffle(self.line_orientations)
                    line_orientation_ground = self.line_orientations[0]
                    if previous_orientation!=line_orientation_ground:
                        break
                previous_orientation = line_orientation_ground 
                

                # load the stimuli in a list already so that the drawing is faster
                width = self.line_widths[trial_index]
                line_spacing = self.line_spacings[trial_index]
                position_noise = self.position_noises[trial_index]
                current_stimulus_string = f'''{self.stimulus_path}L{line_length}w{width}s{line_spacing}n{position_noise}_ori{line_orientation_ground}_loc{figure_location_ID}_rep{repetition}.bmp'''
                current_stimulus = visual.ImageStim(self.win, units='deg', image=current_stimulus_string, size=self.stim_size)
                self.stimuli_list.append(current_stimulus)

                # make a list for random background noise (we need the loop to get two backgrounds - for the fixation and for the response window)
                for _ in range(2):

                    # for this, first find a line orientation that does not equal the stimulus
                    while True:
                        np.random.shuffle(self.line_orientations)
                        background_orientation = self.line_orientations[0]
                        if previous_orientation!=background_orientation:
                            break

                    if self.load_background_stimuli:
                        # randomly choose an index 
                        background_index = np.random.randint(7)
                        background_line_length =  self.line_lengths[background_index]
                        background_width = self.line_widths[background_index]
                        background_line_length = self.line_lengths[background_index]
                        background_figure_location_ID = 0
                        background_line_spacing = self.line_spacings[background_index]
                        background_position_noise = self.position_noises[background_index]
                        background_string = f'''{self.stimulus_path}L{background_line_length}w{background_width}s{background_line_spacing}n{background_position_noise}_ori{background_orientation}_loc{background_figure_location_ID}_rep{repetition}.bmp'''
                        background_stimulus = visual.ImageStim(self.win, units='deg', image=background_string, size=self.stim_size)
                        self.background_list.append(background_stimulus)
                
                trial_count += 1
                response_window = random.uniform(self.response_window_duration[0], self.response_window_duration[1])
                trial_phase_duration = self.phase_duration + [response_window]
                trial = FGSegTrial(self, trial_count, i, trial_phase_duration, self.phase_names, line_length,
                                    figure_location_ID, figure_location, repetition, line_orientation_ground,
                                    position_noise, line_spacing, width, response_window, 'seconds')
                                    
                self.trial_list.append(trial)

            # append trial which includes a break with the option to wait and button check before and after
            if i < self.nr_blocks-1:
                
                self.add_button_check()
                # break 
                break_trial = FGSegTrial(self, 0, i, [self.break_duration, 0, 0, 0, 0, 0], self.phase_names_break, 'break', -1, 'break', 0, 0, 0, 0, 0, 0, 'seconds')
                self.trial_list.append(break_trial)
                self.add_button_check()

                # only a 'please wait' and blank screen to get ready for the real block 
                pre_trial = FGSegTrial(self, 0, 0, [0, 0, self.after_break, 0, 0, 0], self.phase_names_break, 'break', -1, 'break', 0, 0, 0, 0, 0, 0, 'seconds')
                self.trial_list.append(pre_trial)

    def create_stimuli(self):

        # fixation dot in red (for the first two phases of the trial)
        self.fixation_dot_red = visual.Circle(self.win, 
            radius=0.2/2, 
            units='deg', colorSpace='rgb255', lineColor=self.red_value, fillColor=self.red_value)

        self.fixation_dot_green = visual.Circle(self.win, 
            radius=0.2/2, 
            units='deg', colorSpace='rgb255', lineColor=self.green_value, fillColor=self.green_value)

        self.break_stim = visual.TextStim(self.win, text="Break")
        self.button_check_stim = visual.TextStim(self.win, text="Button check - Please wait")
        image_path = self.stimulus_path+self.test_stimulus_path+self.test_stimulus_file
        self.check_yes_stimulus_left = visual.ImageStim(self.win, units='deg', image=image_path+'2.bmp', size=self.stim_size)
        self.check_yes_stimulus_right = visual.ImageStim(self.win, units='deg', image=image_path+'1.bmp', size=self.stim_size)
        self.check_no_stimulus = visual.ImageStim(self.win, units='deg', image=image_path+'0'+'.bmp', size=self.stim_size)

        # create black background and homogeneous grey stimulus 
        self.homogen_grey = visual.Rect(self.win, units='deg', colorSpace='rgb255', size=self.stim_size, fillColor=self.grey_value, lineColor=self.grey_value)


    def add_button_check(self):
        """
        This adds two trials that are used to check which buttons the participant uses. 
        Helps us later in the analysis to determine if the participant maybe confused the buttons.
        """
        
        # start off with a check for each the yes and the no button
        # randomly determine figure location for the yes check
        figure_location = 'break'

        if random.uniform(1,100) < 50:
            start_yes = True        
            if random.uniform(1,100) < 50:
                figure_location_ID = '2'
                figure_location = 'yes_figure_left' 
            else:
                figure_location_ID = '1'
                figure_location = 'yes_figure_right' 
        else:
            start_yes = False
            figure_location_ID = '0'
            if random.uniform(1,100) < 50:
                figure_location = 'yes_figure_left' 
            else:
                figure_location = 'yes_figure_right' 



        # append a short waiting period in which there is only a blank screen to get ready
        button_check_trial = FGSegTrial(self, 0, 0, self.phase_duration_button_check, self.phase_names_break, 'break', figure_location_ID, figure_location, 0, 0, 0, 0, 0, 0, 'seconds')
        self.trial_list.append(button_check_trial)


    def draw_stimulus(self, phase):
        """
        Depending on what phase we are in, this function draws the apropriate stimulus.
        """


        if self.current_trial.line_length == 'break':
            
            # BREAK
            if phase == 0:
                self.break_stim.draw()

            elif phase == 1:
                self.button_check_stim.draw()

            # short grey screen
            elif phase in [2,4]:
                self.homogen_grey.draw()
                self.fixation_dot_red.draw()
            
            # CHECK YES
            elif phase == 3:
                # draw the stimulus with figure to check the yes response
                if self.current_trial.figure_location_ID == '2':
                    self.check_yes_stimulus_left.draw()
                elif self.current_trial.figure_location_ID == '1':
                    self.check_yes_stimulus_right.draw()
                elif self.current_trial.figure_location_ID == '0':
                    self.check_no_stimulus.draw()
                self.fixation_dot_red.draw()
            # CHECK NO
            elif phase == 5:
                # draw the stimulus that has not been drawn in the first button check
                if self.current_trial.figure_location_ID in ['1', '2']:
                    self.check_no_stimulus.draw()
                elif self.current_trial.figure_location_ID == '0':
                    if self.current_trial.figure_location == 'yes_figure_left':
                        self.check_yes_stimulus_left.draw()
                    elif self.current_trial.figure_location == 'yes_figure_right':
                        self.check_yes_stimulus_right.draw()
                self.fixation_dot_red.draw()
                
        else:

            if phase == 0:
                self.homogen_grey.draw()
                #self.background_list[self.current_trial.trial_nr-1].draw()
                # READY fixation dot in green
                self.fixation_dot_red.draw()
            
            elif phase == 1:
                # draw the line stimulus
                self.stimuli_list[self.current_trial.trial_nr-1].draw()
                # on top of the stimuli draw a red fixation dot     
                self.fixation_dot_red.draw()
            
            elif phase == 2:
                self.homogen_grey.draw()
                #self.background_list[self.current_trial.trial_nr].draw()
                self.fixation_dot_green.draw()

    def run(self):
        print("-------------RUN SESSION---------------")
        
        if self.eyetracker_on:
            self.calibrate_eyetracker()
            self.start_recording_eyetracker()
        
        self.display_text(self.button_instructions, keys='space')
        self.display_text('Please wait', keys='t')

        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        self.kb.clock.reset()
        self.win.color = [0, 0, 0]

        print(f"We have {len(self.trial_list)} trials (with breaks)!")
        
        for trial in self.trial_list:
            self.current_trial = trial
            self.current_trial_start_time = self.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.display_text('End. \n Thank you for participating!', keys='space')
        self.close()






        
