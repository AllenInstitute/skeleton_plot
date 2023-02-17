import setuptools

setuptools.setup(
    name="skeleton_plot",
    version="0.0.2",
    author="Emily Joyce",
    author_email="emily.m.joyce1@gmail.com",
    description="tools for visulizing skeletons",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    #project_urls={
        #"Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    #},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"skeleton_plot": "plot_tools.py"},
    packages=setuptools.find_packages(where = 'src'),
    python_requires=">=3.6",
)