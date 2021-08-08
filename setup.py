from setuptools import setup
import os

VERSION = "0.2.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="myfitnesspal-to-sqlite",
    description="Save data from MyFitnessPal to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Wasim Lorgat",
    url="https://github.com/seem/myfitnesspal-to-sqlite",
    project_urls={
        "Issues": "https://github.com/seem/myfitnesspal-to-sqlite/issues",
        "CI": "https://github.com/seem/myfitnesspal-to-sqlite/actions",
        "Changelog": "https://github.com/seem/myfitnesspal-to-sqlite/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["myfitnesspal_to_sqlite"],
    entry_points="""
        [console_scripts]
        myfitnesspal-to-sqlite=myfitnesspal_to_sqlite.cli:cli
    """,
    install_requires=["click", "sqlite-utils>=3.0", "myfitnesspal"],
    extras_require={"test": ["pytest"]},
    tests_require=["myfitnesspal-to-sqlite[test]"],
)
