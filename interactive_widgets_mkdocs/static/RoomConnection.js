class RoomConnection extends EventTarget {
  constructor(roomName) {
    super();
    this.roomName = roomName;
    this.pendingLoadingWidgets = 0;
    this.enableConnecting = false;
    this.messageQueue = [];
    this.disconnectedElement = null;
    this.webSocket = null;
  }

  connect() {
    this.webSocket = new WebSocket(this.getWebSocketUrl());
    this.webSocket.addEventListener("open", this.handleOpen.bind(this));
    this.webSocket.addEventListener("message", this.handleMessage.bind(this));
    this.webSocket.addEventListener("close", this.handleClose.bind(this));
    this.webSocket.addEventListener("error", this.handleError.bind(this));
  }

  getWebSocketUrl() {
    const webSocketUrl = new URL(window.location);
    if (webSocketUrl.protocol === "https:") {
      webSocketUrl.protocol = "wss:";
    } else {
      webSocketUrl.protocol = "ws:";
    }
    webSocketUrl.hash = "";
    const hasTrailingSlash = webSocketUrl.pathname[webSocketUrl.pathname.length - 1] === "/";
    webSocketUrl.pathname = `${webSocketUrl.pathname}${hasTrailingSlash ? "" : "/"}ws`;
    const webSocketUrlParams = new URLSearchParams();
    webSocketUrlParams.append("roomName", this.roomName);
    webSocketUrl.search = webSocketUrlParams;
    return webSocketUrl.toString();
  }

  handleOpen() {
    this.showConnected();
    this.dispatchEvent(new Event("connect"));
    for (let message = this.messageQueue.pop(); message !== undefined; message = this.messageQueue.pop()) {
      this.webSocket.send(JSON.stringify(message));
    }
  }

  handleMessage(event) {
    const message = JSON.parse(event.data);
    this.dispatchEvent(new CustomEvent(message.executor, { detail: message.message }));
  }

  handleClose(event) {
    this.showDisconnected();
    console.warn("WEBSOCKET CLOSED!!11elf", event);
    this.dispatchEvent(new Event("disconnect"));
  }

  handleError(event) {
    this.showDisconnected();
    console.error("WEBSOCKET ERROR:", event);
    this.dispatchEvent(new Event("disconnect"));
  }

  addWidget() {
    this.pendingLoadingWidgets += 1;
  }

  markWidgetReady() {
    this.pendingLoadingWidgets -= 1;
    if (this.enableConnecting && this.pendingLoadingWidgets === 0) {
      this.connect();
    }
  }

  readyForConnecting() {
    this.enableConnecting = true;
    if (this.pendingLoadingWidgets === 0) {
      this.connect();
    }
  }

  sendMessage(executor, message) {
    const completeMessage = {
      executor: executor,
      message: message,
    };

    if (this.webSocket !== null && this.webSocket.readyState === 1) {
      this.webSocket.send(JSON.stringify(completeMessage));
    } else {
      this.messageQueue.push(completeMessage);
    }
  }

  showDisconnected() {
    if (this.disconnectedElement === null) {
      this.disconnectedElement = document.createElement("div");
      document.body.insertBefore(this.disconnectedElement, document.body.firstChild);
      this.disconnectedElement.classList.add("interactive-widgets-disconnected");

      const disconnectedBoxElement = document.createElement("div");
      this.disconnectedElement.appendChild(disconnectedBoxElement);

      const svgNamespace = "http://www.w3.org/2000/svg";
      const disconnectedSvgElement = document.createElementNS(svgNamespace, "svg");
      disconnectedBoxElement.appendChild(disconnectedSvgElement);
      disconnectedSvgElement.setAttributeNS(null, "viewBox", "0 0 24 24");

      const disconnectedSvgEmptyPathElement = document.createElementNS(svgNamespace, "path");
      disconnectedSvgElement.appendChild(disconnectedSvgEmptyPathElement);
      disconnectedSvgEmptyPathElement.setAttributeNS(null, "d", "M0 0h24v24H0z");
      disconnectedSvgEmptyPathElement.setAttributeNS(null, "fill", "none");

      const disconnectedSvgIconPathElement = document.createElementNS(svgNamespace, "path");
      disconnectedSvgElement.appendChild(disconnectedSvgIconPathElement);
      disconnectedSvgIconPathElement.setAttributeNS(null, "d", "M19.35 10.04C18.67 6.59 15.64 4 12 4c-1.48 0-2.85.43-4.01 1.17l1.46 1.46C10.21 6.23 11.08 6 12 6c3.04 0 5.5 2.46 5.5 5.5v.5H19c1.66 0 3 1.34 3 3 0 1.13-.64 2.11-1.56 2.62l1.45 1.45C23.16 18.16 24 16.68 24 15c0-2.64-2.05-4.78-4.65-4.96zM3 5.27l2.75 2.74C2.56 8.15 0 10.77 0 14c0 3.31 2.69 6 6 6h11.73l2 2L21 20.73 4.27 4 3 5.27zM7.73 10l8 8H6c-2.21 0-4-1.79-4-4s1.79-4 4-4h1.73z");

      const disconnectedSpanElement = document.createElement("span");
      disconnectedBoxElement.appendChild(disconnectedSpanElement);
      disconnectedSpanElement.innerText = "Connection lost. Please reload.";
    }
  }

  showConnected() {
    if (this.disconnectedElement !== null) {
      document.body.removeChild(this.disconnectedElement);
      this.disconnectedElement = null;
    }
  }
}
