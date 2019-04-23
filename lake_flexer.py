#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 10:17:01 2019

@author: gtucker
"""

from landlab import load_params
from landlab.components import Flexure
from landlab.io import read_esri_ascii
from landlab.io.netcdf import write_netcdf
import numpy as np

MAX_ITERATIONS = 100


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
        self.tolerance = params['lake_elev_tolerance']

        # Read DEM
        (self.grid, self.dem) = read_esri_ascii(params['dem_filename'])
        
        # Store a copy that we'll modify
        self.flexed_dem = self.dem.copy()

        # Create and initialize Flexure component
        self.flexer = Flexure(self.grid, eet=self.elastic_thickness,
                              youngs=self.youngs_modulus, method="flexure",
                              rho_mantle=self.rho_m, gravity=self.grav_accel)
        self.load = self.grid.at_node['lithosphere__overlying_pressure_increment']
        self.deflection = self.grid.at_node['lithosphere_surface__elevation_increment']

        self.initialized = True

    def update(self):

        # Make sure model has been initialized
        try:
            if self.initialized == False:
                raise RuntimeError('LakeFlexer must be initialized before'
                                   + 'calling update()')
        except RuntimeError:
            raise

        i = 0
        done = False
        while not done:

            # Calculate water depths
            self.water_depth = self.water_surf_elev - self.flexed_dem
            self.water_depth[self.water_depth < 0.0] = 0.0

            # Calculate loads
            self.load[:] = self.water_density * self.grav_accel * self.water_depth

            # Calculate flexure and adjust elevations
            self.flexer.update()
            self.flexed_dem = self.dem - self.deflection

            # Compare modeled and desired water-surface elevations
            flexed_wse = (self.flexed_dem[self.water_depth > 0.0]
                          + self.water_depth[self.water_depth > 0.0])
            residual = self.water_surf_elev - flexed_wse
            if np.amax(np.abs(residual)) < self.tolerance:
                done = True

            i += 1
            if i > MAX_ITERATIONS:
                print('Warning: maximum number of iterations exceeded')
                done = True

    def finalize(self):
        """Output data to file."""
        write_netcdf("lake_flex.nc", self.grid)