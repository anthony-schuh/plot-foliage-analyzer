from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plot-foliage-analyzer",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Interactive OpenCV tool for rectifying plot images and quantifying green vegetation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anthony-schuh/plot-foliage-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "plot-analyzer=plots_green:main",
        ],
    },
)
