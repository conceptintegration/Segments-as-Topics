To compile anagular_distance.so for your environment follow the steps below.

1. Install or upgrade the cython package

% pip install --upgrade cython

2. In a terminal, change directory to the python directory:

% cd <cython_dir>

3. Create and run setup.py in a terminal:

% python setup.py build_ext --inplace

You may see some warnings but these can be ignored.

4. A shared object file named angular_distance.<cython_info>.so will be created at the top-level of the cython folder. Rename the shared object to angular_distance.so

4. Copy angular_distance.so to the ../processing/ folder.

