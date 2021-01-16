class RoomConnection {
  constructor(roomName) {
    this.roomName = roomName;
    this.subscribers = {};
    this.messageQueue = [];
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
    for (const widget of Object.values(this.subscribers)) {
      widget.handleOpen();
    }
  }
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      this.subscribers[message.executor].handleMessage(message.message);
    } catch (error) {
      console.error(error);
      console.error(event.data);
    }
  }
  handleClose(event) {
    console.warn("WEBSOCKET CLOSED!!11elf", event);  // TODO: show in UI
    for (const widget of Object.values(this.subscribers)) {
      widget.handleClose();
    }
  }
  handleError(event) {
    console.error("WEBSOCKET ERROR:", event);  // TODO: show in UI
    for (const widget of Object.values(this.subscribers)) {
      widget.handleClose();
    }
  }
  subscribe(name, widget) {
    this.subscribers[name] = widget;
  }
  sendMessage(message) {
    this.webSocket.send(JSON.stringify(message));
  }
  getSendMessageCallback(name) {
    return message => {
      this.sendMessage({
        executor: name,
        message: message,
      });
    };
  }
}
