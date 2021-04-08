import bs4
import mkdocs
import pathlib
import shlex
import typing

from .widget import Widget


class TerminalWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.image = self.tag['image']
        self.command = self.tag['command']
        self.working_directory = self.tag.get('working-directory', None)
        self.memory_limit_bytes = self.tag.get(
            'memory-limit-bytes', self.config['backend_default_memory_limit_bytes'])
        self.cpu_limit = self.tag.get(
            'cpu-limit', self.config['backend_default_cpu_limit'])
        self.pids_limit = self.tag.get(
            'pids-limit', self.config['backend_default_pids_limit'])
        self.name = self._hash_inputs(
            'terminal',
            str(self.url),
            str(index),
            self.image,
            self.command,
            self.working_directory if self.working_directory is not None else '',
        )

    def __str__(self) -> str:
        return f'TerminalWidget(name={repr(self.name)}, image={repr(self.image)}, command={repr(self.command)}, working_directory={repr(self.working_directory)})'

    def get_static_files(self):
        return [
            'TerminalWidget.js',
            'Widget.js',
            'node_modules/xterm/lib',
            'node_modules/xterm-addon-fit/lib',
            'node_modules/xterm/css',
        ]

    def get_dependencies(self) -> typing.List[bs4.element.Tag]:
        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/Widget.js')

        script_terminal_widget = self.soup.new_tag('script')
        script_terminal_widget['src'] = self._relative('/TerminalWidget.js')

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
            script_widget,
            script_terminal_widget,
            script_xterm,
            script_xterm_fit,
            style_xterm,
        ]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-terminal-{self.name}'
        div['class'] = 'interactive-widgets-container'
        return div

    def get_instantiation(self) -> bs4.element.Tag:
        script = self.soup.new_tag('script')
        script.append(f'''
            {{
                roomConnection.addWidget();
                const widget = new TerminalWidget(
                    document.getElementById("widget-terminal-{self.name}"),
                    "{self._sanitize_javascript(self.command)}",
                    "{self._sanitize_javascript(self.working_directory)}",
                );
                widget.addEventListener("ready", function _listener() {{
                    roomConnection.markWidgetReady();
                    widget.removeEventListener("ready", _listener);
                }});
                widget.addEventListener("message", event => {{
                    roomConnection.sendMessage("{self.name}", event.detail);
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
            'type': 'always',
            'logger_name': f'{self.config["backend_type"].capitalize()}Always',
            'image': self.image,
            'enable_tty': True,
            'command': shlex.split(self.command),
            'memory_limit_bytes': self.memory_limit_bytes,
            'cpu_limit': self.cpu_limit,
            'pids_limit': self.pids_limit,
        }
        if self.working_directory is not None:
            configuration['working_directory'] = self.working_directory
        return configuration
