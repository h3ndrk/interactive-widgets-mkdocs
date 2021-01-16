class TextEditorWidget {
  constructor(element, sendMessage, file) {
    this.element = element;
    this.sendMessage = sendMessage;
    this.file = file;
    this.stdoutBuffer = "";
    this.open = false;
    this.setupUi();
  }
  setupUi() {
    this.element.classList = ["interactive-widgets-text-editor"];
    this.contentsElement = document.createElement("div");
    this.contentsElement.classList.add("contents");

    const buttonsElement = document.createElement("div");
    buttonsElement.classList.add("buttons");
    const buttonCreateElement = document.createElement("button");
    buttonCreateElement.innerText = "Create/Empty";
    buttonCreateElement.addEventListener("click", () => {
      if (this.open) {
        this.sendMessage({
          stdin: btoa(JSON.stringify({
            contents: "",
          }) + "\n"),
        });
      }
    });
    buttonsElement.appendChild(buttonCreateElement);
    const spacerBetweenCreateAndSaveElement = document.createElement("div");
    spacerBetweenCreateAndSaveElement.classList.add("spacer", "hide-on-error");
    buttonsElement.appendChild(spacerBetweenCreateAndSaveElement);
    const buttonSaveElement = document.createElement("button");
    buttonSaveElement.classList.add("hide-on-error");
    buttonSaveElement.innerText = "Save";
    buttonSaveElement.addEventListener("click", () => {
      if (this.open) {
        this.sendMessage({
          stdin: btoa(JSON.stringify({
            contents: btoa(this.editor.getValue()),
          }) + "\n"),
        });
      }
    });
    buttonsElement.appendChild(buttonSaveElement);
    const spacerBetweenSaveAndDeleteElement = document.createElement("div");
    spacerBetweenSaveAndDeleteElement.classList.add("spacer", "hide-on-error");
    buttonsElement.appendChild(spacerBetweenSaveAndDeleteElement);
    const buttonDeleteElement = document.createElement("button");
    buttonDeleteElement.classList.add("hide-on-error");
    buttonDeleteElement.innerText = "Delete";
    buttonDeleteElement.addEventListener("click", () => {
      if (this.open) {
        this.sendMessage({
          stdin: btoa(JSON.stringify({
            delete: true,
          }) + "\n"),
        })
      };
    });
    buttonsElement.appendChild(buttonDeleteElement);
    this.contentsElement.appendChild(buttonsElement);

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
    this.errorDescriptionElement = document.createElement("div");
    this.errorDescriptionElement.classList.add("description");
    errorElement.appendChild(this.errorDescriptionElement);
    errorContainerElement.appendChild(errorElement);
    this.contentsElement.appendChild(errorContainerElement);

    const editorElement = document.createElement("div");
    editorElement.classList.add("editor");
    this.editor = CodeMirror(editorElement, {
      lineNumbers: true,
    });
    this.contentsElement.appendChild(editorElement);
    this.editor.refresh();

    this.setupError(btoa("There is no data"));

    this.element.appendChild(this.contentsElement);

    this.captionElement = document.createElement("div");
    this.captionElement.classList.add("caption");
    this.captionElement.innerText = `Editing text of ${this.file}`;
    this.element.appendChild(this.captionElement);
  }
  setupError(error) {
    this.contentsElement.classList.remove("with-contents");
    this.contentsElement.classList.add("with-error");

    this.errorDescriptionElement.innerText = atob(error);
  }
  setupContents(contents) {
    this.contentsElement.classList.remove("with-error");
    this.contentsElement.classList.add("with-contents");

    this.editor.setValue(atob(contents));
    this.editor.refresh();
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
