#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 10:17:15 2019

@author: gtucker
"""

import os
import sys
import numpy as np
from numpy.testing import assert_raises, assert_array_equal, assert_array_almost_equal
from landlab.io import write_esri_ascii
from landlab import RasterModelGrid

sys.path.append(os.path.abspath('..'))
from lakeflexer import LakeFlexer


def make_test_dem_with_line_load():
    """Make a 13x13 DEM with all elevation s at 10 m except a column down the
    middle where elevation is -10.0 m."""
    grid = RasterModelGrid((13, 13), xy_spacing=10000.0)
    dem = grid.add_zeros('node', 'topographic__elevation')
    dem[:] = 10.0
    dem[grid.x_of_node > 50000.0] = -10.0
    dem[grid.x_of_node > 60000.0] = 10.0
    return grid


def write_test_parameter_file(filename):

    f = open(filename, 'w')
    f.write('dem_filename: test_dem.asc\n')
    f.write('water_surface_elevation: 0.0\n')
    f.write('elastic_thickness: 3266.\n')
    f.write('youngs_modulus: 7.0e10\n')
    f.write('mantle_density: 3300.0\n')
    f.write('gravitational_acceleration: 10.0\n')
    f.write('lake_water_density: 1000.0\n')
    f.close()


def test_lake_flexer_with_line_load():
    """Test with a line-like load.
    """
    dem_filename = 'test_dem.asc'
    param_filename = 'test_params.txt'
    
    # Create test grid, DEM, and input file
    test_grid = make_test_dem_with_line_load()
    write_esri_ascii(dem_filename, test_grid)
    write_test_parameter_file(param_filename)

    # Create LakeFlexer
    lf = LakeFlexer()
    
    # Test that it fails if update() is run before initialization
    assert_raises(RuntimeError, lf.update)

    lf.initialize(param_filename)
    
    os.remove(dem_filename)
    os.remove(param_filename)

    lf.update()
    lf.finalize()

    deflection = lf.grid.at_node['lithosphere_surface__elevation_increment']
    assert_array_almost_equal(deflection[78:91],
                       np.array([ -1.117830e-02,  -3.394216e-02,
                                  -5.237843e-02,  -8.787396e-04,
                                   2.468120e-01,   7.672625e-01,
                                   1.201217e+00,   7.672625e-01,
                                   2.468120e-01,  -8.787396e-04,
                                  -5.237843e-02,  -3.394216e-02,
                                  -1.117830e-02]))


