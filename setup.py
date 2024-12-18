#!/usr/bin/env python

from setuptools import find_packages, setup


def readme():
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    return content


version_file = "geoagent/version.py"


def get_version():
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


def parse_requirements(file_name: str) -> list[str]:
    with open(file_name) as f:
        return [
            require.strip()
            for require in f
            if require.strip() and not require.startswith("#")
        ]


if __name__ == "__main__":
    setup(
        name="geoagent",
        version=get_version(),
        description=(
            "An efficient toolkit for GEO data analysis"
        ),
        long_description=readme(),
        long_description_content_type="text/markdown",
        author="Panrong Tong",
        packages=find_packages(),
        include_package_data=True,
        python_requires=">=3.10",
        install_requires=parse_requirements("requirements.txt"),
        zip_safe=False,
        entry_points={"console_scripts": ["geoagent=geoagent.cli:cli"]},
    )
