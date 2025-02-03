import numpy as np

from calculations import *


def get_adiabatic_data(adiabatic_index: float, initial_pressure: float, initial_volume: float, final_volume: float) -> tuple[list[float], list[float]]:
    """
    Get the data for the first and thrid stages of the Otto cycle (Adiabatic Compression and Adiabatic Expansion)
    """
    # Calculate the step size to split the volume into 1000 parts 
    step_size = (final_volume - initial_volume) * (10 ** (-3))
    
    
    # Create a list of volumes from the initial volume to the final volume
    volumes = [float(volume) for volume in np.arange(initial_volume, final_volume, step_size)]
    
    # Calculate the pressures for each volume
    pressures = [calculate_pressure_adiabatic(adiabatic_index, initial_pressure, initial_volume, volume) for volume in volumes]
    
    
    # Convert the volumes from cubic feet to cubic inches
    volumes = [convert_cubic_feet_to_cubic_inches(volume) for volume in volumes]
    
    # Convert the pressures from psf to psi
    pressures = [convert_psf_to_psi(pressure) for pressure in pressures]
    
    return (volumes, pressures)