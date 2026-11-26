from setuptools import find_packages, setup

package_name = 'percepetion_module'

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
        'console_scripts': [ "camera_processor=percepetion_module.camera_processor:main",
                             "data_logger = percepetion_module.data_logger:main",
                             'joy_teleop = percepetion_module.joy_teleop:main',
        ],
    },
)
