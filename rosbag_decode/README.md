# Decoding ROS2 Bag files

* Via python rosbags
* Matlab https://se.mathworks.com/help/ros/ref/ros2bag.html

## Time Series Sample Rate

* Time series data from the ros bags will have large differences in how frequent they are. If possible it would be useful to have an sparse data representation with a common time axis and entires only when there is data for a specific collumn.
  * One solution could be using spares dataframes in Python Pandas. Merging from diffrent data frames can be done with merge_asof [How to Merge “Not Matching” Time Series with Pandas](https://towardsdatascience.com/how-to-merge-not-matching-time-series-with-pandas-7993fcbce063)