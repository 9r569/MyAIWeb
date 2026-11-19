
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatBox = document.getElementById("chatBox");
const welcomeScreen = document.getElementById("welcomeScreen");

// Store conversation history
const conversationHistory = JSON.parse(
    localStorage.getItem("wareallyHistory")
) || [];

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

    if (sendBtn.disabled) {
        return;
    }

    sendBtn.disabled = true;

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


    // Show typing indicator
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

        // Send message and previous history to Python
        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                history: conversationHistory.slice(-20)

            })

        });


        const data = await response.json();

        typingIndicator.remove();

        if (!response.ok) {
            throw new Error(data.reply || "AI request failed.");
        }


        // Display AI response
        const aiMessage = document.createElement("div");

        aiMessage.className = "message ai-message";

        aiMessage.innerHTML = DOMPurify.sanitize(
            marked.parse(data.reply || "No response received.")
        );

        chatBox.appendChild(aiMessage);


        // Save successful conversation
        conversationHistory.push(
            {
                role: "user",
                parts: [
                    { text: message }
                ]
            },
            {
                role: "model",
                parts: [
                    { text: data.reply }
                ]
            }
        );


        // Keep only the latest 20 messages
        if (conversationHistory.length > 20) {

            conversationHistory.splice(
                0,
                conversationHistory.length - 20
            );

        }

        scrollToBottom();


    } catch (error) {

        typingIndicator.remove();

        console.error(error);

        const errorMessage = document.createElement("div");

        errorMessage.className = "message ai-message";

        errorMessage.textContent =
            error.message || "Could not connect to AI server.";

        chatBox.appendChild(errorMessage);

        scrollToBottom();

    } finally {

        sendBtn.disabled = false;

        userInput.focus();

    }

}
