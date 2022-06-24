import bs4
import json
import mkdocs
import os
import pathlib
import shutil

from .button import ButtonWidget
from .epilogue import EpilogueWidget
from .image_viewer import ImageViewerWidget
from .prologue import PrologueWidget
from .terminal import TerminalWidget
from .text_editor import TextEditorWidget
from .text_viewer import TextViewerWidget


log = mkdocs.plugins.log.getChild('interactive-widgets')


class Plugin(mkdocs.plugins.BasePlugin):

    config_scheme = (
        ('nginx_server_name', mkdocs.config.config_options.Type(
            str, default='localhost')),
        ('nginx_port_http', mkdocs.config.config_options.Type(int, default=80)),
        ('nginx_port_https', mkdocs.config.config_options.Type(int, default=443)),
        ('nginx_https_certificate', mkdocs.config.config_options.Type(str, default=None)),
        ('nginx_https_certificate_key',
         mkdocs.config.config_options.Type(str, default=None)),
        ('backend_host', mkdocs.config.config_options.Type(str, default='*')),
        ('backend_port', mkdocs.config.config_options.Type(int, default=80)),
        ('backend_type', mkdocs.config.config_options.Type(str, default='docker')),
        ('backend_logging_level', mkdocs.config.config_options.Choice(
            ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='DEBUG',
        )),
        ('backend_monitor_image', mkdocs.config.config_options.Type(
            str,
            default='interactive-widgets-monitor',
        )),
        ('backend_monitor_command', mkdocs.config.config_options.Type(
            str,
            default='interactive-widgets-monitor',
        )),
        ('backend_monitor_default_success_timeout',
         mkdocs.config.config_options.Type(float, default=0.1)),
        ('backend_monitor_default_failure_timeout',
         mkdocs.config.config_options.Type(float, default=5.0)),
        ('backend_default_memory_limit_bytes',
         mkdocs.config.config_options.Type(int, default=128*1024*1024)),
        ('backend_default_cpu_limit',
         mkdocs.config.config_options.Type(float, default=1.0)),
        ('backend_default_pids_limit',
         mkdocs.config.config_options.Type(int, default=128)),
    )

    def on_config(self, config: mkdocs.config.base.Config, *args, **kwargs) -> mkdocs.config.base.Config:
        config['site_dir_parent'] = pathlib.Path(config['site_dir'])
        config['site_dir'] = pathlib.Path(config['site_dir']) / 'static'
        return config

    def on_pre_build(self, *args, **kwargs):
        self.backend_configuration = {
            'host': self.config['backend_host'],
            'port': self.config['backend_port'],
            'logger_name': 'Server',
            'logging_level': self.config['backend_logging_level'],
            'context': {
                'type': self.config['backend_type'],
                'logger_name': f'{self.config["backend_type"].capitalize()}Context',
            },
            'pages': {},
        }
        self.static_files = set()

    def on_post_page(self, output: str, page: mkdocs.structure.pages.Page, *args, **kwargs):
        log.info(
            f'Building {page} with backend type: {self.config["backend_type"]}',
        )
        soup = bs4.BeautifulSoup(output, 'html.parser')

        widgets = [
            {
                'x-button': ButtonWidget,
                'x-epilogue': EpilogueWidget,
                'x-image-viewer': ImageViewerWidget,
                'x-prologue': PrologueWidget,
                'x-terminal': TerminalWidget,
                'x-text-editor': TextEditorWidget,
                'x-text-viewer': TextViewerWidget,
            }[tag.name](
                self.config,
                pathlib.PurePosixPath(page.url),
                soup,
                index,
                tag,
            )
            for index, tag in enumerate(soup.find_all([
                'x-button',
                'x-epilogue',
                'x-image-viewer',
                'x-prologue',
                'x-terminal',
                'x-text-editor',
                'x-text-viewer',
            ]))
        ]

        if len(widgets) > 0:
            page_url = pathlib.PurePosixPath('/') / page.url
            self.backend_configuration['pages'][str(page_url)] = {
                'type': self.config['backend_type'],
                'logger_name_page': 'Page',
                'logger_name_room_connection': 'RoomConnection',
                'logger_name_room': f'{self.config["backend_type"].capitalize()}Room',
                'executors': {},
            }

            current_head = soup.find(string=lambda text: isinstance(
                text, bs4.Comment) and text.string.strip() == 'interactive-widgets')
            if current_head is None:
                current_head = soup.select('head > *:last-child')[0]
            assert current_head is not None

            script_redirect = soup.new_tag('script')
            script_redirect.append('''
                const currentUrl = new URL(window.location);
                const currentUrlSearchParams = new URLSearchParams(currentUrl.search);
                const currentRoomName = currentUrlSearchParams.get("roomName");
                // https://gist.github.com/johnelliott/cf77003f72f889abbc3f32785fa3df8d
                if (currentRoomName === null || !currentRoomName.match(new RegExp(/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i))) {
                    // https://gist.github.com/outbreak/316637cde245160c2579898b21837c1c
                    const getRandomSymbol = (symbol) => {
                        var array;
                        if (symbol === "y") {
                        array = ["8", "9", "a", "b"];
                        return array[Math.floor(Math.random() * array.length)];
                        }
                        array = new Uint8Array(1);
                        window.crypto.getRandomValues(array);
                        return (array[0] % 16).toString(16);
                    }
                    const newRoomName = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, getRandomSymbol);
                    currentUrlSearchParams.set("roomName", newRoomName);
                    currentUrl.search = currentUrlSearchParams;
                    window.location.replace(currentUrl.toString());
                }
            ''')
            current_head.insert_after(script_redirect)
            current_head = script_redirect

            script_room_connection = soup.new_tag('script')
            script_room_connection['src'] = os.path.relpath(
                '/RoomConnection.js',
                page_url,
            )
            current_head.insert_after(script_room_connection)
            current_head = script_room_connection
            self.static_files |= set(['RoomConnection.js'])

            script_room_connection_construction = soup.new_tag('script')
            script_room_connection_construction.append(
                'const roomConnection = new RoomConnection(currentRoomName);',
            )
            soup.body.insert(0, script_room_connection_construction)

            for widget in widgets:
                log.info(f'Processing {widget}...')
                replacement = widget.get_replacement()
                parent_tag = widget.tag.parent
                assert parent_tag.name == 'p'
                if replacement is not None:
                    parent_tag.replace_with(replacement)
                    replacement.insert_after(widget.get_instantiation())
                else:
                    parent_tag.insert_after(widget.get_instantiation())
                    parent_tag.extract()
                for tag in widget.get_dependencies():
                    if tag not in soup.head:
                        current_head.insert_after(tag)
                        current_head = tag
                self.backend_configuration['pages'][str(page_url)]['executors'][widget.name] = widget.get_backend_configuration(
                )
                self.static_files |= set(widget.get_static_files())

            script_room_connection_ready = soup.new_tag('script')
            script_room_connection_ready.append(
                'roomConnection.readyForConnecting();',
            )
            soup.body.append(script_room_connection_ready)

            return soup.encode_contents(formatter='html5').decode()

        log.info(f'No widgets in {page}, building as static page')
        return output

    def on_post_build(self, config: mkdocs.config.base.Config, *args, **kwargs):
        if len(self.backend_configuration['pages']) > 0:
            log.info('Writing interactive-widgets-backend.json...')
            with (config['site_dir_parent'] / 'interactive-widgets-backend.json').open('w') as f:
                json.dump(self.backend_configuration, f, indent=2)

            log.info('Copying static files...')
            for static_file in self.static_files:
                source_static_file = pathlib.Path(
                    __file__).parent / 'static' / pathlib.Path(static_file)
                target_static_file = config['site_dir'] / \
                    pathlib.Path(static_file)
                target_static_file.parent.mkdir(parents=True, exist_ok=True)
                if source_static_file.is_file():
                    shutil.copy(
                        source_static_file,
                        target_static_file,
                    )
                else:
                    shutil.copytree(
                        source_static_file,
                        target_static_file,
                        dirs_exist_ok=True,
                    )

        log.info('Writing interactive-widgets-nginx.conf...')
        with (config['site_dir_parent'] / 'interactive-widgets-nginx.conf').open('w') as f:
            if len(self.backend_configuration['pages']) > 0:
                print('upstream backend {', file=f)
                print('    server interactive-widgets-backend;', file=f)
                print('}', file=f)
            print('server {', file=f)
            print('    listen       80;', file=f)
            print(
                f'    server_name  {self.config["nginx_server_name"]};', file=f)
            print('    location / {', file=f)
            print('        root /usr/share/nginx/html;', file=f)
            print('        index index.html index.htm;', file=f)
            print('    }', file=f)
            for page_url in self.backend_configuration['pages'].keys():
                websocket_url = pathlib.PurePosixPath(page_url) / 'ws'
                proxy_url = f'http://backend{websocket_url}'
                print(f'    location = {websocket_url} {{', file=f)
                print(f'        proxy_pass {proxy_url};', file=f)
                print('        proxy_http_version 1.1;', file=f)
                print('        proxy_set_header Upgrade $http_upgrade;', file=f)
                print('        proxy_set_header Connection "Upgrade";', file=f)
                print('        proxy_set_header Host $host;', file=f)
                print('    }', file=f)
            print('}', file=f)
            if self.config['nginx_https_certificate'] is not None and self.config['nginx_https_certificate_key'] is not None:
                print('server {', file=f)
                print('    listen       443 ssl;', file=f)
                print(f'    ssl_certificate /tmp/nginx.crt;', file=f)
                print(f'    ssl_certificate_key /tmp/nginx.key;', file=f)
                print(
                    f'    server_name  {self.config["nginx_server_name"]};', file=f)
                print('    location / {', file=f)
                print('        root /usr/share/nginx/html;', file=f)
                print('        index index.html index.htm;', file=f)
                print('    }', file=f)
                for page_url in self.backend_configuration['pages'].keys():
                    websocket_url = pathlib.PurePosixPath(page_url) / 'ws'
                    proxy_url = f'http://backend{websocket_url}'
                    print(f'    location = {websocket_url} {{', file=f)
                    print(f'        proxy_pass {proxy_url};', file=f)
                    print('        proxy_http_version 1.1;', file=f)
                    print('        proxy_set_header Upgrade $http_upgrade;', file=f)
                    print('        proxy_set_header Connection "Upgrade";', file=f)
                    print('        proxy_set_header Host $host;', file=f)
                    print('    }', file=f)
                print('}', file=f)

        log.info('Writing Dockerfile...')
        with (config['site_dir_parent'] / 'Dockerfile').open('w') as f:
            print('FROM nginx', file=f)
            print(
                'RUN rm /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*', file=f)
            print('COPY interactive-widgets-nginx.conf /etc/nginx/conf.d/', file=f)
            print('COPY static/ /usr/share/nginx/html/', file=f)

        log.info('Writing docker-compose.yaml...')
        with (config['site_dir_parent'] / 'docker-compose.yaml').open('w') as f:
            print('version: "3"', file=f)
            print('services:', file=f)
            print('  interactive-widgets-nginx:', file=f)
            print('    image: interactive-widgets-nginx', file=f)
            print('    build: .', file=f)
            print('    ports:', file=f)
            print(f'    - "{self.config["nginx_port_http"]}:80"', file=f)
            if self.config['nginx_https_certificate'] is not None and self.config['nginx_https_certificate_key'] is not None:
                print(f'    - "{self.config["nginx_port_https"]}:443"', file=f)
                print('    volumes:', file=f)
                print(
                    f'      - "{self.config["nginx_https_certificate"]}:/tmp/nginx.crt"', file=f)
                print(
                    f'      - "{self.config["nginx_https_certificate_key"]}:/tmp/nginx.key"', file=f)
            if len(self.backend_configuration['pages']) > 0:
                print('  interactive-widgets-backend:', file=f)
                print('    image: interactive-widgets-backend', file=f)
                print('    volumes:', file=f)
                print(
                    '      - "./interactive-widgets-backend.json:/usr/src/app/interactive-widgets-backend.json"', file=f)
                print('      - "/var/run/docker.sock:/var/run/docker.sock"', file=f)
                print(
                    '    command: ["interactive-widgets-backend", "interactive-widgets-backend.json"]', file=f)
