import bs4
import mkdocs
import pathlib
import typing

from .widget import Widget


class TextEditorWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.file = self.tag['file']
        self.mode = self.tag.get('mode')
        self.success_timeout = self.tag.get(
            'success-timeout',
            str(self.config['backend_monitor_default_success_timeout']),
        )
        self.failure_timeout = self.tag.get(
            'failure-timeout',
            str(self.config['backend_monitor_default_failure_timeout']),
        )
        self.memory_limit_bytes = self.tag.get(
            'memory-limit-bytes', self.config['backend_default_memory_limit_bytes'])
        self.cpu_limit = self.tag.get(
            'cpu-limit', self.config['backend_default_cpu_limit'])
        self.pids_limit = self.tag.get(
            'pids-limit', self.config['backend_default_pids_limit'])
        self.name = self._hash_inputs(
            'text-editor',
            str(self.url),
            str(index),
            self.file,
            self.success_timeout,
            self.failure_timeout,
        )

    def __str__(self) -> str:
        return f'TextEditorWidget(name={repr(self.name)}, file={repr(self.file)})'

    def get_static_files(self):
        return [
            'TextEditorWidget.js',
            'Widget.js',
            'node_modules/codemirror/addon',
            'node_modules/codemirror/keymap',
            'node_modules/codemirror/lib',
            'node_modules/codemirror/mode',
            'node_modules/codemirror/theme',
        ]

    def get_dependencies(self) -> typing.List[bs4.element.Tag]:
        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/Widget.js')

        script_text_editor_widget = self.soup.new_tag('script')
        script_text_editor_widget['src'] = self._relative('/TextEditorWidget.js')

        script_codemirror = self.soup.new_tag('script')
        script_codemirror['src'] = self._relative(
            '/node_modules/codemirror/lib/codemirror.js',
        )

        style_codemirror = self.soup.new_tag('link')
        style_codemirror['rel'] = 'stylesheet'
        style_codemirror['href'] = self._relative(
            '/node_modules/codemirror/lib/codemirror.css',
        )

        script_codemirror_mode = []
        if self.mode is not None:
            script_codemirror_mode.append(self.soup.new_tag('script'))
            script_codemirror_mode[0]['src'] = self._relative(
                f'/node_modules/codemirror/mode/{self.mode}/{self.mode}.js',
            )

        return [
            script_widget,
            script_text_editor_widget,
            script_codemirror,
            style_codemirror,
        ] + script_codemirror_mode

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-text-editor-{self.name}'
        div['class'] = 'interactive-widgets-container'
        return div

    def get_instantiation(self) -> bs4.element.Tag:
        script = self.soup.new_tag('script')
        mode_parameter = f'"{self._sanitize_javascript(self.mode)}"' if self.mode is not None else 'null'
        script.append(f'''
            {{
                roomConnection.addWidget();
                const widget = new TextEditorWidget(
                    document.getElementById("widget-text-editor-{self.name}"),
                    "{self._sanitize_javascript(self.file)}",
                    {mode_parameter},
                );
                widget.addEventListener("ready", function _listener() {{
                    roomConnection.markWidgetReady();
                    widget.removeEventListener("ready", _listener);
                }});
                widget.addEventListener("message", event => {{
                    roomConnection.sendMessage("{self.name}", event.detail);
                }});
                roomConnection.addEventListener("connect", event => {{
                    widget.handleOpen();
                }});
                roomConnection.addEventListener("disconnect", event => {{
                    widget.handleClose();
                }});
                roomConnection.addEventListener("{self.name}", event => {{
                    widget.handleMessage(event.detail);
                }});
                widget.start();
            }}
        ''')
        return script

    def get_backend_configuration(self) -> dict:
        return {
            'type': 'always',
            'logger_name': f'{self.config["backend_type"].capitalize()}Always',
            'image': self.config['backend_monitor_image'],
            'command': [
                self.config['backend_monitor_command'],
                self.file,
                self.success_timeout,
                self.failure_timeout,
            ],
            'memory_limit_bytes': self.memory_limit_bytes,
            'cpu_limit': self.cpu_limit,
            'pids_limit': self.pids_limit,
        }
