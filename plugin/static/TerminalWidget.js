class TerminalWidget {
  constructor(element, sendMessage, workingDirectory) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.workingDirectory = workingDirectory;
    this.setupUi();
  }
  setupUi() {
    this.element.classList = ["interactive-widgets-terminal"];
    this.titleElement = document.createElement("div");
    this.titleElement.classList.add("title");
    this.titleElement.innerText = "";
    this.element.appendChild(this.titleElement);
    this.terminalElement = document.createElement("div");
    this.terminalElement.classList.add("terminal");
    this.terminalElement.innerText = "";
    this.element.appendChild(this.terminalElement);
    this.setupTerminal();
  }
  setupTerminal() {
    this.terminal = new Terminal({
      fontFamily: 'JetBrains Mono',
      theme: {
        foreground: '#000',
        background: '#eee',
        black: '#000',
        blue: '#2196f3',
        brightBlack: '#000',
        brightBlue: '#2196f3',
        brightCyan: '#00acc1',
        brightGreen: '#43a047',
        brightMagenta: '#9c27b0',
        brightRed: '#f44336',
        brightWhite: '#000',
        brightYellow: '#fdd835',
        cursor: '#000',
        cursorAccent: '#000',
        cyan: '#00acc1',
        green: '#43a047',
        magenta: '#9c27b0',
        red: '#f44336',
        selection: 'rgba(0, 0, 0, 0.25)',
        white: '#000',
        yellow: '#fdd835',
      },
    });
    this.fitAddon = new FitAddon.FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.open(this.terminalElement);
    this.terminal.onData(data => {
      this.sendMessage({
        stdin: btoa(data),
      });
    });
    this.terminal.onTitleChange(title => {
      this.titleElement.innerText = `Terminal: ${title}`;
    });
    this.terminal.onResize(size => {
      console.log('TODO');
      // this.sendMessage({
      //   size: size,
      // });
    });
    this.fitAddon.fit();
    window.addEventListener('resize', () => {
      this.fitAddon.fit();
    });
  }
  handleMessage(message) {
    this.terminal.write(atob(message.stdout));
  }
}
