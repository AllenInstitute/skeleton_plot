from setuptools import setup, find_packages
import re
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


# def find_version(*file_paths):
#     version_file = read(*file_paths)
#     version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
#     if version_match:
#         return version_match.group(1)
#     raise RuntimeError("Unable to find version string.")


with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setup(
    version='0.0.5',
    name="skeleton_plot",
    description="package for plotting skeletons",
    author="Emily Joyce, Forrest Collman, Casey Schneider-Mizell",
    author_email="emily.joyce@alleninstitute.org, forrestc@alleninstute.org,caseys@alleninstitute.org,",
    url="https://github.com/AllenInstitute/skeleton_plot",
    packages=find_packages(where="."),
    extras_require={"cloud": ["caveclient>=4.0.0", "cloudfiles"]},
    include_package_data=True,
    install_requires=required,
    setup_requires=["pytest-runner"],
)