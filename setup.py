import setuptools

setuptools.setup(
    name="rephile",
    version="0.0.0",
    author="Brett Viren",
    author_email="brett.viren@gmail.com",
    description="A digital photo oriented storage system",
    url="https://brettviren.github.io/rephile",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires = [
        "click",
        "jinja2",
        "sqlalchemy",
        "python-magic",
        "git_annex_adapter",
    ],
    entry_points = dict(
        console_scripts = [
            'rephile = rephile.__main__:main',
        ]
    ),
)
