class ButtonWidget extends Widget {
  constructor(element, command, label) {
    super();
    this.element = element;
    this.command = command;
    this.label = label;
    this.open = false;
    this.running = false;
    this.stdoutBuffer = "";
    this.stderrBuffer = "";
  }

  start() {
    this.setupUi();
    this.dispatchEvent(new Event("ready"));
  }

  setupUi() {
    this.boxElement = document.createElement("div");
    this.element.appendChild(this.boxElement);
    this.boxElement.classList.add("interactive-widgets-box", "shrink", "interactive-widgets-button", "empty");

    this.buttonsElement = document.createElement("div");
    this.boxElement.appendChild(this.buttonsElement);
    this.buttonsElement.classList.add("buttons", "show");

    this.buttonElement = document.createElement("button");
    this.buttonsElement.appendChild(this.buttonElement);
    this.buttonElement.disabled = !this.open || this.running;
    this.buttonElement.innerText = this.label;
    this.buttonElement.addEventListener("click", () => {
      if (this.open) {
        this.dispatchEvent(new CustomEvent("message", { detail: null }));
      }
    });

    this.commandElement = document.createElement("div");
    this.boxElement.appendChild(this.commandElement);
    this.commandElement.classList.add("command", "show");
    this.commandElement.innerText = this.command;

    this.outputsElement = document.createElement("div");
    this.boxElement.appendChild(this.outputsElement);
    this.outputsElement.classList.add("outputs");
  }

  handleOpen() {
    this.open = true;
    this.buttonElement.disabled = !this.open || this.running;
  }

  handleClose() {
    this.open = false;
    this.buttonElement.disabled = !this.open || this.running;
  }

  handleMessage(message) {
    switch (message.type) {
      case "started": {
        this.running = true;
        this.buttonElement.disabled = !this.open || this.running;
        while (this.outputsElement.firstChild) {
          this.outputsElement.removeChild(this.outputsElement.firstChild);
        }
        this.boxElement.classList.add("empty");
        this.outputsElement.classList.remove("show");
        break;
      }
      case "output": {
        if ("stdout" in message) {
          this.stdoutBuffer += this.atob(message.stdout);
          for (let newlinePosition = this.stdoutBuffer.indexOf("\n"); newlinePosition !== -1; newlinePosition = this.stdoutBuffer.indexOf("\n")) {
            const currentLine = this.stdoutBuffer.substr(0, newlinePosition);
            this.boxElement.classList.remove("empty");
            this.outputsElement.classList.add("show");
            const lineElement = document.createElement("pre");
            lineElement.classList.add("line", "stdout");
            console.log(currentLine);
            lineElement.innerText = currentLine;
            this.outputsElement.appendChild(lineElement);
            this.stdoutBuffer = this.stdoutBuffer.substr(newlinePosition + 1, this.stdoutBuffer.length - newlinePosition - 1);
          }
        } else if ("stderr" in message) {
          this.stderrBuffer += this.atob(message.stderr);
          for (let newlinePosition = this.stderrBuffer.indexOf("\n"); newlinePosition !== -1; newlinePosition = this.stderrBuffer.indexOf("\n")) {
            const currentLine = this.stderrBuffer.substr(0, newlinePosition);
            this.boxElement.classList.remove("empty");
            this.outputsElement.classList.add("show");
            const lineElement = document.createElement("pre");
            lineElement.classList.add("line", "stderr");
            console.log(currentLine);
            lineElement.innerText = currentLine;
            this.outputsElement.appendChild(lineElement);
            this.stderrBuffer = this.stderrBuffer.substr(newlinePosition + 1, this.stderrBuffer.length - newlinePosition - 1);
          }
        }
        break;
      }
      case "finished": {
        this.running = false;
        this.buttonElement.disabled = !this.open || this.running;
        break;
      }
      case "errored": {
        this.running = false;
        this.buttonElement.disabled = !this.open || this.running;
        this.boxElement.classList.remove("empty");
        this.outputsElement.classList.add("show");
        const errorElement = document.createElement("div");
        errorElement.classList.add("error");
        errorElement.innerText = this.atob(message.stdout);
        this.outputsElement.appendChild(errorElement);
        break;
      }
    }
  }
}
