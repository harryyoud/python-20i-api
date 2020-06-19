import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twentyi-api-harryyoud",
    version="1.0.0",
    author="Harry Youd",
    author_email="harry@harryyoud.co.uk",
    description="API for 20i reseller hosting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harryyoud/python-20i-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
