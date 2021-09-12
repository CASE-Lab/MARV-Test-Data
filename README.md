# MARV-Test-Data
Data from test drives with the MARV system in ROS2 bag format

## Decoding ROS2 bag data
A script in available in rosbag-decode can be used to load and decode the data in Python. To do this the ros message defenitions used when recording the data are needed. To simply this a copy of the message defenitions have been provided in the folder.
The rosbag decode scripts also include functionlaity to resample, plot, select data of intrest and export to CSV. The data processing is based around Python Pandas which should make other data processing of the data simple to perform.
