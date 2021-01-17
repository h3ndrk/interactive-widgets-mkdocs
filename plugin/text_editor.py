import bs4
import mkdocs
import pathlib
import typing

from .widget import Widget


class TextEditorWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.file = self.tag['file']
        self.success_timeout = self.tag.get(
            'success-timeout',
            str(self.config['backend_monitor_default_success_timeout']),
        )
        self.failure_timeout = self.tag.get(
            'failure-timeout',
            str(self.config['backend_monitor_default_failure_timeout']),
        )
        self.name = self._hash_inputs(
            'text-editor',
            str(self.url),
            str(index),
            self.file,
            self.success_timeout,
            self.failure_timeout,
        )

    def __str__(self) -> str:
        return f'TextEditorWidget(name=\'{self.name}\', file=\'{self.file}\')'

    def get_static_files(self):
        return [
            'RoomConnection.js',
            'TextEditorWidget.js',
            'node_modules/codemirror/addon',
            'node_modules/codemirror/keymap',
            'node_modules/codemirror/lib',
            'node_modules/codemirror/mode',
            'node_modules/codemirror/theme',
            'see-no-evil-monkey.png',
        ]

    def get_head_prepends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/TextEditorWidget.js')

        script_codemirror = self.soup.new_tag('script')
        script_codemirror['src'] = self._relative(
            '/node_modules/codemirror/lib/codemirror.js',
        )

        style_codemirror = self.soup.new_tag('link')
        style_codemirror['rel'] = 'stylesheet'
        style_codemirror['href'] = self._relative(
            '/node_modules/codemirror/lib/codemirror.css',
        )

        return super().get_head_prepends() + [
            script_room_connection,
            script_widget,
            script_codemirror,
            style_codemirror,
        ]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-text-editor-{self.name}'
        return div

    def get_body_appends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            f'''roomConnection.subscribe("{self.name}", new TextEditorWidget(
                document.getElementById("widget-text-editor-{self.name}"),
                roomConnection.getSendMessageCallback("{self.name}"),
                "{self._sanitize_javascript(self.file)}",
            ));''',
        )
        return [script]

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
        }
