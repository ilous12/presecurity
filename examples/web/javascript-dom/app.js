const params = new URLSearchParams(window.location.search);
const displayName = params.get("name") || "guest";

// Intentional fixture: user-controlled HTML is written into the page.
document.getElementById("profile").innerHTML = displayName;
