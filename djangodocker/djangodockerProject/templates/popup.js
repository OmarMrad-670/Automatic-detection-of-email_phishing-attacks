document.addEventListener("DOMContentLoaded", function () {
    var openGoogleButton = document.getElementById("openGoogle");
    openGoogleButton.addEventListener("click", function () {
      chrome.tabs.create({ url: "http://localhost:8000/" });
    });
  });