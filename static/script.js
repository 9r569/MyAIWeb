
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatBox = document.getElementById("chatBox");

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {

    const message = userInput.value.trim();

    if (message === "") {
        return;
    }

    // Display user message
    const userMessage = document.createElement("div");

    userMessage.className = "message user-message";
    userMessage.textContent = message;

    chatBox.appendChild(userMessage);

    userInput.value = "";
  // Show AI typing indicator
const typingIndicator = document.createElement("div");

typingIndicator.className = "typing-indicator";

typingIndicator.innerHTML = `
    AI is typing
    <span>.</span>
    <span>.</span>
    <span>.</span>
`;

chatBox.appendChild(typingIndicator);

    try {

        // Send message to Python
        const response = await fetch("/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });

        // Receive Python response
        const data = await response.json();
      typingIndicator.remove();

        // Display AI response
        const aiMessage = document.createElement("div");

        aiMessage.className = "message ai-message";
        aiMessage.innerHTML = DOMPurify.sanitize(
    marked.parse(data.reply)
);

        chatBox.appendChild(aiMessage);

    } catch (error) {
      typingIndicator.remove();

        console.error(error);
        alert("Could not connect to AI server.");

    }

}
