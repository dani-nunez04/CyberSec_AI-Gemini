function sendMessage() {
const input = document.getElementById("userInput");
const message = input.value.trim();
if (!message) return;

// Agregar mensaje del usuario
const chatWindow = document.getElementById("chatWindow");
const userMsg = document.createElement("div");
userMsg.classList.add("message", "user-message");
userMsg.innerHTML = `<div>${message}</div>`;
chatWindow.appendChild(userMsg);
chatWindow.scrollTop = chatWindow.scrollHeight;

// Simular respuesta
const botMsg = document.createElement("div");
botMsg.classList.add("message", "bot-message");
botMsg.innerHTML = `<div>Haz clic aquí para ver la respuesta en grande</div>`;
botMsg.onclick = () => openLargeWindow("Esta es la respuesta a tu pregunta: " + message);
chatWindow.appendChild(botMsg);
chatWindow.scrollTop = chatWindow.scrollHeight;

input.value = "";
}

function openLargeWindow(content) {
document.getElementById("largeContent").innerHTML = content;
document.getElementById("largeWindow").style.display = "flex";
}

function closeLargeWindow() {
document.getElementById("largeWindow").style.display = "none";
}