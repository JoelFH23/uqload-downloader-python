from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.readlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="uqload_dl",
    version="1.0",
    author="Joel Flores",
    license="GPLv3",
    description="Download any video from the Uqload site",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoelFH23/uqload-downloader-python",
    packages=["uqload_dl"],
    install_requires=requirements,
    keywords=["uqload", "download", "video"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "uqload_dl=uqload_dl.cli:main",
        ]
    },
)
