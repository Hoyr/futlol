# futlol
q-learning game for open spiel framework https://github.com/deepmind/open_spiel

## Install
Add futlol.cc, futlol.h, and futlol_test.cc to the game source code folder and add the game to CMake and test suite as per the instructions here: https://github.com/deepmind/open_spiel/blob/master/docs/developer_guide.md

Optional: Replace file_logger.py in the OpenSpiel python utils. Adds makedir functionality to file_logger.py

Place futlol_dqn.py, futlol_dqn_load.py, and futlol_dqn_playgame.py in the python examples folder and run them from a terminal sitting in the OpenSpiel main folder.

The files data_analysis.py, data_compress.py and replay_game.py are helper scripts for data analysis and are setup to be run from the folder the data is logged to.
