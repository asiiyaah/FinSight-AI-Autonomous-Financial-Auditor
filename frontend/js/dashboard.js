const accessToken = localStorage.getItem("access_token");

if (!accessToken) {
    window.location.href = "index.html";
}