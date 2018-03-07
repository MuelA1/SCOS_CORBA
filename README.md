# Setup Environment for Ubuntu
- Install Anaconda (download from https://www.anaconda.com/download/#linux)
## Install omniORB
- tar xf omniORB-4.2.2.tar.bz2
- cd omniORB-4.2.2/; mkdir build
- cd build/; ../configure (specify PYTHON='location of anaconda python binary' if required)
- make
- sudo make install
## Install omniORBpy
- repeat steps above for omniORBpy
## Add to .bashrc
- export PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.6/site-packages"
- export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib:/usr/local/lib/python3.6" 
(you may have to change these paths according to your setup)
