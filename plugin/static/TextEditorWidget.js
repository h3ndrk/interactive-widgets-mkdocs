class TextEditorWidget {
  constructor(element, sendMessage, file) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.file = file;
    this.stdoutBuffer = "";
    this.setupUi();
  }
  setupUi() {
    this.element.classList = ["interactive-widgets-text-editor"];
    this.contentsElement = document.createElement("div");
    this.contentsElement.classList.add("contents");
    this.setupError(btoa("There is no data"));
    this.element.appendChild(this.contentsElement);
    this.captionElement = document.createElement("div");
    this.captionElement.classList.add("caption");
    this.captionElement.innerText = `Editing text of ${this.file}`;
    this.element.appendChild(this.captionElement);
  }
  setupButtons(hasError) {
    const buttonsElement = document.createElement("div");
    buttonsElement.classList.add("buttons");
    const buttonCreateElement = document.createElement("button");
    buttonCreateElement.innerText = "Create/Empty";
    buttonCreateElement.addEventListener("click", () => {
      // TODO
      // this.sendMessage(null);
    });
    buttonsElement.appendChild(buttonCreateElement);
    if (!hasError) {
      const buttonSaveElement = document.createElement("button");
      buttonSaveElement.innerText = "Save";
      buttonSaveElement.addEventListener("click", () => {
        // TODO
        // this.sendMessage(null);
      });
      buttonsElement.appendChild(buttonSaveElement);
      const buttonDeleteElement = document.createElement("button");
      buttonDeleteElement.innerText = "Delete";
      buttonDeleteElement.addEventListener("click", () => {
        // TODO
        // this.sendMessage(null);
      });
      buttonsElement.appendChild(buttonDeleteElement);
    }
    this.contentsElement.appendChild(buttonsElement);
  }
  setupError(error) {
    while (this.contentsElement.firstChild) {
      this.contentsElement.removeChild(this.contentsElement.firstChild);
    }

    this.contentsElement.classList.remove("with-contents");
    this.contentsElement.classList.add("with-error");

    this.setupButtons(true);

    const errorContainerElement = document.createElement("div");
    errorContainerElement.classList.add("error-container");
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
    errorContainerElement.appendChild(errorElement);
    this.contentsElement.appendChild(errorContainerElement);
  }
  setupContents(contents) {
    while (this.contentsElement.firstChild) {
      this.contentsElement.removeChild(this.contentsElement.firstChild);
    }

    this.contentsElement.classList.remove("with-error");
    this.contentsElement.classList.add("with-contents");

    this.setupButtons(false);

    const editorElement = document.createElement("div");
    editorElement.classList.add("editor");
    this.editor = CodeMirror(editorElement, {
      lineNumbers: true,
      value: atob(contents),
    });
    this.contentsElement.appendChild(editorElement);
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
