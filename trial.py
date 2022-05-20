#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/03 13:45:26
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''


from matplotlib.pyplot import figure
from psychopy import event
import numpy as np
from exptools2.core.trial import Trial
import os
opj = os.path.join


class FGSegTrial(Trial):
    """ 
    This class implements how a trial looks like in the experiment and 
    also handles keyboard responses.  
    """

    def __init__(self, session, trial_nr, block_nr, phase_duration, phase_names, line_length, figure_location_ID, figure_location, repetition, line_orientation,
                position_noise, line_spacing, line_width, response_window_dur, timing, *args, **kwargs):
        
        super().__init__(session, trial_nr, phase_duration, phase_names,
                         parameters={'line_length': line_length,
                                     'trial_nr': trial_nr,
                                     'block_nr': block_nr,
                                     'figure_location_ID': figure_location_ID, 
                                     'figure_location': figure_location,
                                     'line_orientation' : line_orientation,
                                     'repetition' : repetition,
                                     'position_noise' : position_noise,
                                     'line_spacing' : line_spacing,
                                     'line_width' : line_width,
                                     'response_window_duration' : response_window_dur},
                         verbose=False, timing=timing, *args, **kwargs)
        
        # store if it is a rivalry trial or unambiguous trial 
        self.ID = trial_nr
        self.line_length = line_length
        self.figure_location_ID = figure_location_ID
        self.figure_location = figure_location
        self.line_orientation = line_orientation
        self.line_length = line_length # this should be in pixels!
        self.repetition = repetition
        self.phase_duration = phase_duration
        self.position_noise = position_noise
        self.line_spacing = line_spacing
        self.line_width = line_width
        self.response_window_dur = response_window_dur        
        self.pause_switch = False
            
    def draw(self):
        ''' 
        This tells what happens in the trial, and this is defined in the session itself. 
        Since this is dependent on the phase of the trial, self.phase (which is an attribute of the
        trial instance defined in the parent class) is used as parameter.
        '''
        self.session.draw_stimulus(self.phase)


    def get_events(self):
        """ Logs responses/triggers """
        
        keys = self.session.kb.getKeys(waitRelease=True)
        for thisKey in keys:

            if thisKey.name==self.session.exit_key:  # it is equivalent to the string 'q'
                print("End experiment!")
                if self.session.settings['Task settings']['Screenshot']==True:
                    print('\nSCREENSHOT\n')
                    self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+'_Screenshot.png'))
                self.session.close()
                self.session.quit()
            elif (thisKey=='s') & (self.session.settings['Task settings']['Screenshot']==True):
                self.session.win.getMovieFrame()
                self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+f'_Screenshot_{self.figure_location_ID}.png'))
            else:
                print(thisKey.name, thisKey.tDown, thisKey.rt)
                t = thisKey.rt
                idx = self.session.global_log.shape[0]     
                event_type = self.figure_location    
                 

                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr   
                self.session.global_log.loc[idx, 'response'] = thisKey.name
                self.session.global_log.loc[idx, 'button_encoding'] = self.session.response_button
                self.session.global_log.loc[idx, 'event_type'] = 'button_press'
                self.session.global_log.loc[idx, 'onset'] = t
                self.session.global_log.loc[idx, 'line_orientation'] = self.line_orientation
                self.session.global_log.loc[idx, 'figure_location'] = self.figure_location
                self.session.global_log.loc[idx, 'response_window_duration'] = self.response_window_dur
                self.session.global_log.loc[idx, 'nr_frames'] = 0
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'position_noise'] = self.position_noise
                self.session.global_log.loc[idx, 'line_spacing'] = self.line_spacing
                self.session.global_log.loc[idx, 'line_width'] = self.line_width
                

                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

                if self.eyetracker_on:  # send message to eyetracker
                            msg = f'start_type-{event_type}_trial-{self.trial_nr}_phase-{self.phase}_key-{thisKey.name}_time-{t}_duration-{thisKey.duration}'
                            self.session.tracker.sendMessage(msg)

                if thisKey.name in self.session.break_buttons:
                    print('NEXT PHASE')
                    self.exit_phase = True

                if thisKey.name == 'p':
                    input('PAUSE. Press enter to continue.')

