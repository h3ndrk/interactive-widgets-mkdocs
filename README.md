# interactive-widgets-mkdocs

This repository contains an [MkDocs](https://mkdocs.org) plugin for converting custom HTML tags embedded in the [Markdown](https://daringfireball.net/projects/markdown/) of MkDocs pages into interactive widgets. The plugin relies on [interactive-widgets-backend](https://github.com/h3ndrk/interactive-widgets-backend/) as the backend for providing isolated Docker containers for running the widgets.

## Configuration

See the [MkDocs documentation about how to use plugins](https://www.mkdocs.org/user-guide/plugins/#using-plugins) which shows how to supply configuration values to this plugin.

- `nginx_port` (type: `int`, default: `80`): Port to use for the generated Nginx container in `docker-compose.yml`
- `backend_host` (type: `str`, default: `'*'`): Host address for HTTP server of backend for `interactive-widgets-backend.json`
- `backend_port` (type: `int`, default: `80`): Port for HTTP server of backend for `interactive-widgets-backend.json`
- `backend_type` (type: `str`, default: `'docker'`): Type of widget executors to use in backend for `interactive-widgets-backend.json`
- `backend_logging_level` (type: one of `'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'`, `'CRITICAL'`, default: `'DEBUG'`): Logging level to use in backend for `interactive-widgets-backend.json`
- `backend_monitor_image` (type: `str`, default: `'interactive-widgets-monitor'`): Docker image to use for monitor containers in backend for `interactive-widgets-backend.json`
- `backend_monitor_command` (type: `str`, default: `'interactive-widgets-monitor'`): Command to execute in Docker container for monitor containers in backend for `interactive-widgets-backend.json`
- `backend_monitor_default_success_timeout` (type: `float`, default: `0.1`): Success timeout in seconds for monitor containers in backend for `interactive-widgets-backend.json`
- `backend_monitor_default_failure_timeout` (type: `float`, default: `5.0`): Failure timeout in seconds for monitor containers in backend for `interactive-widgets-backend.json`

For all `backend_*`-options, see [interactive-widgets-backend for documentation](https://github.com/h3ndrk/interactive-widgets-backend/).

## HTML Tag Reference

The following HTML tags can be used in any Markdown page processed with the *interactive-widgets-mkdocs* plugin. Special characters within HTML tag attributes need to be escaped. Symptomes of lacking escaping may be missing page contents.

### `<x-button />`

Displays a button which executes a given command.

Attributes:

- `command`: The command to execute in a new container.
- `image`: The Docker image to use to start the container from.
- `label`: The label for the frontend button.
- `working-directory`: The working directory to execute the given command in.

The frontend shows a button with the given *label*. The *command* is also displayed. If the command outputs to the standard output, it will be rendered in the frontend. During execution of the command, any additional execution attempts are ignored.

Clicking the button in the frontend results in starting a Docker container in the backend and waiting for the termination. During the execution, output is transmitted to all connected frontend clients and additional execution requests are ignored.

Example: `<x-button command="date" image="ubuntu:latest" label="Print date" working-directory="/data" />`

### `<x-epilogue />`

Executes a given command at room tear down.

Attributes:

- `command`: The command to execute in a new container.
- `image`: The Docker image to use to start the container from.
- `working-directory`: The working directory to execute the given command in.

The frontend shows the given *command*. If the command outputs to the standard output, it will be rendered in the frontend.

The backend runs the given *command* in a new Docker container during room tear down and waits for the termination.

Example: `<x-epilogue command="date" image="ubuntu:latest" working-directory="/data" />`

### `<x-image-viewer />`

Displays and monitors a given image file.

Attributes:

- `file`: The path of the image file to monitor for changes.
- `mime`: The [MIME](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) type of the image.
- `success-timeout` (optional, default from configuration value `backend_monitor_default_success_timeout`): The time to wait after a file change event.
- `failure-timeout` (optional, default from configuration value `backend_monitor_default_failure_timeout`): The time to wait before retrying after a file read failure.

The frontend shows the image or an error message if an error occurred. In the caption it displays the given image *file* path.

The backend monitors the given image *file* for changes and sends the contents or error messages to the frontend. It runs the monitoring process in new long-running Docker container (configurable via configuration values `backend_monitor_image` and `backend_monitor_command`).

Example: `<x-image-viewer file="/data/image.png" mime="image/png" success-timeout="0.1" failure-timeout="5" />`

### `<x-prologue />`

Executes a given command at room instantiation.

Attributes:

- `command`: The command to execute in a new container.
- `image`: The Docker image to use to start the container from.
- `working-directory`: The working directory to execute the given command in.

The frontend shows the given *command*. If the command outputs to the standard output, it will be rendered in the frontend.

The backend runs the given *command* in a new Docker container during room instantiation and waits for the termination.

Example: `<x-prologue command="date" image="ubuntu:latest" working-directory="/data" />`

### `<x-terminal />`

Execute a given command in a pseudo-terminal and display the output.

Attributes:

- `image`: The Docker image to use to start the container from.
- `command`: The command to execute in a new container.
- `working-directory`: The working directory to execute the given command in.

The frontend shows a terminal widget (behaves like a normal terminal) and also displays the current terminal title if a title is set (else the given *command* and *working-directory* is shown).

The backend executes the given *command* in the given *working-directory* in a new long-running and restarting Docker container. It sends the containers output to the frontend and receives the input for the container.

Example: `<x-terminal image="ubuntu:latest" command="/bin/bash" working-directory="/data" />`

### `<x-text-editor />`

Displays, monitors and allows to edit a given text file.

Attributes:

- `file`: The path of the text file to monitor for changes.
- `mode` (optional): The [CodeMirror Language Mode](https://codemirror.net/mode/) to use for e.g. syntax highlighting for the text. It must be a string corresponding to a directory name in the [`mode/`-directory](https://github.com/codemirror/CodeMirror/tree/master/mode).
- `success-timeout` (optional, default from configuration value `backend_monitor_default_success_timeout`): The time to wait after a file change event.
- `failure-timeout` (optional, default from configuration value `backend_monitor_default_failure_timeout`): The time to wait before retrying after a file read failure.

The frontend shows the text editor or an error message if an error occurred. In the caption it displays the given text *file* path. Three buttons allow to create or truncate the monitored *file*, save the current editor contents to that *file*, or delete the monitored *file*.

The backend monitors the given text *file* for changes and sends the contents or error messages to the frontend. The backend receives commands for writing or deleting the given text *file*. It runs the monitoring process in new long-running Docker container (configurable via configuration values `backend_monitor_image` and `backend_monitor_command`).

Example: `<x-text-editor file="/data/example.py" mode="python" success-timeout="0.1" failure-timeout="5" />`

### `<x-text-viewer />`

Displays and monitors a given text file.

Attributes:

- `file`: The path of the text file to monitor for changes.
- `mode` (optional): The [CodeMirror Language Mode](https://codemirror.net/mode/) to use for e.g. syntax highlighting for the text. It must be a string corresponding to a directory name in the [`mode/`-directory](https://github.com/codemirror/CodeMirror/tree/master/mode).
- `success-timeout` (optional, default from configuration value `backend_monitor_default_success_timeout`): The time to wait after a file change event.
- `failure-timeout` (optional, default from configuration value `backend_monitor_default_failure_timeout`): The time to wait before retrying after a file read failure.

The frontend shows the text or an error message if an error occurred. In the caption it displays the given text *file* path.

The backend monitors the given text *file* for changes and sends the contents or error messages to the frontend. It runs the monitoring process in new long-running Docker container (configurable via configuration values `backend_monitor_image` and `backend_monitor_command`).

Example: `<x-text-viewer file="/data/example.py" mode="python" success-timeout="0.1" failure-timeout="5" />`

## Usage

This section covers all necessary steps to build a complete and deployable website based on *interactive-widgets-mkdocs*.

- Optional: Setup virtual environment for Python
- Install MkDocs and this *interactive-widgets-mkdocs* plugin: `pip install ./` (or `pip install --editable ./` for development)
- Write pages according to [MkDocs guide on how to write pages](https://www.mkdocs.org/user-guide/writing-your-docs/). In the `mkdocs.yml`, enable the `interactive_widgets` plugin.
- Build website with MkDocs: `mkdocs build`
- Ensure that the Docker images *interactive-widgets-backend* and *interactive-widgets-monitor* are present. If not, build them according to the [interactive-widgets-backend documentation](https://github.com/h3ndrk/interactive-widgets-backend/).
- Ensure that all Docker images referenced in the Markdown pages (e.g. in the `image` attributes of the HTML tags of the widgets) are present.
- Optional: Adjust the configuration in the generated files in the `site/`-directory.
- In the `site/`-directory, start the website via `docker-compose up --build` (`--build` is optional but ensures that the static files are correctly built into a Docker container *interactive-widgets-nginx*).
- Connect to `http://localhost` to see the started page. (You may need to clear your cache.)

## License

MIT
