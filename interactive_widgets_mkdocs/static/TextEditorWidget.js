class TextEditorWidget extends Widget {
  constructor(element, file, mode) {
    super();
    this.element = element;
    this.file = file;
    this.mode = mode;
    this.stdoutBuffer = "";
    this.open = false;
    this.running = false;
    this.hasContents = false;
  }

  start() {
    this.setupUi();
    this.dispatchEvent(new Event("ready"));
  }

  setupUi() {
    this.boxElement = document.createElement("div");
    this.element.appendChild(this.boxElement);
    this.boxElement.classList.add("interactive-widgets-box", "fixed", "interactive-widgets-text-editor");

    this.buttonsElement = document.createElement("div");
    this.boxElement.appendChild(this.buttonsElement);
    this.buttonsElement.classList.add("buttons", "show");

    this.buttonCreateElement = document.createElement("button");
    this.buttonsElement.appendChild(this.buttonCreateElement);
    this.buttonCreateElement.disabled = !this.open || this.running;
    this.buttonCreateElement.innerText = "Create/Empty";
    this.buttonCreateElement.addEventListener("click", () => {
      if (this.open) {
        this.dispatchEvent(new CustomEvent("message", {
          detail: {
            stdin: this.btoa(JSON.stringify({
              contents: "",
            }) + "\n"),
          },
        }));
        this.running = true;
        this.updateDisabled();
      }
    });

    this.spacerBetweenCreateAndSaveElement = document.createElement("div");
    this.buttonsElement.appendChild(this.spacerBetweenCreateAndSaveElement);
    this.spacerBetweenCreateAndSaveElement.classList.add("spacer");

    this.buttonSaveElement = document.createElement("button");
    this.buttonsElement.appendChild(this.buttonSaveElement);
    this.buttonSaveElement.disabled = !this.open || this.running;
    this.buttonSaveElement.innerText = "Save";
    this.buttonSaveElement.addEventListener("click", () => {
      if (this.open) {
        this.dispatchEvent(new CustomEvent("message", {
          detail: {
            stdin: this.btoa(JSON.stringify({
              contents: this.btoa(this.editor.getValue()),
            }) + "\n"),
          },
        }));
        this.running = true;
        this.updateDisabled();
      }
    });

    this.spacerBetweenSaveAndDeleteElement = document.createElement("div");
    this.buttonsElement.appendChild(this.spacerBetweenSaveAndDeleteElement);
    this.spacerBetweenSaveAndDeleteElement.classList.add("spacer");

    this.buttonDeleteElement = document.createElement("button");
    this.buttonsElement.appendChild(this.buttonDeleteElement);
    this.buttonDeleteElement.disabled = !this.open || this.running;
    this.buttonDeleteElement.innerText = "Delete";
    this.buttonDeleteElement.addEventListener("click", () => {
      if (this.open) {
        this.dispatchEvent(new CustomEvent("message", {
          detail: {
            stdin: this.btoa(JSON.stringify({
              delete: true,
            }) + "\n"),
          },
        }));
        this.running = true;
        this.updateDisabled();
      }
    });

    this.editorElement = document.createElement("div");
    this.boxElement.appendChild(this.editorElement);
    this.editorElement.classList.add("editor");
    this.editor = CodeMirror(this.editorElement, {
      lineNumbers: true,
      lineWrapping: true,
      mode: this.mode,
    });
    this.editor.refresh();

    this.errorElement = document.createElement("div");
    this.boxElement.appendChild(this.errorElement);
    this.errorElement.classList.add("error");

    const svgNamespace = "http://www.w3.org/2000/svg";
    this.svgElement = document.createElementNS(svgNamespace, "svg");
    this.errorElement.appendChild(this.svgElement);
    this.svgElement.setAttributeNS(null, "viewBox", "0 0 24 24");

    this.svgEmptyPathElement = document.createElementNS(svgNamespace, "path");
    this.svgElement.appendChild(this.svgEmptyPathElement);
    this.svgEmptyPathElement.setAttributeNS(null, "d", "M0 0h24v24H0z");
    this.svgEmptyPathElement.setAttributeNS(null, "fill", "none");

    this.svgIconPathElement = document.createElementNS(svgNamespace, "path");
    this.svgElement.appendChild(this.svgIconPathElement);
    this.svgIconPathElement.setAttributeNS(null, "d", "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z");

    this.spanElement = document.createElement("span");
    this.errorElement.appendChild(this.spanElement);

    this.setupError(this.btoa("There is no data"));

    this.captionElement = document.createElement("div");
    this.element.appendChild(this.captionElement);
    this.captionElement.classList.add("interactive-widgets-caption");
    this.captionElement.innerText = `Editing text of ${this.file}`;
  }

  setupError(error) {
    this.running = false;
    this.hasContents = false;
    this.updateDisabled();
    this.editorElement.classList.remove("show");
    this.errorElement.classList.add("show");
    this.spanElement.innerText = this.atob(error);
  }

  setupContents(contents) {
    this.running = false;
    this.hasContents = true;
    this.updateDisabled();
    this.errorElement.classList.remove("show");
    this.editorElement.classList.add("show");
    this.editor.setValue(this.atob(contents));
    this.editor.refresh();
  }

  handleOpen() {
    this.open = true;
    this.updateDisabled();
  }

  handleClose() {
    this.open = false;
    this.updateDisabled();
  }

  updateDisabled() {
    this.buttonCreateElement.disabled = !this.open || this.running;
    this.buttonSaveElement.disabled = !this.open || this.running || !this.hasContents;
    this.buttonDeleteElement.disabled = !this.open || this.running || !this.hasContents;
    this.editor.setOption("readOnly", !this.open || this.running);
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

    this.stdoutBuffer += this.atob(message.stdout);
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
