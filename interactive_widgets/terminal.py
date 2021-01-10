import bs4
import mkdocs
import pathlib
import re
import shlex
import typing

from .widget import Widget


class TerminalWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.image = self.tag['image']
        self.command = self.tag['command']
        self.working_directory = self.tag['working-directory']
        try:
            self.name = self.tag['name']
            assert re.fullmatch(r'[0-9a-z\-]+', self.name) is not None
        except KeyError:
            self.name = self._hash_inputs(
                'terminal',
                str(index),
                self.image,
                self.command,
                self.working_directory,
            )

    def __str__(self) -> str:
        return f'TerminalWidget(name=\'{self.name}\', image=\'{self.image}\', command=\'{self.command}\', working_directory=\'{self.working_directory}\')'

    def get_static_files(self):
        return [
            'RoomConnection.js',
            'TerminalWidget.js',
            'node_modules/xterm/lib',
            'node_modules/xterm-addon-fit/lib',
            'node_modules/xterm/css',
        ]

    def get_head_appends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/TerminalWidget.js')

        script_xterm = self.soup.new_tag('script')
        script_xterm['src'] = self._relative(
            '/node_modules/xterm/lib/xterm.js',
        )

        script_xterm_fit = self.soup.new_tag('script')
        script_xterm_fit['src'] = self._relative(
            '/node_modules/xterm-addon-fit/lib/xterm-addon-fit.js',
        )

        style_xterm = self.soup.new_tag('link')
        style_xterm['rel'] = 'stylesheet'
        style_xterm['href'] = self._relative(
            '/node_modules/xterm/css/xterm.css',
        )

        return [
            script_room_connection,
            script_widget,
            script_xterm,
            script_xterm_fit,
            style_xterm,
        ]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-terminal-{self.name}'
        return div

    def get_body_prepends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            'const roomConnection = new RoomConnection();',
        )
        return [script]

    def get_body_appends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            f'''roomConnection.subscribe("{self.name}", new TerminalWidget(
                document.getElementById("widget-terminal-{self.name}"),
                roomConnection.getSendMessageCallback("{self.name}"),
                "{self._sanitize_javascript(self.working_directory)}",
            ));''',
        )
        return [script]

    def get_backend_configuration(self) -> dict:
        return {
            'type': 'always',
            'logger_name': f'{self.config["backend_type"].capitalize()}Always',
            'image': self.image,
            'enable_tty': True,
            'command': shlex.split(self.command),
        }
