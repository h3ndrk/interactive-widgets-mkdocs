import bs4
import mkdocs
import pathlib
import shlex
import typing

from .widget import Widget


class PrologueWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.command = self.tag['command']
        self.image = self.tag['image']
        self.hidden = self.tag.has_attr('hidden')
        self.working_directory = self.tag.get('working-directory', None)
        self.name = self._hash_inputs(
            'button',
            str(self.url),
            str(index),
            self.command,
            self.image,
            self.working_directory if self.working_directory is not None else '',
        )

    def __str__(self) -> str:
        return f'PrologueWidget(name={repr(self.name)}, command={repr(self.command)}, image={repr(self.image)}, hidden={repr(self.hidden)}, working_directory={repr(self.working_directory)})'

    def get_static_files(self):
        return ['PrologueWidget.js']

    def get_dependencies(self) -> typing.List[bs4.element.Tag]:
        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/PrologueWidget.js')
        return [script_widget]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-prologue-{self.name}'
        return div

    def get_instantiation(self) -> bs4.element.Tag:
        script = self.soup.new_tag('script')
        script.append(f'''
            {{
                roomConnection.addWidget();
                const widget = new PrologueWidget(
                    document.getElementById("widget-prologue-{self.name}"),
                    "{self._sanitize_javascript(self.command)}",
                    {"true" if self.hidden else "false"},
                );
                widget.addEventListener("ready", function _listener() {{
                    roomConnection.markWidgetReady();
                    widget.removeEventListener("ready", _listener);
                }});
                roomConnection.addEventListener("{self.name}", event => {{
                    widget.handleMessage(event.detail);
                }});
                widget.start();
            }}
        ''')
        return script

    def get_backend_configuration(self) -> dict:
        configuration = {
            'type': 'prologue',
            'logger_name': f'{self.config["backend_type"].capitalize()}Prologue',
            'image': self.image,
            'command': shlex.split(self.command),
        }
        if self.working_directory is not None:
            configuration['working_directory'] = self.working_directory
        return configuration
