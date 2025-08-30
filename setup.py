from setuptools import setup

setup(
    name="douglas",
    version="0.1.0",
    description="A terminal application",
    py_modules=["douglas"],
    entry_points={
        "console_scripts": [
            "douglas=douglas:main",
        ],
    },
    python_requires=">=3.6",
)