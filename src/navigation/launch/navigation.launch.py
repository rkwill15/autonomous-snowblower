import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg_dir = get_package_share_directory('navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    ekf_config = os.path.join(nav_pkg_dir, 'config', 'ekf.yaml')
    nav2_params = os.path.join(nav_pkg_dir, 'config', 'nav2_params.yaml')

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config]
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'False',
            'params_file': nav2_params
        }.items()
    )

    return LaunchDescription([
        ekf_node,
        nav2_launch
    ])
