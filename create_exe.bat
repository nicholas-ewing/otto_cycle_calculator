@echo off
cd spec_files
pyinstaller -y --clean --distpath "../executables/dist" --workpath "../executables/build" OttoCycleCalculator.spec
cd ..