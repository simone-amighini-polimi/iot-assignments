.PHONY: make-env energy_report.txt clean clear-venv

all: .pio/build/esp32/firmware.elf

venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r python_requirements.txt

build: .pio/build/esp32/firmware.elf

timing_log: timing_log.csv

energy_report: energy_report.txt

.pio/build/esp32/firmware.elf: src/esp32.ino diagram.json platformio.ini wokwi.toml
	pio run

timing_log.csv: .pio/build/esp32/firmware.elf simulation_log.txt
	@if [ ! -f simulation_log.txt ]; then \
		echo "Error: You must save the simulation log manually before generating the timing log." >&2; \
		exit 1; \
	fi
	echo "Idle1_start,Sensing_start,Idle2_start,WiFi_start,TX_start,Idle3_start,Deep_sleep_start" > timing_log.csv
	grep ">>> Timings summary:" simulation_log.txt | sed 's/>>> Timings summary: //; s/, /,/g' >> timing_log.csv

energy_report.txt: timing_log.csv samples/*
	source .venv/bin/activate && ./generate_energy_report.py $(SCRIPT_ARGS) > energy_report.txt

clean:
	rm -rf .pio/build simulation_log.txt timing_log.csv energy_report.txt

clear-venv:
	rm -rf .venv