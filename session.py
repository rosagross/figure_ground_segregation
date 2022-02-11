#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/03 13:44:52
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

import numpy as np
import os
from psychopy import visual
from exptools2.core import PylinkEyetrackerSession
from trial import FGSegTrial
from stim import FGSegStim
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

        self.nr_of_trials = self.settings['Task settings']['Number of trials']
        self.line_lengths = self.settings['Task settings']['Line lengths']
        self.break_duration = self.settings['Task settings']['Break duration']
        self.stimulus_duration = self.settings['Task settings']['Stimulus duration']
        self.response_window_duration = self.settings['Task settings']['Response window']
        self.fixation_duration = self.settings['Task settings']['Fixation duration']
        self.phase_duration = [self.fixation_duration, self.stimulus_duration, self.response_window_duration]
        self.phase_names = ["fixation", "stimulus", "response"]
        self.line_orientations = self.settings['Task settings']['Line orientations']
        self.exit_key = self.settings['Task settings']['Exit key']

        self.create_trials()
        self.create_stimuli()



    def create_trials(self):
        """
        Creates the trials with its phase durations and randomization. 
        One trial looks like the following:
        1) 300ms background stimulus only, together with fixation dot 
        2) 300ms figure stimulus (in 40% right/left from fixation, 20% no stimulus)
        3) response window 1200-2200ms
        """

        self.trial_list = []
        # create array with all the line length 
        line_length_list = np.repeat(self.line_lengths, self.nr_of_trials)
        # create array with all figure locations
        figure_locations_list = np.repeat([0,1], self.nr_of_trials*len(self.line_lengths)/2)
        # create array with all line orientations for the background
        line_orientations_list = np.repeat(self.line_orientations, self.nr_of_trials*len(self.line_lengths)/len(self.line_orientations))
        previous_orientation = 0
        for trial_nr in range(len(line_length_list)):

            # randomly draw (we do this by first shuffeling and then picking the first element) line_length 
            np.random.shuffle(line_length_list)
            line_length = line_length_list[0]
            line_length_list = line_length_list[1:]

            # randomly choose figure location 
            np.random.shuffle(figure_locations_list)
            figure_location_ID = figure_locations_list[0]
            figure_location = 'right' if figure_location_ID == 0 else 'left'
            figure_locations_list = figure_locations_list[1:]

            # randomly set the line orientation for the background (it's either 22.58, 67.58, 112.58, or 157.58)
            # check if the orientation was like this before already, then shuffle again!
            while True:
                np.random.shuffle(line_orientations_list)
                line_orientation_ground = line_orientations_list[0]
                if previous_orientation!=line_orientation_ground:
                    break
    
            previous_orientation = line_orientation_ground 
            line_orientations_list = line_orientations_list[1:]

            # determine if the figure is visible in this trial
            # TODO: implement correct randomization 
            figure_visible = True if random.uniform(1,100) < 80 else False
            print('figure visible:', figure_visible)

            # get the phase durations for every trial
            trial = FGSegTrial(self, trial_nr+1, self.phase_duration, self.phase_names, line_length,
                                figure_location, line_orientation=line_orientation_ground,
                                figure_visible=figure_visible)
                                
            self.trial_list.append(trial)


    def create_stimuli(self):

        # fixation dot in red 
        self.fixation_dot = visual.Circle(self.win, 
            radius=0.2, 
            units='deg', lineColor='red', fillColor='red')

        # instantiate the line stimulus
        self.fig_ground_stim = FGSegStim(self, self.line_lengths)


    def draw_stimulus(self, phase):
        """
        Depending on what phase we are in, this function draws the apropriate stimulus.
        """

        if phase == 0:
            self.win.color = [1, 1, 1]
            # in the fixation phase there is only the fixation dot on a blank screen
            self.fixation_dot.draw()
        elif phase == 1:
            print("\nlocation:", self.current_trial.figure_location)
            print("line orientation ground")
            self.fig_ground_stim.draw(position=self.current_trial.figure_location, 
                                        orientation=self.current_trial.line_orientation,
                                        line_length=self.current_trial.line_length,
                                        figure_visible=self.current_trial.figure_visible)
        elif phase == 2:
            self.win.color = [0, 0, 0]
            self.display_text('respond if there was a figure', keys='space')
        #elif phase == 3:
        #    self.display_text('Questionnaire ..', keys='space')


    def run(self):
        print("-------------RUN SESSION---------------")
        
        if self.eyetracker_on:
            self.calibrate_eyetracker()
            self.start_recording_eyetracker()
        
        self.display_text('Press SPACE to start experiment', keys='space')
        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        
        for trial in self.trial_list:
            self.current_trial = trial 
            self.current_trial_start_time = self.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.display_text('End. \n Thank you for participating!', keys='space')
        self.close()






        
