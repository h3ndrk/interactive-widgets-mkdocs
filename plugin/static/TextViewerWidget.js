class TextViewerWidget {
  constructor(element, sendMessage, file) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.file = file;
    this.stdoutBuffer = "";
    this.open = false;
    this.setupUi();
  }
  setupUi() {
    this.element.classList = ["interactive-widgets-text-viewer"];
    this.contentsElement = document.createElement("div");
    this.contentsElement.classList.add("contents", "with-error");
    this.setupError(btoa("There is no data"));
    this.element.appendChild(this.contentsElement);
    this.captionElement = document.createElement("div");
    this.captionElement.classList.add("caption");
    this.captionElement.innerText = `Viewing text of ${this.file}`;
    this.element.appendChild(this.captionElement);
  }
  setupError(error) {
    while (this.contentsElement.firstChild) {
      this.contentsElement.removeChild(this.contentsElement.firstChild);
    }

    this.contentsElement.classList.remove("with-contents");
    this.contentsElement.classList.add("with-error");

    const errorElement = document.createElement("div");
    errorElement.classList.add("error");
    const emojiElement = document.createElement("img");
    emojiElement.src = "see-no-evil-monkey.png";
    emojiElement.alt = "Oops";
    errorElement.appendChild(emojiElement);
    const titleElement = document.createElement("div");
    titleElement.classList.add("title");
    titleElement.innerText = `Cannot view ${this.file}`;
    errorElement.appendChild(titleElement);
    const descriptionElement = document.createElement("div");
    descriptionElement.classList.add("description");
    descriptionElement.innerText = atob(error);
    errorElement.appendChild(descriptionElement);
    this.contentsElement.appendChild(errorElement);
  }
  setupContents(contents) {
    while (this.contentsElement.firstChild) {
      this.contentsElement.removeChild(this.contentsElement.firstChild);
    }

    this.contentsElement.classList.remove("with-error");
    this.contentsElement.classList.add("with-contents");

    for (const [lineNumber, line] of atob(contents).split("\n").entries()) {
      const lineNumberElement = document.createElement("div");
      lineNumberElement.classList.add("line-number");
      lineNumberElement.innerText = `${lineNumber + 1}`;
      this.contentsElement.appendChild(lineNumberElement);
      const lineElement = document.createElement("div");
      lineElement.classList.add("line");
      lineElement.innerText = line;
      this.contentsElement.appendChild(lineElement);
    }
  }
  handleOpen() {
    this.open = true;
    this.element.classList.add("open");
  }
  handleClose() {
    this.open = false;
    this.element.classList.remove("open");
  }
  handleMessage(message) {
    if (message.type != "output") {
      console.warn("Message type not implemented:", message);
      return;
    }

    if (!("stdout" in message)) {
      console.warn("Message has no \"stdout\":", message);
      return;
    }

    this.stdoutBuffer += atob(message.stdout);
    for (let newlinePosition = this.stdoutBuffer.indexOf("\n"); newlinePosition != -1; newlinePosition = this.stdoutBuffer.indexOf("\n")) {
      const stdoutMessage = JSON.parse(this.stdoutBuffer.slice(0, newlinePosition));
      if ("contents" in stdoutMessage) {
        this.setupContents(stdoutMessage.contents);
      } else if ("error" in stdoutMessage) {
        this.setupError(stdoutMessage.error);
      }

      this.stdoutBuffer = this.stdoutBuffer.slice(newlinePosition + 1);
    }
  }
}
