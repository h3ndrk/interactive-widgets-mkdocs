import binascii
import bs4
import mkdocs
import pathlib
import re
import shlex
import typing

from .widget import Widget


class ButtonWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.command = self.tag['command']
        self.image = self.tag['image']
        self.label = self.tag['label']
        try:
            self.name = f'{binascii.hexlify(str(self.url).encode("utf-8")).decode("utf-8")}-{self.tag["name"]}'
            assert re.fullmatch(r'[0-9a-z\-]+', self.name) is not None
        except KeyError:
            self.name = self._hash_inputs(
                'button',
                str(self.url),
                str(index),
                self.command,
                self.image,
                self.label,
            )

    def __str__(self) -> str:
        return f'ButtonWidget(name=\'{self.name}\', command=\'{self.command}\', image=\'{self.image}\', label=\'{self.label}\')'

    def get_static_files(self):
        return ['RoomConnection.js', 'ButtonWidget.js']

    def get_head_appends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/ButtonWidget.js')

        return [script_room_connection, script_widget]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-button-{self.name}'
        return div

    def get_body_appends(self) -> typing.List[bs4.element.Tag]:
        script = self.soup.new_tag('script')
        script.append(
            f'''roomConnection.subscribe("{self.name}", new ButtonWidget(
                document.getElementById("widget-button-{self.name}"),
                roomConnection.getSendMessageCallback("{self.name}"),
                "{self._sanitize_javascript(self.command)}",
                "{self._sanitize_javascript(self.label)}",
            ));''',
        )
        return [script]

    def get_backend_configuration(self) -> dict:
        return {
            'type': 'once',
            'logger_name': f'{self.config["backend_type"].capitalize()}Once',
            'image': self.image,
            'command': shlex.split(self.command),
        }
