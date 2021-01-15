import binascii
import bs4
import mkdocs
import pathlib
import re
import typing

from .widget import Widget


class TextViewerWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.file = self.tag['file']
        try:
            self.name = f'{binascii.hexlify(str(self.url).encode("utf-8")).decode("utf-8")}-{self.tag["name"]}'
            assert re.fullmatch(r'[0-9a-z\-]+', self.name) is not None
        except KeyError:
            self.name = self._hash_inputs(
                'text-viewer',
                str(self.url),
                str(index),
                self.file,
            )

    def __str__(self) -> str:
        return f'TextViewerWidget(name=\'{self.name}\', file=\'{self.file}\')'

    def get_static_files(self):
        return ['RoomConnection.js', 'TextViewerWidget.js', 'see-no-evil-monkey.png']

    def get_head_prepends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/TextViewerWidget.js')

        return super().get_head_prepends() + [
            script_room_connection,
            script_widget,
        ]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-text-viewer-{self.name}'
        return div

    def get_body_appends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            f'''roomConnection.subscribe("{self.name}", new TextViewerWidget(
                document.getElementById("widget-text-viewer-{self.name}"),
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
            'command': [self.config['backend_monitor_command'], self.file, '0.1', '5.0'],
        }
