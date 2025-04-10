import setuptools

NAME: str = "personal_python_syntax_optimizer"

setuptools.setup(
    name=NAME, packages=setuptools.find_packages(include=[NAME, f"{NAME}.*"])
)
