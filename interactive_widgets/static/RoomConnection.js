class RoomConnection {
  constructor() {
    this.subscribers = {};
    this.ensureLocationHash();
    this.webSocket = new WebSocket(this.getWebSocketUrl());
    this.webSocket.addEventListener("message", this.handleMessage.bind(this));
    this.webSocket.addEventListener("close", this.handleClose.bind(this));
    this.webSocket.addEventListener("error", this.handleError.bind(this));
  }
  uuidv4() {
    // https://gist.github.com/outbreak/316637cde245160c2579898b21837c1c
    const getRandomSymbol = (symbol) => {
      var array;
      if (symbol === 'y') {
        array = ['8', '9', 'a', 'b'];
        return array[Math.floor(Math.random() * array.length)];
      }
      array = new Uint8Array(1);
      window.crypto.getRandomValues(array);
      return (array[0] % 16).toString(16);
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, getRandomSymbol);
  }
  ensureLocationHash() {
    // https://gist.github.com/johnelliott/cf77003f72f889abbc3f32785fa3df8d
    if (!location.hash.match(new RegExp(/^#[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i))) {
      location.hash = `#${this.uuidv4()}`;
    }
  }
  getUuidFromLocationHash() {
    return location.hash.substr(1);
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
    const webSocketUrlParams = new URLSearchParams(webSocketUrl.search);
    webSocketUrlParams.append("roomName", this.getUuidFromLocationHash());
    webSocketUrl.search = webSocketUrlParams;
    return webSocketUrl.toString();
  }
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      this.subscribers[message.executor].handleMessage(message.message);
    } catch (error) {
      console.error(error);
      console.error(message);
    }
  }
  handleClose(event) {
    console.warn("WEBSOCKET CLOSED!!11elf", event);  // TODO: show in UI
  }
  handleError(event) {
    console.error("WEBSOCKET ERROR:", event);  // TODO: show in UI
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
