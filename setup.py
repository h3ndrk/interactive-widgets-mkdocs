import setuptools

setuptools.setup(
    name='interactive_widgets',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'beautifulsoup4>=4.9.3',
        'mkdocs>=1.1.2',
    ],
    entry_points={
        'mkdocs.plugins': [
            'interactive_widgets = interactive_widgets.plugin:Plugin',
        ],
    },
)
