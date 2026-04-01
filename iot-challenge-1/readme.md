# Challenge 1

## Description

Read `Challenge.pdf` to know about the assigned task and
`Report.pdf` to see the final document which has been
submitted together with the implemented system.

## Requirements

The following software is required in order to run the project:
- platformio
- Wokwi VSCode extension
- make
- python3

## Build, simulation and report generation

Use the targets in the makefile to manage the project.
- `venv` - Install all the python dependencies in a venv.
- `build` target - Build the binary.
- `timing_log` target - Reads the content of the file `simulation_log.txt`
  (who must be created manually: see below) and generate a csv file
  containing the start of each step of the cycle implemented by the device.
- `energy_report` target -  Get a complete report containing timing, power and
  energy analysis of the system based on the generated timing_log and the
  power samples saved in sample folder; a text report is saved on
  `energy_log.txt`.
  The python script that is responsible for the output generation has multiple
  configurable options: type ```./generate_energy_report.py --help``` for
  further information.
  You can pass the your configuration to the script by passing to make
  the argument `SCRIPT_ARGS="<your arguments here>`.
- `clean` target - Clean all the generated files.

**IMPORTANT**: Due to wokwi-cli limitations the simulation start has to be
launched using WokWi VSCode extension and the copy of the results from the
terminal to `simulation_log.txt` has to be done manually.