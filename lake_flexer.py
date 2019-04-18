#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 10:17:01 2019

@author: gtucker
"""

from landlab import load_params
from landlab.components import Flexure
from landlab.io import read_esri_ascii



class LakeFlexer():
    """Calculate elastic lithosphere flexure for a (paleo)lake.

    Landlab-built model that takes a digital elevation model and a target
    water-surface elevation, and calculates flexure resulting from the load of
    the water.
    """

    def __init__(self, param_filename=None):
        
        if param_filename is None:
            self.initialized = False
        else:
            self.initialize(param_filename)

    def initialize(self, param_filename):

        # Read parameters from input file
        params = load_params(param_filename)
        self.elastic_thickness = params['elastic_thickness']
        self.youngs_modulus = params['youngs_modulus']
        self.rho_m = params['mantle_density']
        self.grav_accel = params['gravitational_acceleration']
        self.water_surf_elev = params['water_surface_elevation']
        self.water_density = params['lake_water_density']

        # Read DEM
        (self.grid, self.dem) = read_esri_ascii(params['dem_filename'])

        # Create and initialize Flexure component
        self.flexer = Flexure(self.grid, eet=self.elastic_thickness,
                              youngs=self.youngs_modulus, method="flexure",
                              rho_mantle=self.rho_m, gravity=self.grav_accel)
        print('alpha = ' + str(self.flexer.alpha))
        print('3/4 pi alpha = ' + str(0.75 * 3.1415926 * self.flexer.alpha))
        print('pi alpha = ' + str(3.1415926 * self.flexer.alpha))
        self.load = self.grid.at_node['lithosphere__overlying_pressure_increment']

        # (more to be added here?)

        self.initialized = True
        
    def update(self):

        # Make sure model has been initialized
        try:
            if self.initialized == False:
                raise RuntimeError('LakeFlexer must be initialized before'
                                   + 'calling update()')
        except RuntimeError:
            raise

        # Calculate water depths
        self.water_depth = self.water_surf_elev - self.dem
        self.water_depth[self.water_depth < 0.0] = 0.0

        # Calculate loads
        self.load[:] = self.water_density * self.grav_accel * self.water_depth

        # Calculate flexure
        self.flexer.update()

    def finalize(self):
        print(self.grid.at_node['lithosphere_surface__elevation_increment'].reshape((13, 13)))
