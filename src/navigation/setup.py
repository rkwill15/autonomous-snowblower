import os
from glob import glob
from setuptools import find_packages, setup

package_name = "navigation"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Reese Will",
    maintainer_email="rkwill@wpi.edu",
    description="SnowBot navigation, localization, and sidewalk waypoint mission stack",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "waypoint_follower = navigation.waypoint_follower:main"
        ],
    },
)
