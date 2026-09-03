import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessExit

from launch_ros.actions import Node

import xacro


def generate_launch_description():

    package_name = 'car_description'

    pkg_share = get_package_share_directory(package_name)

    install_dir = os.path.dirname(pkg_share)


    # ============================================================
    # 1. Gazebo resource path
    # ============================================================

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            install_dir,
            ':',
            os.environ.get('GZ_SIM_RESOURCE_PATH', '')
        ]
    )


    # ============================================================
    # 2. Process URDF/Xacro
    # ============================================================

    xacro_file = os.path.join(
        pkg_share,
        'urdf',
        'c_car_sim.urdf.xacro'
    )

    robot_description_config = xacro.process_file(xacro_file)

    robot_description = {
        'robot_description': robot_description_config.toxml()
    }


    # ============================================================
    # 3. Robot State Publisher
    # ============================================================

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': True}
        ]
    )


    # ============================================================
    # 4. Launch Gazebo Sim (Points to your custom world file)
    # ============================================================

    world_path = os.path.join(
        pkg_share,
        'worlds',
        'car_world1.sdf'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ]),
        launch_arguments={
            'gz_args': f'-r {world_path}'
        }.items()
    )


    # ============================================================
    # 5. Gazebo CLOCK -> ROS 2 /clock
    # ============================================================

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )


    # ============================================================
    # 6. Gazebo LiDAR -> ROS 2 LaserScan
    # ============================================================

    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )


    # ============================================================
    # 7. Spawn Robot into Gazebo
    # ============================================================

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'car_description'
        ],
        output='screen'
    )


    # ============================================================
    # 8. Joint State Broadcaster (Enforced sim time)
    # ============================================================

    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--ros-args',
            '-p',
            'use_sim_time:=true'
        ],
        output='screen'
    )


    # ============================================================
    # 9. Ackermann Steering Controller (Enforced sim time)
    # ============================================================

    load_car_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'ackermann_steering_controller',
            '--ros-args',
            '-p',
            'use_sim_time:=true'
        ],
        output='screen'
    )


    # ============================================================
    # 10. Launch Description Assembly
    # ============================================================

    return LaunchDescription([

        # Gazebo environment
        set_gz_resource_path,

        # State publishers
        node_robot_state_publisher,

        # Simulation engine
        gazebo,

        # Topic Bridges
        clock_bridge,
        lidar_bridge,

        # Entity Spawner
        spawn_entity,


        # --------------------------------------------------------
        # Spawn entity -> Joint State Broadcaster
        # --------------------------------------------------------

        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[
                    load_joint_state_broadcaster
                ],
            )
        ),


        # --------------------------------------------------------
        # Joint State Broadcaster -> Ackermann Controller
        # --------------------------------------------------------

        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[
                    load_car_controller
                ],
            )
        ),
    ])