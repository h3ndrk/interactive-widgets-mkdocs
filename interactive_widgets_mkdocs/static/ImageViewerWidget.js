class ImageViewerWidget extends EventTarget {
  constructor(element, file, mime) {
    super();
    this.element = element;
    this.file = file;
    this.mime = mime;
    this.stdoutBuffer = "";
  }

  start() {
    this.setupUi();
    this.dispatchEvent(new Event("ready"));
  }

  setupUi() {
    this.boxElement = document.createElement("div");
    this.element.appendChild(this.boxElement);
    this.boxElement.classList.add("interactive-widgets-box", "fixed", "interactive-widgets-image-viewer");

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

    this.setupError(btoa("There is no data"));

    this.captionElement = document.createElement("div");
    this.element.appendChild(this.captionElement);
    this.captionElement.classList.add("interactive-widgets-caption");
    this.captionElement.innerText = `Viewing image from ${this.file}`;
  }

  setupError(error) {
    this.boxElement.style.backgroundImage = "none";
    this.errorElement.classList.add("show");
    this.spanElement.innerText = atob(error);
  }

  setupContents(contents) {
    this.errorElement.classList.remove("show");
    this.boxElement.style.backgroundImage = `url(data:${this.mime};base64,${contents})`;
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
