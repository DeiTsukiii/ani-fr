from setuptools import setup

setup(
    name="ani-fr",
    version="1.0",
    py_modules=["ani_fr"],
    entry_points={
        "console_scripts": [
            "ani-fr = ani_fr:main",
        ],
    },
)