from setuptools import setup, find_packages

setup(
    name="gym_codecraft",
    version="0.0.1",
    install_requires=["gymnasium"],
    packages=find_packages(where="gym_codecraft"),
    package_dir={"": "gym_codecraft"},
    package_data={"data": ["*", "**/*"]},
)
