class ButtonWidget {
  constructor(element, sendMessage, command, label) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.command = command;
    this.label = label;
    this.open = false;
    this.running = false;
    this.setupUi();
  }
  setupUi() {
    this.boxElement = document.createElement("div");
    this.element.appendChild(this.boxElement);
    this.boxElement.classList.add("interactive-widgets-box", "shrink", "interactive-widgets-button");

    this.buttonsElement = document.createElement("div");
    this.boxElement.appendChild(this.buttonsElement);
    this.buttonsElement.classList.add("buttons", "show");

    this.buttonElement = document.createElement("button");
    this.buttonsElement.appendChild(this.buttonElement);
    this.buttonElement.disabled = !this.open || this.running;
    this.buttonElement.innerText = this.label;
    this.buttonElement.addEventListener("click", () => {
      if (this.open) {
        this.sendMessage(null);
      }
    });

    this.commandElement = document.createElement("div");
    this.boxElement.appendChild(this.commandElement);
    this.commandElement.classList.add("command", "show");
    this.commandElement.innerText = this.command;

    this.outputsElement = document.createElement("div");
    this.boxElement.appendChild(this.outputsElement);
    this.outputsElement.classList.add("outputs", "show");
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
        break;
      }
      case "output": {
        if ("stdout" in message) {
          const lineElement = document.createElement("div");
          lineElement.classList.add("line", "stdout");
          lineElement.innerText = atob(message.stdout);
          this.outputsElement.appendChild(lineElement);
        } else if ("stderr" in message) {
          const lineElement = document.createElement("div");
          lineElement.classList.add("line", "stderr");
          lineElement.innerText = atob(message.stderr);
          this.outputsElement.appendChild(lineElement);
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
        const errorElement = document.createElement("div");
        errorElement.classList.add("error");
        errorElement.innerText = atob(message.stdout);
        this.outputsElement.appendChild(errorElement);
        break;
      }
    }
  }
}
