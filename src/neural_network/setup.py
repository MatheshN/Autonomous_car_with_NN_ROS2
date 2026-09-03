from setuptools import find_packages, setup

package_name = 'neural_network'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mathesh',
    maintainer_email='matheshmsd21@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mock_lidar = neural_network.mock_lidar_pub:main',
            'gesture_control = neural_network.gesture_control:main',
            'brain = neural_network.brain:main',
        ],
    },
)
