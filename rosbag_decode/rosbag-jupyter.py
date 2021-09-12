# Script for handling ros2 bag file generated from the WaveRunner system
# To be run interactively in VS Code Jupypter notebook:
# https://code.visualstudio.com/docs/python/jupyter-support-py
# Can also be converted to regular Jupyter notebook
# (See the "Export a Jupyter notebook" section at the link above)
# %% imports

# for pandas
from numpy.lib.utils import source
import pandas as pd
import numpy as np

# rosbag
import rb2reader as rb

# plotting (uses hvplot, holoviews, bokeh)
import holoviews as hv
from bokeh.plotting import show
# Holoviz doc: https://holoviz.org/index.html

# %% Defining realtive file path
import os
from pathlib import Path
# __file__ attribute does not exsist if running as regular jupyter notebook
dirname = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()

# path to manual test drive
# rosbag_path = os.path.join(dirname, 'logs_2021','rosbag2_2021_06_23-18_04_32')

# path to last wp test rosbag2_2021_07_20-18_23_30
# rosbag_path = os.path.join(dirname, 'logs_2021','rosbag2_2021_07_20-18_23_30')

# heading test rosbag:
# rosbag2_2021_07_20-17_23_31 (bad data - drfiting)
# rosbag2_2021_07_20-17_32_20 (good looking Z WP drive)
# rosbag2_2021_07_20-17_12_08
rosbag_path = os.path.join(dirname, 'logs_2021','rosbag2_2021_07_20-17_12_08')

# %% Loading message defenitions
import os
from pathlib import Path

dirname = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()

sbg_msg_path = dirname / "logs_2021/ros_msg_def/sbg_ros2_msg"
sbg_msg_prefix = "sbg_driver/msg/"

sbg_pathlist = Path(sbg_msg_path).rglob('*.msg')

sbg_msg_dict = {}
for path in sbg_pathlist:
    sbg_msg_dict[(sbg_msg_prefix + path.stem)] = path

# add alias (additional key) for sbg status messages
sbg_msg_dict['msg/SbgEkfStatus'] = sbg_msg_dict[sbg_msg_prefix + 'SbgEkfStatus']
sbg_msg_dict['msg/SbgImuStatus'] = sbg_msg_dict[sbg_msg_prefix + 'SbgImuStatus']

wr_msg_path = dirname / "logs_2021/ros_msg_def/waverunner_msgs"
wr_msg_prefix = "waverunner_msgs/msg/"
wr_pathlist = Path(wr_msg_path).rglob('*.msg')

wr_msg_dict = {}
for path in wr_pathlist:
    wr_msg_dict[(wr_msg_prefix + path.stem)] = path

rb.load_msg_defenition(wr_msg_dict)
rb.load_msg_defenition(sbg_msg_dict)

# %% helper functions
def dict_value(key, series):
    return [tmp[key] for tmp in series]

# %% ekf nav plot longitude latitude example
nav_prefix = 'ekf_nav/'
df_ekf_nav = rb.topic2df(rosbag_path, '/sbg/ekf_nav',['header', 'time_stamp'], nav_prefix)
df_ekf_nav[nav_prefix + 'longitude'] = dict_value('x', df_ekf_nav[nav_prefix + 'position'])
df_ekf_nav[nav_prefix + 'latitude'] = dict_value('y', df_ekf_nav[nav_prefix + 'position'])
df_ekf_nav[nav_prefix + 'vel_x'] = dict_value('x', df_ekf_nav[nav_prefix + 'velocity'])
df_ekf_nav[nav_prefix + 'vel_y'] = dict_value('y', df_ekf_nav[nav_prefix + 'velocity'])
df_ekf_nav[nav_prefix + 'vel_z'] = dict_value('z', df_ekf_nav[nav_prefix + 'velocity'])
df_ekf_nav[nav_prefix + 'pos_valid'] = dict_value('position_valid', df_ekf_nav[nav_prefix + 'status'])
df_ekf_nav[nav_prefix + 'vel_valid'] = dict_value('velocity_valid', df_ekf_nav[nav_prefix + 'status'])
df_ekf_nav[nav_prefix + 'speed'] = np.sqrt(df_ekf_nav[nav_prefix + 'vel_x']**2 + df_ekf_nav[nav_prefix + 'vel_y']**2)

df_plt = df_ekf_nav.resample('40ms').mean()


# %% aps and rps values
tcu_prefix = 'tcu_log1/'
df_log2_tcu = rb.topic2df(rosbag_path, '/waverunner/sys/log/log1_tcu',[], tcu_prefix)
df_plt[tcu_prefix + 'throttle(aps)'] = df_log2_tcu[tcu_prefix + 'aps_out'].resample('40ms').mean()

# %% NCU steering angle
ncu_prefix = 'ncu_log1/'
df_log1_ncu = rb.topic2df(rosbag_path, '/waverunner/sys/log/log1_ncu', [], ncu_prefix)
df_plt[ncu_prefix + 'angle'] = df_log1_ncu[ncu_prefix + 'angle'].resample('40ms').mean()

# %% Ekf Heading
head_prefix = 'ekf_euler/'
df_ekf_euler = rb.topic2df(rosbag_path, '/sbg/ekf_euler',['header', 'time_stamp'], head_prefix)
df_ekf_euler[head_prefix + 'heading'] = np.rad2deg(dict_value('z', df_ekf_euler[head_prefix + 'angle']))
df_plt[head_prefix + 'heading'] = df_ekf_euler[head_prefix + 'heading'].resample('40ms').mean()

# %% Yaw rate
imu_prefix = 'imu_data/'
df_imu = rb.topic2df(rosbag_path, '/sbg/imu_data', ['header'], imu_prefix)
df_imu['gyro_z'] = dict_value('z', df_imu['imu_data/gyro'])
df_imu['delta_angle_z'] = dict_value('z', df_imu['imu_data/delta_angle'])


# %% Pose
pose_prefix = 'pose/'
df_pose = rb.topic2df(rosbag_path, '/waverunner/nav/sbg_pose', [], pose_prefix)
df_pose[pose_prefix + 'pos'] = dict_value('position', df_pose['pose/pose'])
df_pose[pose_prefix + 'pos_x'] = dict_value('x', df_pose[pose_prefix + 'pos'].apply(lambda x: vars(x)))
df_pose[pose_prefix + 'pos_y'] = dict_value('y', df_pose[pose_prefix + 'pos'].apply(lambda x: vars(x)))
df_plt[pose_prefix + 'pos_x'] = df_pose[pose_prefix + 'pos_x'].resample('40ms').mean()
df_plt[pose_prefix + 'pos_y'] = df_pose[pose_prefix + 'pos_y'].resample('40ms').mean()


# %% Check for NaN values and fill
print('Percentage of Nan Values before interpolation:')
print(df_plt[100:-100].isna().sum()/df_plt[100:-100].count()*100)

df_plt.interpolate(method='time', limit=3, inplace = True)

print('\nPercentage of Nan Values after interpolation:')
print(df_plt[100:-100].isna().sum()/df_plt[100:-100].count()*100)

# distribution of timedelta can be check by plotting the following histogram:
# df_ekf_nav.index.to_series().diff().astype('timedelta64[ms]').plot.hist()
# %% Log marker start/stop generation
log_m_prefix = 'log_m/'
df_log_m = rb.topic2df(rosbag_path, '/waverunner/sys/status/logging_marker', [], log_m_prefix)
df_log_m['log_m/current'] = df_log_m
df_log_m = df_log_m.drop(columns=['log_m/data'])
df_log_m['log_m/shifted'] = df_log_m['log_m/current'].shift(1)
df_log_m['log_m/start'] = df_log_m['log_m/current'] - df_log_m['log_m/shifted'] > 0
df_log_m['log_m/stop'] = df_log_m['log_m/current'] - df_log_m['log_m/shifted'] < 0
df_plt['log_m/start'] = df_log_m['log_m/start'].loc[df_log_m['log_m/start'] == True].resample('40ms').mean()
df_plt['log_m/stop'] = df_log_m['log_m/stop'].loc[df_log_m['log_m/stop'] == True].resample('40ms').mean()

# merge into single start stop column
df_plt['log_m/start'] = df_plt['log_m/start'].replace([1], ['log_start'])
df_plt['log_m/stop'] = df_plt['log_m/stop'].replace([1], ['log_stop'])

df_plt['log_m/start_stop'] = df_plt['log_m/start'].combine_first(df_plt['log_m/stop'])



# %% Setting up linked speed and position plot
# https://stackoverflow.com/questions/59609911/holoviews-hovertool-show-extra-row
import hvplot.pandas  # noqa
from holoviews import streams

pos_plot = df_plt.hvplot(
    title = 'Position',
    kind = 'line',
    x = nav_prefix + 'latitude',
    y = nav_prefix + 'longitude',
    by = nav_prefix + 'pos_valid',  # this creates the overlay
    aspect = 'equal',
    hover_cols=['timestamp', head_prefix + 'heading'],
    width = 1600,
    #tools=['box_select', 'lasso_select'],
    padding=0.1
)


speed_plot = df_plt.hvplot(
    title = 'Speed',
    kind='line',
    x = 'timestamp',
    y = nav_prefix + 'speed',
    width = 1600,
    by = nav_prefix + 'vel_valid',  # this creates the overlay
    padding = 0.1
)

start_marker_plot = df_plt.loc[df_plt['log_m/start_stop'].notnull()].hvplot(
    kind = 'scatter',
    x = nav_prefix + 'latitude',
    y = nav_prefix + 'longitude',
    color = 'log_m/start_stop',
    colorbar = False,
    cmap = ['green', 'red'],
    size = 100,
    width = 1600
)

throttle_plot = df_plt.hvplot(
    title = 'Throttle',
    kind='line',
    x = 'timestamp',
    y = tcu_prefix + 'throttle(aps)',
    width = 1600,
    padding = 0.1
)

steering_plot = df_plt.hvplot(
    title = 'Steering Angle',
    kind='line',
    x = 'timestamp',
    y = ncu_prefix + 'angle',
    width = 1600,
    padding = 0.1
)

heading_plot = df_plt.hvplot(
    title = 'Heading Angle',
    kind='scatter',
    x = 'timestamp',
    y = head_prefix + 'heading',
    width = 1600,
    padding = 0.1,
    size = 10
)

selection_linker = hv.selection.link_selections.instance(index_cols = ['timestamp'])

pos_plot = selection_linker(pos_plot)
speed_plot = selection_linker(speed_plot)
throttle_plot = selection_linker(throttle_plot)
steering_plot = selection_linker(steering_plot)
heading_plot = selection_linker(heading_plot)


# %% create and apply holoviews vlines for marking start stop in data
start_vlines = []
stop_vlines = []
for datetime in df_plt.loc[df_plt['log_m/start'].notnull()].index:
    start_vlines.append(hv.VLine(datetime).opts(color = 'green', line_dash='dashed'))

for datetime in df_plt.loc[df_plt['log_m/stop'].notnull()].index:
    stop_vlines.append(hv.VLine(datetime).opts(color = 'red', line_dash='dashed'))

for start_vline, stop_vline in zip(start_vlines, stop_vlines):
    speed_plot = speed_plot * start_vline * stop_vline
    steering_plot = steering_plot * start_vline * stop_vline
    heading_plot = heading_plot * start_vline * stop_vline
    throttle_plot = throttle_plot * start_vline * stop_vline
# %% Setting up geotiff background (air photo)
# https://towardsdatascience.com/displaying-a-gridded-dataset-on-a-web-based-map-ad6bbe90247f

import bokeh as bk
import holoviews as hv
import hvplot.xarray # noqa: adds hvplot method to xarray objects
import rioxarray as rxr
import panel as pn
import datashader

da = rxr.open_rasterio('geo-data/639_31_50_1971.tif', parse_coordinates=True)
#da_lonlat = da.rio.reproject("EPSG:3006")   #corrects projection but still wrong coordinates
da_lonlat = da.rio.reproject("WGS84")   #corrects projection but still wrong coordinates

# define clipping reigion
geometries = [
    {
        'type': 'Polygon',
        'coordinates': [[
            [11.83, 57.66],
            [11.83, 57.68],
            [11.86, 57.68],
            [11.86, 57.66]
        ]]
    }
]

clipped = da_lonlat.rio.clip(geometries)

# %% Stop server
bokeh_server.stop()
# %% 
# Indexing of clipped is done to select first band of data
# After a selection is done a refresh of the web page is required to get correct date time formating again

geo_plot = clipped[0,:,:].hvplot.image(rasterize=True, cmap = 'gray', width = 1600, height = 600, colorbar = False, hover = False, aspect='equal')
bokeh_server = pn.panel((geo_plot*pos_plot*start_marker_plot + speed_plot + throttle_plot + steering_plot + heading_plot).cols(1)).show(port=12345)

# %% Use interactive selction
max_dt = pd.to_datetime(str(max(selection_linker.selection_expr.ops[0]['args'][0])))
min_dt = pd.to_datetime(str(min(selection_linker.selection_expr.ops[0]['args'][0])))

df_sliced = df_plt[min_dt : max_dt]

time_string = str(min_dt.minute) + '_' + str(min_dt.second) + '-' + str(max_dt.minute) + '_' + str(max_dt.second)
name = 'heading-test-0720 '

df_sliced.to_csv('output/' + name + time_string + '.csv')

# %% 
ppdu1= 'pdu-log1/'
df_pdu_log1 = rb.topic2df(rosbag_path, '/waverunner/sys/log/log1_pdu', prefix = ppdu1)
#df_pdu_log1.resample('1s').mean().plot()

plogm = 'log-mark/'
df_log_mark = rb.topic2df(rosbag_path, '/waverunner/sys/status/logging_marker', prefix = plogm)

df_merge = pd.merge_asof(df_pdu_log1.reset_index(), df_log_mark.reset_index(), on='timestamp', tolerance=pd.Timedelta('1ms'))
df_merge[plogm + 'data'] = (df_merge[plogm + 'data']*1000).interpolate(method = 'pad')
df_merge['timestamp'] = pd.to_datetime(df_merge['timestamp'])
df_merge = df_merge.set_index('timestamp')

df_merge.resample('1s').mean().plot()

# %%
