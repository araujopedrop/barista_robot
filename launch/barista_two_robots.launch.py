#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from launch_ros.actions                import Node
from launch                            import LaunchDescription
from ament_index_python.packages       import get_package_prefix
from launch.actions                    import DeclareLaunchArgument
from launch.actions                    import IncludeLaunchDescription
from ament_index_python.packages       import get_package_share_directory
from launch.substitutions              import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro

# this is the function launch  system will look for


def generate_launch_description():

    ####### DATA INPUT ##########
    robot_desc_file           = 'barista_robot_model.urdf.xacro'
    package_description       = "barista_robot_description"
    pkg_gazebo_ros            = get_package_share_directory('gazebo_ros')
    pkg_barista_robot_gazebo  = get_package_share_directory(package_description)

    # We get the whole install dir
    # We do this to avoid having to copy or softlink manually the packages so that gazebo can find them
    description_package_name = package_description
    install_dir = get_package_prefix(description_package_name)

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_barista_robot_gazebo, 'models')
    gazebo_meshes_path = os.path.join(pkg_barista_robot_gazebo, 'meshes')
    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path + ':' + gazebo_meshes_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path + ':' + gazebo_meshes_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )    

    robot_rick_name = "rick"
    robot_morty_name = "morty"

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Define the robot model files to be used
    robot_desc_path = os.path.join(get_package_share_directory(
        "barista_robot_description"), "xacro", robot_desc_file)

    rsp_rick = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=robot_rick_name,
        parameters=[{'frame_prefix': robot_rick_name+'/', 'use_sim_time': use_sim_time,
                     'robot_description': Command(['xacro ', robot_desc_path, ' robot_name:=', robot_rick_name])}],
        output="screen"
    )

    rsp_morty = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=robot_morty_name,
        parameters=[{'frame_prefix': robot_morty_name+'/', 'use_sim_time': use_sim_time,
                     'robot_description': Command(['xacro ', robot_desc_path, ' robot_name:=', robot_morty_name])}],
        output="screen"
    )

    spawn_rick = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'robot1', '-x', '0.0', '-y', '0.0', '-z', '0.0',
                   '-topic', robot_rick_name+'/robot_description']
    )

    spawn_morty = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'robot2', '-x', '0.0', '-y', '2.0', '-z', '0.0',
                   '-topic', robot_morty_name+'/robot_description']
    )
    

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), "config", 'config_file_rick_and_morty.rviz')

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])


    rick_broadcaster_node = Node(
            package='barista_robot_description',
            executable='rick_broadcaster.py',
            name='rick_broadcaster',
        )

    morty_broadcaster_node = Node(
            package='barista_robot_description',
            executable='morty_broadcaster.py',
            name='morty_broadcaster',
        )


    # create and return launch description object
    return LaunchDescription(
        [
            gazebo,
            DeclareLaunchArgument(
            'world',
            default_value=[os.path.join(pkg_barista_robot_gazebo, 'worlds', 'barista_robot_empty.world'), ''],
            description='SDF world file'),
            rsp_rick,
            rsp_morty,
            spawn_rick,
            spawn_morty,
            rick_broadcaster_node,
            morty_broadcaster_node,
            rviz_node
        ]
    )