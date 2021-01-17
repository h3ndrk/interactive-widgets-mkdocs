import bs4
import mkdocs
import pathlib
import shlex
import typing

from .widget import Widget


class ButtonWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.command = self.tag['command']
        self.image = self.tag['image']
        self.label = self.tag['label']
        self.working_directory = self.tag.get('working-directory', None)
        self.name = self._hash_inputs(
            'button',
            str(self.url),
            str(index),
            self.command,
            self.image,
            self.label,
            self.working_directory if self.working_directory is not None else '',
        )

    def __str__(self) -> str:
        return f'ButtonWidget(name={repr(self.name)}, command={repr(self.command)}, image={repr(self.image)}, label={repr(self.label)}, working_directory={repr(self.working_directory)})'

    def get_static_files(self):
        return ['RoomConnection.js', 'ButtonWidget.js']

    def get_head_prepends(self) -> typing.List[bs4.element.Tag]:
        script_room_connection = self.soup.new_tag('script')
        script_room_connection['src'] = self._relative('/RoomConnection.js')

        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/ButtonWidget.js')

        return super().get_head_prepends() + [
            script_room_connection,
            script_widget,
        ]

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
        configuration = {
            'type': 'once',
            'logger_name': f'{self.config["backend_type"].capitalize()}Once',
            'image': self.image,
            'command': shlex.split(self.command),
        }
        if self.working_directory is not None:
            configuration['working_directory'] = self.working_directory
        return configuration
