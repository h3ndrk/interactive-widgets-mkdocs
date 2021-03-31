import bs4
import mkdocs
import pathlib
import typing

from .widget import Widget


class ImageViewerWidget(Widget):

    def __init__(self, config: mkdocs.config.base.Config, url: pathlib.PurePosixPath, soup: bs4.BeautifulSoup, index: int, tag: bs4.element.Tag):
        super().__init__(config, url, soup, index, tag)
        self.file = self.tag['file']
        self.mime = self.tag['mime']
        self.success_timeout = self.tag.get(
            'success-timeout',
            str(self.config['backend_monitor_default_success_timeout']),
        )
        self.failure_timeout = self.tag.get(
            'failure-timeout',
            str(self.config['backend_monitor_default_failure_timeout']),
        )
        self.name = self._hash_inputs(
            'image-viewer',
            str(self.url),
            str(index),
            self.file,
            self.mime,
            self.success_timeout,
            self.failure_timeout,
        )

    def __str__(self) -> str:
        return f'ImageViewerWidget(name={repr(self.name)}, file={repr(self.file)}, mime={repr(self.mime)})'

    def get_static_files(self):
        return ['ImageViewerWidget.js']

    def get_dependencies(self) -> typing.List[bs4.element.Tag]:
        script_widget = self.soup.new_tag('script')
        script_widget['src'] = self._relative('/ImageViewerWidget.js')
        return [script_widget]

    def get_replacement(self) -> bs4.element.Tag:
        div = self.soup.new_tag('div')
        div['id'] = f'widget-image-viewer-{self.name}'
        div['class'] = 'interactive-widgets-container'
        return div

    def get_instantiation(self) -> bs4.element.Tag:
        script = self.soup.new_tag('script')
        script.append(f'''
            {{
                roomConnection.addWidget();
                const widget = new ImageViewerWidget(
                    document.getElementById("widget-image-viewer-{self.name}"),
                    "{self._sanitize_javascript(self.file)}",
                    "{self._sanitize_javascript(self.mime)}",
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
