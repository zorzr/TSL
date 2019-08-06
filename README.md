# Time Series Labeler &emsp;&emsp;&emsp; [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-349bff.svg)](https://www.gnu.org/licenses/gpl-3.0)  [![Python 3](https://img.shields.io/badge/Python-100%25-brightgreen.svg)](https://www.python.org/)
*Time Series Labeler* (or just *TSL*) is a Python-developed tool for time series analysis, labelling and processing on Windows, Linux and MacOS.

It allows to plot multiple series at the same time, and provides features to manage the graphs layout. As the name suggests, labels can be put on some specific time lapses to identify a particular event (i.e. a machinery failure) and then be saved on the original data file.

Label names and colors are customizable from within the application and are stored in a specific configuration file for the type of selected project: in fact, you can choose to work on single files or manage bigger project for files containing the same kind of data (that is, the time series are indicated with the same name and are arranged in the same way for all files included in the project).

Furthermore, the application combines key bindings, mouse click and drag/drop to speed up operations and allow a quick context change from a file to the following. Zoom in and out is supported and can become really useful when managing really long series: high performances are granted by a downsampling algorithm which doesn't affect the usage and is completely transparent to the user.



## Features
- Works with single files
- Projects for related data files
- Timestamped data support
- Customizable labels for files and projects
- Mouse and keyboard bindings
- Drag-and-drop option for label application
- Single mouse click for precise labelling
- Right-click menu to customize the plot layout
- Downsampling algorithm applied for big series
- Zoom in/out on plots
- Autosave feature



## TODO
- Functions of existing series
- Figure layout management from settings
- Scrollbar to display huge numbers of plots
- Other minor improvements



## Requirements
- [Python 3](https://www.python.org/)
- [Numpy](https://www.numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib 3.1.0](https://matplotlib.org/)
- [PyQT5](https://pypi.org/project/PyQt5/)
- [lttb.py](https://github.com/javiljoen/lttb.py)

  
