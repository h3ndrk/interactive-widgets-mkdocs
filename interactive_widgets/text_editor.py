import bs4
import mkdocs
import pathlib
import re
import typing

from .widget import Widget


class TextEditorWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.file = self.tag['file']
        try:
            self.name = self.tag['name']
            assert re.fullmatch(r'[0-9a-z\-]+', self.name) is not None
        except KeyError:
            self.name = self._hash_inputs(
                'text-editor',
                str(index),
                self.file,
            )

    def __str__(self) -> str:
        return f'TextEditorWidget({self.name})'

    def get_head_appends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/js/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/js/TextEditorWidget.js')

        script_codemirror = self.soup.new_tag('script')
        script_codemirror['src'] = self._relative(
            '/js/node_modules/codemirror/lib/codemirror.js',
        )

        style_codemirror = self.soup.new_tag('link')
        style_codemirror['rel'] = 'stylesheet'
        style_codemirror['href'] = self._relative(
            '/js/node_modules/codemirror/lib/codemirror.css',
        )

        return [
            script_room_connection,
            script_widget,
            script_codemirror,
            style_codemirror,
        ]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-text-editor-{self.name}'
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
            f'''roomConnection.subscribe(new TextEditorWidget(
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
            'image': 'inter-md-monitor',
            'enable_tty': True,
            'command': ['inter-md-monitor', self.file, '0.1', '5.0'],
        }
