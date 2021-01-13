class ButtonWidget {
  constructor(element, sendMessage, command, label) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.command = command;
    this.label = label;
    this.setupUi();
  }
  setupUi() {
    this.element.classList = ["interactive-widgets-button"];
    const buttonElement = document.createElement("button");
    buttonElement.classList.add("button");
    buttonElement.innerText = this.label;
    buttonElement.addEventListener("click", () => {
      this.sendMessage(null);
    });
    this.element.appendChild(buttonElement);
    const commandElement = document.createElement("div");
    commandElement.classList.add("command");
    commandElement.innerText = this.command;
    this.element.appendChild(commandElement);
    this.statusElement = document.createElement("div");
    this.statusElement.classList.add("status");
    this.statusElement.innerText = "";
    this.element.appendChild(this.statusElement);
    this.outputsElement = document.createElement("div");
    this.outputsElement.classList.add("outputs");
    this.element.appendChild(this.outputsElement);
    const noOutputElement = document.createElement("div");
    noOutputElement.classList.add("message");
    noOutputElement.innerText = "There is no output yet";
    this.outputsElement.appendChild(noOutputElement);
  }
  handleMessage(message) {
    switch (message.type) {
      case "started": {
        while (this.outputsElement.firstChild) {
          this.outputsElement.removeChild(this.outputsElement.firstChild);
        }
        this.statusElement.innerText = "Running";
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
        this.statusElement.innerText = "Finished";
        break;
      }
      case "errored": {
        this.statusElement.innerText = "Failed";
        const errorElement = document.createElement("div");
        errorElement.classList.add("error");
        errorElement.innerText = atob(message.stdout);
        this.outputsElement.appendChild(errorElement);
        break;
      }
    }
  }
}
