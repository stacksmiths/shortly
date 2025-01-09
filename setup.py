from setuptools import setup, find_packages

setup(
    name="shortly",
    version="0.1.1",
    author="John Ajera",
    description="FastAPI-powered URL shortener for quick, reliable links",
    long_description=open("README.rst", encoding="utf-8").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/stacksmiths/shortly",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=9",
    entry_points={
        "console_scripts": [
            "shortly=src.shortly.main:main",
        ],
    },
)
