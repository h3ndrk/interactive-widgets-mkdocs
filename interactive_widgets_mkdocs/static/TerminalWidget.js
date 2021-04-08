class TerminalWidget extends Widget {
  constructor(element, command, workingDirectory) {
    super();
    this.element = element;
    this.command = command;
    this.workingDirectory = workingDirectory;
  }

  start() {
    this.setupUi();
  }

  async setupUi() {
    this.boxElement = document.createElement("div");
    this.element.appendChild(this.boxElement);
    this.boxElement.classList.add("interactive-widgets-box", "fixed", "interactive-widgets-terminal");

    this.captionElement = document.createElement("div");
    this.element.appendChild(this.captionElement);
    this.captionElement.classList.add("interactive-widgets-caption");
    this.captionElement.innerText = `Terminal: ${this.command} (${this.workingDirectory})`;

    this.regularFontElement = document.createElement("div");
    this.boxElement.appendChild(this.regularFontElement);
    this.regularFontElement.classList.add("show");
    this.regularFontElement.style.fontWeight = 400;
    this.regularFontElement.innerHTML = "&nbsp;";

    this.boldFontElement = document.createElement("div");
    this.boxElement.appendChild(this.boldFontElement);
    this.boldFontElement.classList.add("show");
    this.regularFontElement.style.fontWeight = 700;
    this.boldFontElement.innerHTML = "&nbsp;";

    await document.fonts.ready;

    while (this.boxElement.firstChild) {
      this.boxElement.removeChild(this.boxElement.firstChild);
    }

    const computedStyle = window.getComputedStyle(this.boxElement);
    this.terminal = new Terminal({
      fontFamily: computedStyle.getPropertyValue("font-family"),
      allowTransparency: true,
      theme: {
        foreground: "#000",
        background: "transparent",
        black: "#000",
        blue: "#2196f3",
        brightBlack: "#000",
        brightBlue: "#2196f3",
        brightCyan: "#00acc1",
        brightGreen: "#43a047",
        brightMagenta: "#9c27b0",
        brightRed: "#f44336",
        brightWhite: "#000",
        brightYellow: "#fdd835",
        cursor: "#000",
        cursorAccent: "#fff",
        cyan: "#00acc1",
        green: "#43a047",
        magenta: "#9c27b0",
        red: "#f44336",
        selection: "rgba(0, 0, 0, 0.25)",
        white: "#000",
        yellow: "#fdd835",
      },
    });

    this.fitAddon = new FitAddon.FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.open(this.boxElement);

    this.terminal.onData(data => {
      this.dispatchEvent(new CustomEvent("message", {
        detail: {
          stdin: this.btoa(data),
        },
      }));
    });

    this.terminal.onTitleChange(title => {
      this.captionElement.innerText = `Terminal: ${title}`;
    });

    this.terminal.onResize(size => {
      this.dispatchEvent(new CustomEvent("message", {
        detail: {
          size: size,
        },
      }));
    });

    this.fitAddon.fit();
    window.addEventListener("resize", () => {
      this.fitAddon.fit();
    });

    this.dispatchEvent(new Event("ready"));
  }

  handleMessage(message) {
    this.terminal.write(this.atob(message.stdout));
  }
}
