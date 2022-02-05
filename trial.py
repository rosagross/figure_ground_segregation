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

    def __init__(self, session, trial_nr, phase_duration, phase_names, line_length, figure_location, line_orientation, figure_visible, *args, **kwargs):
        
        super().__init__(session, trial_nr, phase_duration, phase_names,
                         parameters={'line_length': line_length,
                                     'figure_location': figure_location, 
                                     'phase_duration' : phase_duration,
                                     'orientation_ground' : line_orientation},
                         verbose=False, *args, **kwargs)
        
        # store if it is a rivalry trial or unambiguous trial 
        self.ID = trial_nr
        self.line_length = line_length
        self.figure_location = figure_location # this can be either left or right
        self.line_orientation = line_orientation
        self.line_length = line_length # this should be in pixels!
        self.figure_visible = figure_visible
        
            
    def draw(self):
        ''' 
        This tells what happens in the trial, and this is defined in the session itself. 
        Since this is dependent on the phase of the trail, self.phase (which is an attribute of the
        trial instance defined in the parent class) is used as parameter.
        '''
        
        self.session.draw_stimulus(self.phase)


    def get_events(self):
        """ Logs responses/triggers """
        
        events = event.getKeys(timeStamped=self.session.clock)
        if events:
            if self.session.exit_key in [ev[0] for ev in events]: 
                print("End experiment!")

                if self.session.settings['Task settings']['Screenshot']==True:
                    print('\nSCREENSHOT\n')
                    self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+'_Screenshot.png'))
                self.session.close()
                self.session.quit()
