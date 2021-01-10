import setuptools
import setuptools.command.build_py


class NpmInstall(setuptools.command.build_py.build_py):

    def run(self):
        self.spawn(['npm', 'ci', '--prefix', 'plugin/static'])
        super().run()


setuptools.setup(
    name='interactive_widgets_mkdocs',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'beautifulsoup4>=4.9.3',
        'mkdocs>=1.1.2',
    ],
    entry_points={
        'mkdocs.plugins': [
            'interactive_widgets = plugin.plugin:Plugin',
        ],
    },
    include_package_data=True,
    cmdclass={
        'build_py': NpmInstall,
    },
)
