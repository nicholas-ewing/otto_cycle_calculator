from __future__ import annotations
import datetime as dt
from pathlib import Path
from typing import Any

from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from calculations import *
from file_path import get_file_path
from graph import get_adiabatic_data


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_version: str | None) -> None:
        super().__init__()
        
        self._app_version = app_version
        
        self.calculated = False
        
        # Inputs
        self.compression_ratio: float | None = None
        self.specific_heat_pressure: float | None = None
        self.specific_heat_volume: float | None = None
        self.gas_constant: float | None = None
        self.engine_displacement: float | None = None
        self.initial_pressure: float | None = None
        self.initial_temperature: float | None = None
        self.operating_temperature: float | None = None
        
        # Outputs
        self.air_mass: float | None = None
        self.total_work: float | None = None
        self.thermal_efficiency: float | None = None
        self.adiabatic_index: float | None = None
        
        self.initial_volume: float | None = None
        self.stage_1_work: float | None = None
        self.stage_1_final_pressure: float | None = None
        self.stage_1_final_temperature: float | None = None
        self.stage_1_final_volume: float | None = None
        
        self.stage_2_final_pressure: float | None = None
        self.stage_2_heat: float | None = None
        
        self.stage_3_work: float | None = None
        self.stage_3_final_pressure: float | None = None
        self.stage_3_final_temperature: float | None = None
        
        self.stage_4_heat: float | None = None
        
        self.setup_ui()
        
        self.graph_window: pg.PlotWidget | None = None
        
        self.inputs = self.add_inputs()
        self.outputs = self.add_outputs()
        
        self.set_input_defaults()
        
    def setup_ui(self) -> None:
        self.setMinimumSize(QtCore.QSize(1160, 900))
        self.resize(1160, 900)
        
        if self._app_version is not None:
            self.setWindowTitle(f"Otto Cycle Calculator {self._app_version}")
        else:
            self.setWindowTitle("Otto Cycle Calculator")
        self.setWindowIcon(QtGui.QIcon(get_file_path("assets/Trine.ico")))
        
        self.setStyleSheet("QGroupBox { font-size: 10pt; }")
        
        self.central_widget = QtWidgets.QWidget(self)
        
        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        
        self.setCentralWidget(self.central_widget)
        
        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)
        
        self.file_menu = QtWidgets.QMenu(self.menubar)
        self.file_menu.setTitle("File")
        
        self.save_results_action = QtGui.QAction(self)
        self.save_results_action.setText("Save Results")
        self.save_results_action.setShortcut("Ctrl+S")
        self.save_results_action.setDisabled(True)
        
        self.file_menu.addAction(self.save_results_action)
        
        self.menubar.addAction(self.file_menu.menuAction())
        
        self.output_groupbox = QtWidgets.QGroupBox(self.central_widget)
        self.output_groupbox.setTitle("Output")
        self.output_groupbox_layout = QtWidgets.QVBoxLayout(self.output_groupbox)
        self.output_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.general_groupbox = QtWidgets.QGroupBox(self.output_groupbox)
        self.general_groupbox.setTitle("General")
        self.general_groupbox.setMaximumHeight(90)
        self.general_groupbox_layout = QtWidgets.QGridLayout(self.general_groupbox)
        self.general_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.stage_1_2_groupbox = QtWidgets.QGroupBox(self.output_groupbox)
        self.stage_1_2_groupbox.setTitle("Stage 1 -> 2 (Adiabatic Compression)")
        self.stage_1_2_groupbox_layout = QtWidgets.QGridLayout(self.stage_1_2_groupbox)
        self.stage_1_2_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.stage_2_3_groupbox = QtWidgets.QGroupBox(self.output_groupbox)
        self.stage_2_3_groupbox.setTitle("Stage 2 -> 3 (Combustion)")
        self.stage_2_3_groupbox_layout = QtWidgets.QGridLayout(self.stage_2_3_groupbox)
        self.stage_2_3_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.stage_3_4_groupbox = QtWidgets.QGroupBox(self.output_groupbox)
        self.stage_3_4_groupbox.setTitle("Stage 3 -> 4 (Adiabatic Expansion)")
        self.stage_3_4_groupbox_layout = QtWidgets.QGridLayout(self.stage_3_4_groupbox)
        self.stage_3_4_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.stage_4_1_groupbox = QtWidgets.QGroupBox(self.output_groupbox)
        self.stage_4_1_groupbox.setTitle("Stage 4 -> 1 (Heat Rejection)")
        self.stage_4_1_groupbox_layout = QtWidgets.QGridLayout(self.stage_4_1_groupbox)
        self.stage_4_1_groupbox_layout.setContentsMargins(4, 4, 4, 4)

        self.output_groupbox_layout.addWidget(self.general_groupbox)
        self.output_groupbox_layout.addWidget(self.stage_1_2_groupbox)
        self.output_groupbox_layout.addWidget(self.stage_2_3_groupbox)
        self.output_groupbox_layout.addWidget(self.stage_3_4_groupbox)
        self.output_groupbox_layout.addWidget(self.stage_4_1_groupbox)
        
        self.vertial_line = QtWidgets.QFrame(self.central_widget)
        self.vertial_line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.vertial_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        
        self.input_groupbox = QtWidgets.QGroupBox(self.central_widget)
        self.input_groupbox.setTitle("Input")
        self.input_groupbox.setMaximumWidth(360)
        self.input_groupbox_layout = QtWidgets.QVBoxLayout(self.input_groupbox)
        self.input_groupbox_layout.setContentsMargins(4, 4, 4, 4)
        
        self.calculate_button = QtWidgets.QPushButton(self.central_widget)
        self.calculate_button.setMaximumWidth(175)
        self.calculate_button.setText("Calculate")
        
        self.graph_button = QtWidgets.QPushButton(self.central_widget)
        self.graph_button.setMaximumWidth(175)
        self.graph_button.setText("Graph")
        self.graph_button.setDisabled(True)
        
        self.reset_inputs_button = QtWidgets.QPushButton(self.input_groupbox)
        self.reset_inputs_button.setMaximumWidth(175)
        self.reset_inputs_button.setText("Reset Inputs")
        
        self.clear_output_button = QtWidgets.QPushButton(self.central_widget)
        self.clear_output_button.setMaximumWidth(175)
        self.clear_output_button.setText("Clear Output")
        
        self.attribution_label = QtWidgets.QLabel(self.central_widget)
        self.attribution_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.attribution_label.setText("<a href=\"https://nicholasewing.dev\" style=\"color: gray; font-size: 8pt; text-decoration: none;\" target=\"_blank\">© 2025 Nicholas Ewing. All rights reserved.</a>")
        self.attribution_label.setOpenExternalLinks(True)
        
        self.grid_layout.addWidget(self.output_groupbox, 0, 0, 3, 1)
        self.grid_layout.addWidget(self.attribution_label, 3, 0, 1, 1)
        self.grid_layout.addWidget(self.vertial_line, 0, 1, 4, 1)
        self.grid_layout.addWidget(self.input_groupbox, 0, 2, 2, 2)
        self.grid_layout.addWidget(self.calculate_button, 2, 2, 1, 1)
        self.grid_layout.addWidget(self.graph_button, 2, 3, 1, 1)
        self.grid_layout.addWidget(self.clear_output_button, 3, 2, 1, 1)
        self.grid_layout.addWidget(self.reset_inputs_button, 3, 3, 1, 1)
        
        self.save_results_action.triggered.connect(self.handle_save_results_action)
        self.calculate_button.clicked.connect(self.handle_calculate_button)
        self.graph_button.clicked.connect(self.handle_graph_button)
        self.clear_output_button.clicked.connect(self.handle_clear_output_button)
        self.reset_inputs_button.clicked.connect(self.handle_reset_inputs_button)
    
    def add_inputs(self) -> list[ValueWidget]:
        self.compression_ratio_input = ValueWidget(parent=self.input_groupbox, label_text="Compression Ratio (CR)", editable=True)
        self.specific_heat_pressure_input = ValueWidget(parent=self.input_groupbox, label_text="Specific Heat at Constant Pressure (C_p)", decimals=3, suffix="Btu/lb-°R", editable=True)
        self.specific_heat_volume_input = ValueWidget(parent=self.input_groupbox, label_text="Specific Heat at Constant Volume (C_v)", decimals=3, suffix="Btu/lb-°R", editable=True)
        self.adiabatic_index_display = ValueWidget(parent=self.input_groupbox, label_text="Adiabatic Index (k)", decimals=4, editable=False)
        self.gas_constant_input = ValueWidget(parent=self.input_groupbox, label_text="Gas Constant (R)", decimals=4, suffix="lbf-ft/lbm-°R", editable=True)
        self.engine_displacement_input = ValueWidget(parent=self.input_groupbox, label_text="Engine Displacement (ΔV)", suffix="in^3", editable=True)
        self.initial_pressure_input = ValueWidget(parent=self.input_groupbox, label_text="Initial Pressure (P_1)", suffix="psi", editable=True)
        self.initial_temperature_input = ValueWidget(parent=self.input_groupbox, label_text="Initial Temperature (T_1)", suffix="°F", editable=True)
        self.operating_temperature_input = ValueWidget(parent=self.input_groupbox, label_text="Operating Temperature (T_3)", suffix="°F", editable=True)
        
        self.compression_ratio_input.tie_change_function(self.handle_compression_ratio_change)
        self.specific_heat_pressure_input.tie_change_function(self.handle_specific_heat_pressure_change)
        self.specific_heat_volume_input.tie_change_function(self.handle_specific_heat_volume_change)
        self.gas_constant_input.tie_change_function(self.handle_gas_constant_change)
        self.engine_displacement_input.tie_change_function(self.handle_engine_displacement_change)
        self.initial_pressure_input.tie_change_function(self.handle_initial_pressure_change)
        self.initial_temperature_input.tie_change_function(self.handle_initial_temeprature_change)
        self.operating_temperature_input.tie_change_function(self.handle_operating_temperature_change)
        
        self.inputs = [
            self.compression_ratio_input,
            self.specific_heat_pressure_input,
            self.specific_heat_volume_input,
            self.adiabatic_index_display,
            self.gas_constant_input,
            self.engine_displacement_input,
            self.initial_pressure_input,
            self.initial_temperature_input,
            self.operating_temperature_input
        ]
        
        for input_widget in self.inputs:
            self.input_groupbox_layout.addWidget(input_widget)
        
        return self.inputs
            

    def add_outputs(self) -> list[ValueWidget]:
        
        # General
        self.air_mass_display = ValueWidget(parent=self.general_groupbox, label_text="Air Mass (m_air)", decimals=4, suffix="lbm", editable=False)
        self.total_work_display = ValueWidget(parent=self.general_groupbox, label_text="Total Work (Work_total)", suffix="Btu", editable=False)
        self.thermal_efficiency_display = ValueWidget(parent=self.general_groupbox, label_text="Thermal Efficiency (Efficiency)", decimals=2, suffix="%", editable=False)
        
        self.general_groupbox_layout.addWidget(self.air_mass_display, 0, 0, 1, 1)
        self.general_groupbox_layout.addWidget(self.total_work_display, 0, 1, 1, 1)
        self.general_groupbox_layout.addWidget(self.thermal_efficiency_display, 0, 2, 1, 1)
        
        # Stage 1 -> 2
        self.stage_1_initial_pressure_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Initial Pressure (P_1)", suffix="psi", editable=False)
        self.stage_1_initial_temperature_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Initial Temperature (T_1)", suffix="°F", editable=False)
        self.stage_1_initial_volume_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Initial Volume (V_1)", suffix="in^3", editable=False)
        self.stage_1_final_pressure_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Final Pressure (P_2)", suffix="psi", editable=False)
        self.stage_1_final_temperature_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Final Temperature (T_2)", suffix="°F", editable=False)
        self.stage_1_final_volume_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Final Volume (V_2)", suffix="in^3", editable=False)
        self.stage_1_heat_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Heat (Q_1)", decimals=0, suffix="Btu", editable=False)
        self.stage_1_work_display = ValueWidget(parent=self.stage_1_2_groupbox, label_text="Work (Work_1)", suffix="Btu", editable=False)
        
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_initial_pressure_display, 0, 0, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_initial_temperature_display, 1, 0, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_initial_volume_display, 2, 0, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_final_pressure_display, 0, 1, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_final_temperature_display, 1, 1, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_final_volume_display, 2, 1, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_heat_display, 0, 2, 1, 1)
        self.stage_1_2_groupbox_layout.addWidget(self.stage_1_work_display, 1, 2, 1, 1)
        
        # Stage 2 -> 3
        self.stage_2_initial_pressure_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Initial Pressure (P_2)", suffix="psi", editable=False)
        self.stage_2_initial_temperature_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Initial Temperature (T_2)", suffix="°F", editable=False)
        self.stage_2_initial_volume_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Initial Volume (V_2)", suffix="in^3", editable=False)
        self.stage_2_final_pressure_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Final Pressure (P_3)", suffix="psi", editable=False)
        self.stage_2_final_temperature_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Final Temperature (T_3)", suffix="°F", editable=False)
        self.stage_2_final_volume_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Final Volume (V_3)", suffix="in^3", editable=False)
        self.stage_2_heat_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Heat (Q_2)", suffix="Btu", editable=False)
        self.stage_2_work_display = ValueWidget(parent=self.stage_2_3_groupbox, label_text="Work (Work_2)", suffix="Btu", editable=False)
        
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_initial_pressure_display, 0, 0, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_initial_temperature_display, 1, 0, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_initial_volume_display, 2, 0, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_final_pressure_display, 0, 1, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_final_temperature_display, 1, 1, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_final_volume_display, 2, 1, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_heat_display, 0, 2, 1, 1)
        self.stage_2_3_groupbox_layout.addWidget(self.stage_2_work_display, 1, 2, 1, 1)
        
        # Stage 3 -> 4
        self.stage_3_initial_pressure_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Initial Pressure (P_3)", suffix="psi", editable=False)
        self.stage_3_initial_temperature_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Initial Temperature (T_3)", suffix="°F", editable=False)
        self.stage_3_initial_volume_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Initial Volume (V_3)", suffix="in^3", editable=False)
        self.stage_3_final_pressure_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Final Pressure (P_4)", suffix="psi", editable=False)
        self.stage_3_final_temperature_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Final Temperature (T_4)", suffix="°F", editable=False)
        self.stage_3_final_volume_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Final Volume (V_4)", suffix="in^3", editable=False)
        self.stage_3_heat_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Heat (Q_3)", decimals=0, suffix="Btu", editable=False)
        self.stage_3_work_display = ValueWidget(parent=self.stage_3_4_groupbox, label_text="Work (Work_3)", suffix="Btu", editable=False)
        
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_initial_pressure_display, 0, 0, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_initial_temperature_display, 1, 0, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_initial_volume_display, 2, 0, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_final_pressure_display, 0, 1, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_final_temperature_display, 1, 1, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_final_volume_display, 2, 1, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_heat_display, 0, 2, 1, 1)
        self.stage_3_4_groupbox_layout.addWidget(self.stage_3_work_display, 1, 2, 1, 1)
        
        # Stage 4 -> 1
        self.stage_4_initial_pressure_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Initial Pressure (P_4)", suffix="psi", editable=False)
        self.stage_4_initial_temperature_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Initial Temperature (T_4)", suffix="°F", editable=False)
        self.stage_4_initial_volume_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Initial Volume (V_4)", suffix="in^3", editable=False)
        self.stage_4_final_pressure_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Final Pressure (P_1)", suffix="psi", editable=False)
        self.stage_4_final_temperature_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Final Temperature (T_1)", suffix="°F", editable=False)
        self.stage_4_final_volume_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Final Volume (V_1)", suffix="in^3", editable=False)
        self.stage_4_heat_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Heat (Q_4)", suffix="Btu", editable=False)
        self.stage_4_work_display = ValueWidget(parent=self.stage_4_1_groupbox, label_text="Work (Work_4)", suffix="Btu", editable=False)
        
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_initial_pressure_display, 0, 0, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_initial_temperature_display, 1, 0, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_initial_volume_display, 2, 0, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_final_pressure_display, 0, 1, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_final_temperature_display, 1, 1, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_final_volume_display, 2, 1, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_heat_display, 0, 2, 1, 1)
        self.stage_4_1_groupbox_layout.addWidget(self.stage_4_work_display, 1, 2, 1, 1)
        
        self.outputs = [
            self.air_mass_display,
            self.total_work_display,
            self.thermal_efficiency_display,
            self.stage_1_initial_pressure_display,
            self.stage_1_initial_temperature_display,
            self.stage_1_initial_volume_display,
            self.stage_1_final_pressure_display,
            self.stage_1_final_temperature_display,
            self.stage_1_final_volume_display,
            self.stage_1_heat_display,
            self.stage_1_work_display,
            self.stage_2_initial_pressure_display,
            self.stage_2_initial_temperature_display,
            self.stage_2_initial_volume_display,
            self.stage_2_final_pressure_display,
            self.stage_2_final_temperature_display,
            self.stage_2_final_volume_display,
            self.stage_2_heat_display,
            self.stage_2_work_display,
            self.stage_3_initial_pressure_display,
            self.stage_3_initial_temperature_display,
            self.stage_3_initial_volume_display,
            self.stage_3_final_pressure_display,
            self.stage_3_final_temperature_display,
            self.stage_3_final_volume_display,
            self.stage_3_heat_display,
            self.stage_3_work_display,
            self.stage_4_initial_pressure_display,
            self.stage_4_initial_temperature_display,
            self.stage_4_initial_volume_display,
            self.stage_4_final_pressure_display,
            self.stage_4_final_temperature_display,
            self.stage_4_final_volume_display,
            self.stage_4_heat_display,
            self.stage_4_work_display
        ]
        
        return self.outputs
        
    
    def handle_compression_ratio_change(self, new_value: float) -> None:
        self.compression_ratio = new_value
    
    def handle_specific_heat_pressure_change(self, new_value: float) -> None:
        self.specific_heat_pressure = new_value
        
        self.adiabatic_index = calculate_adiabatic_index(self.specific_heat_pressure, self.specific_heat_volume)
        if self.adiabatic_index is not None:
            self.adiabatic_index_display.value = self.adiabatic_index
    
    def handle_specific_heat_volume_change(self, new_value: float) -> None:
        self.specific_heat_volume = new_value
        
        self.adiabatic_index = calculate_adiabatic_index(self.specific_heat_pressure, self.specific_heat_volume)
        if self.adiabatic_index is not None:
            self.adiabatic_index_display.value = self.adiabatic_index
    
    def handle_gas_constant_change(self, new_value: float) -> None:
        self.gas_constant = new_value
    
    def handle_engine_displacement_change(self, new_value: float) -> None:
        self.engine_displacement = new_value
    
    def handle_initial_pressure_change(self, new_value: float) -> None:
        self.initial_pressure = new_value
    
    def handle_initial_temeprature_change(self, new_value: float) -> None:
        self.initial_temperature = new_value
    
    def handle_operating_temperature_change(self, new_value: float) -> None:
        self.operating_temperature = new_value
    
    def set_input_defaults(self) -> None:
        self.compression_ratio_input.value = 8
        self.specific_heat_pressure_input.value = .24
        self.specific_heat_volume_input.value = .17
        self.gas_constant_input.value = 53.3
        self.engine_displacement_input.value = 258
        self.initial_pressure_input.value = 14.7
        self.initial_temperature_input.value = 70
        self.operating_temperature_input.value = convert_rankine_to_farhenheit(4130)
        
    def refresh_output_display(self, clear: bool = False) -> None:
        if clear:
            for output in self.outputs:
                output.value = 0
            return
        
        self.air_mass_display.value = self.air_mass
        self.total_work_display.value = self.total_work
        self.thermal_efficiency_display.value = (self.thermal_efficiency * 100)

        self.stage_1_initial_pressure_display.value = self.initial_pressure
        self.stage_1_initial_temperature_display.value = self.initial_temperature
        self.stage_1_initial_volume_display.value = self.initial_volume
        self.stage_1_final_pressure_display.value = self.stage_1_final_pressure
        self.stage_1_final_temperature_display.value = self.stage_1_final_temperature
        self.stage_1_final_volume_display.value = self.stage_1_final_volume
        self.stage_1_work_display.value = self.stage_1_work
        
        self.stage_2_initial_pressure_display.value = self.stage_1_final_pressure
        self.stage_2_initial_temperature_display.value = self.stage_1_final_temperature
        self.stage_2_initial_volume_display.value = self.stage_1_final_volume
        self.stage_2_final_pressure_display.value = self.stage_2_final_pressure
        self.stage_2_final_temperature_display.value = self.operating_temperature
        self.stage_2_final_volume_display.value = self.stage_1_final_volume
        self.stage_2_heat_display.value = self.stage_2_heat
        
        self.stage_3_initial_pressure_display.value = self.stage_2_final_pressure
        self.stage_3_initial_temperature_display.value = self.operating_temperature
        self.stage_3_initial_volume_display.value = self.stage_1_final_volume
        self.stage_3_final_pressure_display.value = self.stage_3_final_pressure
        self.stage_3_final_temperature_display.value = self.stage_3_final_temperature
        self.stage_3_final_volume_display.value = self.initial_volume
        self.stage_3_work_display.value = self.stage_3_work
        
        self.stage_4_initial_pressure_display.value = self.stage_3_final_pressure
        self.stage_4_initial_temperature_display.value = self.stage_3_final_temperature
        self.stage_4_initial_volume_display.value = self.initial_volume
        self.stage_4_final_pressure_display.value = self.initial_pressure
        self.stage_4_final_temperature_display.value = self.initial_temperature
        self.stage_4_final_volume_display.value = self.initial_volume
        self.stage_4_heat_display.value = self.stage_4_heat
    
    def calculate(self) -> None:
        self.initial_volume = convert_cubic_feet_to_cubic_inches(
            calculate_initial_volume(
                self.compression_ratio,
                convert_cubic_inches_to_cubic_feet(self.engine_displacement)
            )
        )
        
        self.air_mass = calculate_air_mass(
            convert_psi_to_psf(self.initial_pressure),
            convert_farhenheit_to_rankine(self.initial_temperature),
            convert_cubic_inches_to_cubic_feet(self.initial_volume),
            self.gas_constant
        )
        
        self.stage_1_final_pressure = convert_psf_to_psi(
            calculate_final_pressure_adiabatic(
                self.compression_ratio,
                self.adiabatic_index,
                convert_psi_to_psf(self.initial_pressure)
            )
        )
        self.stage_1_final_temperature = convert_rankine_to_farhenheit(
            calculate_final_temperature_adiabatic(
                self.compression_ratio,
                self.adiabatic_index,
                convert_farhenheit_to_rankine(self.initial_temperature)
            )
        )
        self.stage_1_final_volume = convert_cubic_feet_to_cubic_inches(
            calculate_final_volume(
                self.compression_ratio,
                convert_cubic_inches_to_cubic_feet(self.initial_volume)
            )
        )
        self.stage_1_work = convert_ft_lbf_to_btu(
            calculate_work_adiabatic(
                self.adiabatic_index,
                convert_psi_to_psf(self.initial_pressure),
                convert_cubic_inches_to_cubic_feet(self.initial_volume),
                convert_psi_to_psf(self.stage_1_final_pressure), 
                convert_cubic_inches_to_cubic_feet(self.stage_1_final_volume)
            )
        )
        
        self.stage_2_final_pressure = convert_psf_to_psi(
            calculate_final_pressure_constant_volume(
                convert_psi_to_psf(self.stage_1_final_pressure),
                convert_farhenheit_to_rankine(self.operating_temperature), 
                convert_farhenheit_to_rankine(self.stage_1_final_temperature)
            )
        )
        self.stage_2_heat = calculate_heat(
            self.specific_heat_volume,
            self.air_mass,
            convert_farhenheit_to_rankine(self.operating_temperature),
            convert_farhenheit_to_rankine(self.stage_1_final_temperature)
        )
        
        self.stage_3_final_pressure = convert_psf_to_psi(
            calculate_final_pressure_adiabatic(
                self.compression_ratio,
                self.adiabatic_index,
                convert_psi_to_psf(self.stage_2_final_pressure),
                compression=False # Expansion stroke
            )
        )
        self.stage_3_final_temperature = convert_rankine_to_farhenheit(
            calculate_final_temperature_adiabatic(
                self.compression_ratio,
                self.adiabatic_index,
                convert_farhenheit_to_rankine(self.operating_temperature), 
                compression=False # Expansion stroke
            )
        )
        self.stage_3_work = convert_ft_lbf_to_btu(
            calculate_work_adiabatic(
                self.adiabatic_index,
                convert_psi_to_psf(self.stage_2_final_pressure),
                convert_cubic_inches_to_cubic_feet(self.stage_1_final_volume),
                convert_psi_to_psf(self.stage_3_final_pressure),
                convert_cubic_inches_to_cubic_feet(self.initial_volume)
            )
        )
        
        self.stage_4_heat = calculate_heat(
            self.specific_heat_volume,
            self.air_mass,
            convert_farhenheit_to_rankine(self.initial_temperature),
            convert_farhenheit_to_rankine(self.stage_3_final_temperature)
        )
        
        self.total_work = calculate_total_work(self.stage_1_work, self.stage_3_work)
        self.thermal_efficiency = calculate_thermal_efficiency(self.total_work, self.stage_2_heat)
    
    def graph(self) -> None:
        stage_1_data = get_adiabatic_data(
            self.adiabatic_index,
            convert_psi_to_psf(self.initial_pressure),
            convert_cubic_inches_to_cubic_feet(self.initial_volume),
            convert_cubic_inches_to_cubic_feet(self.stage_1_final_volume)
        )
        
        stage_3_data = get_adiabatic_data(
            self.adiabatic_index,
            convert_psi_to_psf(self.stage_2_final_pressure),
            convert_cubic_inches_to_cubic_feet(self.stage_1_final_volume),
            convert_cubic_inches_to_cubic_feet(self.initial_volume)
        )
        
        combined_data = (
            stage_1_data[0] + stage_3_data[0] + stage_1_data[0][0:1],
            stage_1_data[1] + stage_3_data[1] + stage_1_data[1][0:1]
        )
        
        # Create a plot window
        self.graph_window = pg.plot(*combined_data, title="Otto Cycle", labels={"left": "Pressure (psi)", "bottom": "Volume (in^3)"}, pen=(59, 166, 237), antialias=True, skipFiniteCheck=True)
        self.graph_window.setWindowIcon(QtGui.QIcon(get_file_path("assets/Trine.ico")))
    
    def handle_save_results_action(self) -> None:
        if not self.calculated:
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Results", str(Path.home() / "Documents"), "Text Files (*.txt)")
        
        if file_path:
            with open(file_path, "w") as file:
                # Header
                file.write("Otto Cycle Calculator Results:\n")
                if self._app_version is not None:
                    file.write(f"Generated by Otto Cycle Calculator {self._app_version} on {dt.datetime.now().strftime('%B %d, %Y %I:%M:%S %p')}\n\n\n")
                else:
                    file.write(f"Generated by Otto Cycle Calculator on {dt.datetime.now().strftime('%B %d, %Y %I:%M:%S %p')}\n\n\n")
                
                
                # Inputs
                file.write("Inputs:\n")
                file.write(f"\tCompression Ratio (CR): {self.compression_ratio:.2f}\n")
                file.write(f"\tSpecific Heat at Constant Pressure (C_p): {self.specific_heat_pressure:.3f} Btu/lb-°F\n")
                file.write(f"\tSpecific Heat at Constant Volume (C_v): {self.specific_heat_volume:.3f} Btu/lb-°F\n")
                file.write(f"\tAdiabatic Index (k): {self.adiabatic_index:.4f}\n")
                file.write(f"\tGas Constant (R): {self.gas_constant:.4f} lbf-ft/lbm-°R\n")
                file.write(f"\tEngine Displacement (deltaV): {self.engine_displacement:.2f} in^3\n")
                file.write(f"\tInitial Pressure (P_1): {self.initial_pressure:.2f} psi\n")
                file.write(f"\tInitial Temperature (T_1): {self.initial_temperature:.2f} °F\n")
                file.write(f"\tOperating Temperature (T_3): {self.operating_temperature:.2f} °F\n\n\n")
                
                
                # Outputs
                file.write("Outputs:\n")
                
                file.write("\tGeneral:\n")
                file.write(f"\t\tAir Mass (m_air): {self.air_mass:.4f} lbm\n")
                file.write(f"\t\tTotal Work (Work_total): {self.total_work:.2f} Btu\n")
                file.write(f"\t\tThermal Efficiency (Efficiency): {(self.thermal_efficiency * 100):.2f}%\n\n")
                
                file.write("\tStage 1 -> 2 (Adiabatic Compression):\n")
                file.write(f"\t\tInitial Pressure (P_1): {self.initial_pressure:.2f} psi\n")
                file.write(f"\t\tInitial Temperature (T_1): {self.initial_temperature:.2f} °F\n")
                file.write(f"\t\tInitial Volume (V_1): {self.initial_volume:.2f} in^3\n")
                file.write(f"\t\tFinal Pressure (P_2): {self.stage_1_final_pressure:.2f} psi\n")
                file.write(f"\t\tFinal Temperature (T_2): {self.stage_1_final_temperature:.2f} °F\n")
                file.write(f"\t\tFinal Volume (V_2): {self.stage_1_final_volume:.2f} in^3\n")
                file.write(f"\t\tHeat (Q_1): 0 Btu\n")
                file.write(f"\t\tWork (Work_1): {self.stage_1_work:.2f} Btu\n\n")
                
                file.write("\tStage 2 -> 3 (Combustion):\n")
                file.write(f"\t\tInitial Pressure (P_2): {self.stage_1_final_pressure:.2f} psi\n")
                file.write(f"\t\tInitial Temperature (T_2): {self.stage_1_final_temperature:.2f} °F\n")
                file.write(f"\t\tInitial Volume (V_2): {self.stage_1_final_volume:.2f} in^3\n")
                file.write(f"\t\tFinal Pressure (P_3): {self.stage_2_final_pressure:.2f} psi\n")
                file.write(f"\t\tFinal Temperature (T_3): {self.operating_temperature:.2f} °F\n")
                file.write(f"\t\tFinal Volume (V_3): {self.stage_1_final_volume:.2f} in^3\n")
                file.write(f"\t\tHeat (Q_2): {self.stage_2_heat:.2f} Btu\n")
                file.write(f"\t\tWork (Work_2): 0 Btu\n\n")
                
                file.write("\tStage 3 -> 4 (Adiabatic Expansion):\n")
                file.write(f"\t\tInitial Pressure (P_3): {self.stage_2_final_pressure:.2f} psi\n")
                file.write(f"\t\tInitial Temperature (T_3): {self.operating_temperature:.2f} °F\n")
                file.write(f"\t\tInitial Volume (V_3): {self.stage_1_final_volume:.2f} in^3\n")
                file.write(f"\t\tFinal Pressure (P_4): {self.stage_3_final_pressure:.2f} psi\n")
                file.write(f"\t\tFinal Temperature (T_4): {self.stage_3_final_temperature:.2f} °F\n")
                file.write(f"\t\tFinal Volume (V_4): {self.initial_volume:.2f} in^3\n")
                file.write(f"\t\tHeat (Q_3): 0 Btu\n")
                file.write(f"\t\tWork (Work_3): {self.stage_3_work:.2f} Btu\n\n")
                
                file.write("\tStage 4 -> 1 (Heat Rejection):\n")
                file.write(f"\t\tInitial Pressure (P_4): {self.stage_3_final_pressure:.2f} psi\n")
                file.write(f"\t\tInitial Temperature (T_4): {self.stage_3_final_temperature:.2f} °F\n")
                file.write(f"\t\tInitial Volume (V_4): {self.initial_volume:.2f} in^3\n")
                file.write(f"\t\tFinal Pressure (P_1): {self.initial_pressure:.2f} psi\n")
                file.write(f"\t\tFinal Temperature (T_1): {self.initial_temperature:.2f} °F\n")
                file.write(f"\t\tFinal Volume (V_1): {self.initial_volume:.2f} in^3\n")
                file.write(f"\t\tHeat (Q_4): {self.stage_4_heat:.2f} Btu\n")
                file.write(f"\t\tWork (Work_4): 0 Btu\n\n\n")
                
                file.write("Otto Cycle Calcultor. © 2025 Nicholas Ewing. All rights reserved.")
            
            QtWidgets.QMessageBox.information(self, "Results Saved", f"Results saved to <a href=\"file:///{file_path}\">{file_path.split('/')[-1]}</a>")
    
    def handle_calculate_button(self) -> None:
        self.calculate()
        
        self.refresh_output_display()
        
        self.calculated = True
        self.save_results_action.setEnabled(True)
        self.graph_button.setEnabled(True)
    
    def handle_graph_button(self) -> None:
        if not self.calculated:
            return
        
        if self.graph_window is not None:
            # self.graph_window.setFocus()
            self.graph_window.activateWindow()
            return
        
        self.graph()
    
    def handle_clear_output_button(self) -> None:
        self.refresh_output_display(clear=True)

        self.calculated = False
        self.save_results_action.setEnabled(False)
        self.graph_button.setEnabled(False)
    
    def handle_reset_inputs_button(self) -> None:
        self.set_input_defaults()
        
        self.refresh_output_display(clear=True)

        self.calculated = False
        self.save_results_action.setEnabled(False)
        self.graph_button.setEnabled(False)
    
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.graph_window is not None:
            self.graph_window.close()
        
        return super().closeEvent(event)
        
        
class ValueWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None, label_text: str = "", initial_value: int | float | None = None, decimals: int = 2, prefix: str | None = None, suffix: str | None = None, editable: bool = True) -> None:
        super().__init__(parent)
        
        self.label_text = label_text
        self.initial_value = initial_value
        self.decimals = decimals
        self.prefix = prefix
        self.suffix = suffix
        self.editable = editable
        
        self.max_value = 1e+21
        
        self.setup_ui()
        
        self.valueChanged = self.field.valueChanged
    
    def setup_ui(self) -> None:
        self.setStyleSheet("""
            QLabel {
                font-size: 10pt;
            }
            QDoubleSpinBox {
                border-radius: 3px;
            }
        """)
        
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed))
        
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setSpacing(2)
        self.vertical_layout.setContentsMargins(4, 4, 4, 4)
        
        self.label = QtWidgets.QLabel(self)
        self.label.setText(self.label_text)
        
        self.field = QtWidgets.QDoubleSpinBox(self)
        self.field.setFrame(False)
        self.field.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.field.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.field.setDecimals(0) # 0 to show initials without decimals, will be set to self.decimals if value is not 0
        self.field.setMinimum(-self.max_value)
        self.field.setMaximum(self.max_value)
        self.field.setReadOnly(not self.editable)
        if self.initial_value is not None:
            self.field.setValue(self.initial_value)
        if self.prefix is not None:
            self.field.setPrefix(f"{self.prefix} ")
        if self.suffix is not None:
            self.field.setSuffix(f" {self.suffix}")
        
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.field)
        
        self.setLayout(self.vertical_layout)
        
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
    
    @property
    def value(self) -> int | float:
        return self.field.value()
    
    @value.setter
    def value(self, value: int | float) -> None:
        if value == 0:
            self.field.setDecimals(0)
        else:
            self.field.setDecimals(self.decimals)
        
        self.field.setValue(value)
        
    def set_label(self, label: str) -> None:
        self.label.setText(label)
        
    def tie_change_function(self, function: Any) -> None:
        self.field.valueChanged.connect(function)