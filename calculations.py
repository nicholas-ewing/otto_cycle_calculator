def convert_rankine_to_farhenheit(temperature: float) -> float:
    return temperature - 459.67

def convert_farhenheit_to_rankine(temperature: float) -> float:
    return temperature + 459.67

def convert_psi_to_psf(pressure: float) -> float:
    return pressure * 144

def convert_psf_to_psi(pressure: float) -> float:
    return pressure / 144

def convert_cubic_inches_to_cubic_feet(volume: float) -> float:
    return volume / 1728

def convert_cubic_feet_to_cubic_inches(volume: float) -> float:
    return volume * 1728

def convert_btu_to_ft_lbf(energy: float) -> float:
    return energy * 778.17

def convert_ft_lbf_to_btu(energy: float) -> float:
    return energy / 778.17

def calculate_adiabatic_index(specific_heat_pressure: float, specific_heat_volume: float) -> float | None:
    try:
        return (specific_heat_pressure / specific_heat_volume)
    except (ZeroDivisionError, TypeError):
        return None

def calculate_initial_volume(compression_ratio: float, engine_displacement: float) -> float:
    return (engine_displacement / (1 - (1 / compression_ratio)))

def calculate_air_mass(initial_pressure: float, initial_temperature: float, initial_volume: float, gas_constant: float) -> float:
    return ((initial_pressure * initial_volume) / (gas_constant * initial_temperature))

def calculate_final_pressure_adiabatic(compression_ratio: float, adiabatic_index: float, initial_pressure: float, compression: bool = True) -> float:
    if compression:
        return (initial_pressure * (compression_ratio ** adiabatic_index))
    return (initial_pressure * ((1 / compression_ratio) ** adiabatic_index))

def calculate_pressure_adiabatic(adiabatic_index: float, initial_pressure: float, initial_volume: float, final_volume: float) -> float:
    return (initial_pressure * ((initial_volume / final_volume) ** adiabatic_index))

def calculate_final_temperature_adiabatic(compression_ratio: float, adiabatic_index: float, initial_temperature: float, compression: bool = True) -> float:
    if compression:
        return ((initial_temperature * (compression_ratio ** (adiabatic_index - 1))))
    return ((initial_temperature * ((1 / compression_ratio) ** (adiabatic_index - 1))))

def calculate_final_volume(compression_ratio: float, initial_volume: float) -> float:
    return (initial_volume / compression_ratio)

def calculate_work_adiabatic(adiabatic_index: float, initial_pressure: float, initial_volume: float, final_pressure: float, final_volume: float) -> float:
    return (((final_pressure * final_volume) - (initial_pressure * initial_volume)) / (1 - adiabatic_index))

def calculate_final_pressure_constant_volume(initial_pressure: float, final_temperature: float, initial_temperature: float) -> float:
    return (initial_pressure * (final_temperature / initial_temperature))

def calculate_heat(specific_heat_volume: float, mass: float, final_temperature: float, initial_temperature: float) -> float:
    return (specific_heat_volume * mass * (final_temperature - initial_temperature))

def calculate_total_work(*works: float) -> float:
    return sum(works)

def calculate_thermal_efficiency(total_work: float, heat_added: float) -> float:
    return (total_work / heat_added)