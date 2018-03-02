from setuptools import setup

setup(
    entry_points={
        'console_scripts': ['template = template.template:main']
    },
    include_package_data=True
)
