
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatBox = document.getElementById("chatBox");
const welcomeScreen = document.getElementById("welcomeScreen");

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});


// SCROLL TO LATEST MESSAGE
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}


// SEND MESSAGE
async function sendMessage() {

    const message = userInput.value.trim();

    if (message === "") {
        return;
    }

    // Remove welcome screen
    if (welcomeScreen) {
        welcomeScreen.remove();
    }

    // Display user message
    const userMessage = document.createElement("div");

    userMessage.className = "message user-message";
    userMessage.textContent = message;

    chatBox.appendChild(userMessage);

    userInput.value = "";

    scrollToBottom();


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

    scrollToBottom();


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
            marked.parse(data.reply || "No response received.")
        );

        chatBox.appendChild(aiMessage);

        scrollToBottom();


    } catch (error) {

        typingIndicator.remove();

        console.error(error);

        const errorMessage = document.createElement("div");

        errorMessage.className = "message ai-message";

        errorMessage.textContent =
            "Could not connect to AI server. Please try again.";

        chatBox.appendChild(errorMessage);

        scrollToBottom();

    }

}
