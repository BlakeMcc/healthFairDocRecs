function copyClipboard() {
  var urlEl = document.getElementById("urlVal");
  range = document.createRange();
  range.selectNode(urlEl);
  window.getSelection().addRange(range);
  document.execCommand("copy");
}
