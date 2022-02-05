#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/03 16:54:41
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

import numpy as np
from psychopy import visual
from psychopy import tools


class FGSegStim(object):  

    def __init__(self, session, tex_nr_pix=2048, **kwargs):

        self.session = session
        self.tex_nr_pix = tex_nr_pix

        self.setup_stimulus()


    def setup_stimulus(self):
        """ 
        Uses attributes of the FGSeg instance to construct the stimulus.
        """

        self.line_stim = visual.Line(self.session.win, units='pixels', lineColor='black')


    def draw(self, orientation, position, line_length, figure_visible):
        """
        This function finally draws the stimulus (it is called in the session instance, after the trial called
        its draw method).
        """
        
        # set all the parameters for the lines (the same for all lines)
        size = (line_length*0.5, line_length*5)
        
        

        if figure_visible:
            # determine the position of the square (centre)
            if position == 'left':
                x_pos, y_pos = (-100, 0)
            else:
                x_pos, y_pos = (100, 0)

            # TODO
            # determine the size of the square 

            # draw the square stimulus (this should actually happen AFTER drawing the background stimulus)
            
        # if the figure should not be displayed just show the background stimulus
        else: 
            x_pos, y_pos = [100, 100]
            self.line_stim.setSize(size)
            self.line_stim.setPos([x_pos, y_pos])
            self.line_stim.setOri(orientation)
        
        self.line_stim.draw()



