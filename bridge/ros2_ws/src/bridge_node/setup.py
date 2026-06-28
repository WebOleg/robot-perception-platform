from setuptools import find_packages, setup

package_name = "bridge_node"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages",
            ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Oleg Minenko",
    maintainer_email="olegminenko2005@gmail.com",
    description="The seam: forwards ROS2 detections to World B over HTTP.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "bridge = bridge_node.bridge:main",
        ],
    },
)
