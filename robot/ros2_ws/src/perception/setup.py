import os
from glob import glob
from setuptools import find_packages, setup

package_name = "perception"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages",
            ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Install launch files so 'ros2 launch' can find them.
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Oleg Minenko",
    maintainer_email="olegminenko2005@gmail.com",
    description="World A perception nodes: camera capture and object detection.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "heartbeat = perception.heartbeat:main",
            "listener = perception.listener:main",
        ],
    },
)
