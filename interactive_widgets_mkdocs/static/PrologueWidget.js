class PrologueWidget extends EventTarget {
  constructor(element, command, hidden) {
    super();
    this.element = element;
    this.command = command;
    this.hidden = hidden;
  }

  start() {
    this.setupUi();
    this.dispatchEvent(new Event("ready"));
  }

  setupUi() {
    if (!this.hidden) {
      this.boxElement = document.createElement("div");
      this.element.appendChild(this.boxElement);
      this.boxElement.classList.add("interactive-widgets-box", "shrink", "interactive-widgets-logue", "empty");

      this.commandElement = document.createElement("div");
      this.boxElement.appendChild(this.commandElement);
      this.commandElement.classList.add("command", "show");
      this.commandElement.innerText = this.command;

      this.outputsElement = document.createElement("div");
      this.boxElement.appendChild(this.outputsElement);
      this.outputsElement.classList.add("outputs");

      this.captionElement = document.createElement("div");
      this.element.appendChild(this.captionElement);
      this.captionElement.classList.add("interactive-widgets-caption");
      this.captionElement.innerText = "Prologue";
    }
  }

  handleMessage(message) {
    if (!this.hidden) {
      switch (message.type) {
        case "started": {
          while (this.outputsElement.firstChild) {
            this.outputsElement.removeChild(this.outputsElement.firstChild);
          }
          this.boxElement.classList.add("empty");
          this.outputsElement.classList.remove("show");
          break;
        }
        case "output": {
          if ("stdout" in message) {
            this.boxElement.classList.remove("empty");
            this.outputsElement.classList.add("show");
            const lineElement = document.createElement("div");
            lineElement.classList.add("line", "stdout");
            lineElement.innerText = atob(message.stdout);
            this.outputsElement.appendChild(lineElement);
          } else if ("stderr" in message) {
            this.boxElement.classList.remove("empty");
            this.outputsElement.classList.add("show");
            const lineElement = document.createElement("div");
            lineElement.classList.add("line", "stderr");
            lineElement.innerText = atob(message.stderr);
            this.outputsElement.appendChild(lineElement);
          }
          break;
        }
        case "finished": {
          break;
        }
        case "errored": {
          this.boxElement.classList.remove("empty");
          this.outputsElement.classList.add("show");
          const errorElement = document.createElement("div");
          errorElement.classList.add("error");
          errorElement.innerText = atob(message.stdout);
          this.outputsElement.appendChild(errorElement);
          break;
        }
      }
    }
  }
}
