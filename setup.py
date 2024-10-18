import setuptools

NAME: str = "personal_python_minifier"

setuptools.setup(
    name=NAME,
    packages=setuptools.find_packages(include=[NAME, f"{NAME}.*"]),
    install_requires=["autoflake==2.3.1"],
)
