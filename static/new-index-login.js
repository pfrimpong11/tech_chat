const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-message');
const firstMessageUserInput = document.getElementById('modal-user-input');
const firstMessageSendButton = document.getElementById('send-first-message');
const newChatButton = document.getElementById('new-chat');
const clearChatButton = document.getElementById('clear-chat');
const themeToggle = document.getElementById('theme-toggle');
const faqItems = document.querySelectorAll('.faq-item');
const logoImg = document.getElementById('logo-img');
const sidebarTabs = document.querySelectorAll('.sidebar-tab');
const sidebarContents = document.querySelectorAll('.sidebar-content');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
var loader = document.createElement("div");
loader.className = "loader";



// function to add message to the chat window
function addMessage(content, isUser = false) {
    // Remove any existing error messages before adding a regular message
    removeErrorMessage();

    const messageDiv = document.createElement('div');
    
    messageDiv.classList.add('message');
    if (isUser) messageDiv.classList.add('user-message');
    
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// function to remove existing error messages
function removeErrorMessage() {
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
}

// function to add error message
function addErrorMessage(content) {
    // Remove any existing error messages before adding a new one
    removeErrorMessage();

    const messageDiv = document.createElement('div');
    
    messageDiv.classList.add('message', 'error-message'); // Add a class for error messages
    messageDiv.innerHTML = `
        <div class="message-content" style="color: red;">${content}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// function to send message for response
function sendMessage(message) {
    if (isConnected()) {
        console.log("Connected to the internet. Processing input");

        if (message) {
            setTimeout(async function() {
                try {
                    // Make request to backend with user input
                    const response = await fetch("/get_response", {
                        method: "POST",
                        body: JSON.stringify({ message: message }),
                        headers: {
                            "Content-Type": "application/json",
                        },
                    });

                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }

                    const data = await response.json();

                    // Remove loader element when response is received
                    loader.remove();

                    if (data.response == "I'm sorry, I don't understand that.") {
                        saveUserInputToFile(message); // Save user input to file if the bot doesn't understand
                        addMessage("I don't have an answer for that. Kindly rephrase your question for a better response. Was this helpful?");
                        continueChat("I don't have an answer for that. Kindly rephrase your question for a better response. Was this helpful?", 'TechChat');
                    } 
                    else if (data.response == "Please check your internet connection.") {
                        addErrorMessage("An unexpected error has occurred. Please try again later. If the issue persists, kindly reach out to our support team for assistance.");
                    } else {
                        // display response from bot
                        addMessage(data.response);
                        continueChat(data.response, 'TechChat');
                    }

                } catch (error) {
                    console.error("Error:", error);
                    loader.remove();
                    // Add error message to chat
                    addErrorMessage("An unexpected error has occurred. Please try again later. If the issue persists, kindly reach out to our support team for assistance.");
                }
            }, 1000);
        }
    } else {
        addErrorMessage("You are not connected to the internet. Please check your connection.");
    }
}

// Send button and enter key to continue chat
sendButton.addEventListener('click', () => {
    if (userInput.value.trim() !== '') {
        const message = userInput.value.trim();
        addMessage(message, true);
        continueChat(message, 'user'); // Save user message in the database
        userInput.value = "";
        sendMessage(message);   //send message to backend for response

        chatMessages.appendChild(loader);   //add a loader
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && userInput.value.trim() !== '') {
        const message = userInput.value.trim();
        addMessage(message, true);
        continueChat(message, 'user'); // Save user message in the database
        userInput.value = "";
        sendMessage(message);   //send message to backend for response
        
        chatMessages.appendChild(loader);   //add a loader
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

newChatButton.addEventListener('click', () => {
    console.log("new chat button clicked");
    chatMessages.innerHTML = '';
    showModal();
    firstMessageUserInput.focus();
});

clearChatButton.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the chat?')) {
        chatMessages.innerHTML = '';
    }
});

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const icon = themeToggle.querySelector('i');
    icon.classList.toggle('fa-moon');
    icon.classList.toggle('fa-sun');
    
    if (document.body.classList.contains('dark-mode')) {
        logoImg.src = '/static/techchat_logo_dark.png';
    } else {
        logoImg.src = '/static/techchat_logo_light.png';
    }
});

faqItems.forEach(item => {
    item.addEventListener('click', () => {
        userInput.value = item.textContent;
        firstMessageUserInput.value = item.textContent;
        userInput.focus();
        firstMessageUserInput.focus();
    });
});

sidebarTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.getAttribute('data-tab');
        sidebarTabs.forEach(t => t.classList.remove('active'));
        sidebarContents.forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        
        document.getElementById(`${tabName}-content`).classList.add('active');
    });
});


sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// Close sidebar when clicking outside of it
document.addEventListener('click', (e) => {
    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target) && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
    }
});

// // Initial greeting
// addMessage("Hello! How can I assist you with KNUST admissions today?");

// Make sidebar toggle button draggable
let isDragging = false;
let currentX;
let currentY;
let initialX;
let initialY;
let xOffset = 0;
let yOffset = 0;

sidebarToggle.addEventListener("touchstart", dragStart, false);
sidebarToggle.addEventListener("touchend", dragEnd, false);
sidebarToggle.addEventListener("touchmove", drag, false);

sidebarToggle.addEventListener("mousedown", dragStart, false);
sidebarToggle.addEventListener("mouseup", dragEnd, false);
sidebarToggle.addEventListener("mousemove", drag, false);

function dragStart(e) {
    if (e.type === "touchstart") {
        initialX = e.touches[0].clientX - xOffset;
        initialY = e.touches[0].clientY - yOffset;
    } else {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
    }

    if (e.target === sidebarToggle) {
        isDragging = true;
    }
}

function dragEnd(e) {
    initialX = currentX;
    initialY = currentY;

    isDragging = false;
}

function drag(e) {
    if (isDragging) {
        e.preventDefault();
        if (e.type === "touchmove") {
            currentX = e.touches[0].clientX - initialX;
            currentY = e.touches[0].clientY - initialY;
        } else {
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
        }

        xOffset = currentX;
        yOffset = currentY;

        setTranslate(currentX, currentY, sidebarToggle);
    }
}

function setTranslate(xPos, yPos, el) {
    el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
}























// feedback handling
document.addEventListener("DOMContentLoaded", function() {
    var sendFeedbackBtn = document.getElementById("send-feedback-btn");
    sendFeedbackBtn.addEventListener("click", function(event) {
        event.preventDefault(); 

        var firstName = document.getElementById("first-name").value;
        var lastName = document.getElementById("last-name").value;
        var email = document.getElementById("email").value;
        var feedbackText = document.getElementById("feedback-text").value;

        const errorMessage = document.getElementById('feedback-error-message');
        errorMessage.textContent = ''; // Clear any previous error message
    

        if (firstName.trim() === "" || lastName.trim() === "" || email.trim() === "" || feedbackText.trim() === "") {
            errorMessage.innerText = 'Please fill in all fields'; 
            return;
        }

        if (!validateEmail(email)) {
            errorMessage.innerText = 'Please enter a valid email'; 
            return;
        }

            sendUserFeedback(firstName, lastName, email, feedbackText, null, null);

        document.getElementById("first-name").value = "";
        document.getElementById("last-name").value = "";
        document.getElementById("email").value = "";
        document.getElementById("feedback-text").value = "";
        fileInput.value = "";
    });
});

function validateEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}


// Function to send feedback from the feedback button to the server
function sendUserFeedback(firstName, lastName, email, feedback, base64File, fileName) {
    var feedbackData = {
        firstName: firstName,
        lastName: lastName,
        email: email,
        feedback: feedback,
        file: base64File,
        fileName: fileName
    };

    fetch("/record_feedback_with_user_details", {
        method: "POST",
        body: JSON.stringify(feedbackData),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (response.ok) {
            console.log("Feedback recorded successfully.");
            alert('Thank you for your feedback!');
        } else {
            console.error("Failed to record feedback.");
            alert("Failed to record feedback. Please try again later.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error occurred. Please try again later.");
    });
}


















const sessionsContainer = document.getElementById("sessions-container");
const searchInput = document.getElementById("search-input");
const modalOverlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const modalContent = document.getElementById("modal-content");
const modalActions = document.getElementById("modal-actions");
let chatSessions = [];

async function fetchChatSessions() {
    try {
        const response = await fetch(
        `/get-chat-sessions?user_id=${localStorage.getItem("user_id")}`
        );
        const data = await response.json();
        if (data.error) {
        showAlertModal("Error", data.error);
        } else {
        chatSessions = data.chat_sessions;
        renderChatSessions();
        }
    } catch (error) {
        console.error("Error:", error);
        showModal();
        firstMessageUserInput.focus();
        // showAlertModal( "Error", "An error occurred while fetching chat sessions. Please try again.");
    }
}

function renderChatSessions() {
const filteredSessions = chatSessions.filter((session) =>
    session.session_name
    .toLowerCase()
    .includes(searchInput.value.toLowerCase())
);

sessionsContainer.innerHTML = "";

if (filteredSessions.length === 0) {
    sessionsContainer.innerHTML =
    '<p class="no-sessions">No chat history found.</p>';
} else {
    filteredSessions.forEach((session) => {
    const sessionCard = document.createElement("div");
    sessionCard.className = "card";
    sessionCard.innerHTML = `
                <div class="card-header">
                    <h3 class="card-title">${session.session_name}</h3>
                    <p class="card-description">
                        <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        ${new Date(Date.parse(session.created_at)).toLocaleDateString()}
                        <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        ${new Date(Date.parse(session.created_at)).toLocaleTimeString()}
                    </p>
                </div>
                <div class="card-footer">
                    <button class="button button-primary" onclick="openChatSession('${
                        session.session_id
                    }')">Open Session</button>
                    <button class="button button-destructive" onclick="confirmDeleteSession('${
                        session.session_id
                    }')">Delete</button>
                </div>
            `;
    sessionsContainer.appendChild(sessionCard);
    });
}
}

function openChatSession(sessionId) {
    localStorage.setItem('currentSessionId', sessionId);
    location.reload();
}

function confirmDeleteSession(sessionId) {
    showAlertModal(
        "Confirm Deletion",
        "Are you sure you want to delete this chat session? This action cannot be undone.",
        [
        { text: "Cancel", onClick: hideAlertModal, class: "button" },
        {
            text: "Delete",
            onClick: () => deleteSession(sessionId),
            class: "button button-destructive",
        },
        ]
    );
}

async function deleteSession(sessionId) {
    try {
        const response = await fetch(
        `/delete-chat-session/${sessionId}?user_id=${localStorage.getItem(
            "user_id"
        )}`,
        {
            method: "DELETE",
        }
        );
        const data = await response.json();
        if (data.error) {
        showAlertModal("Error", data.error);
        } else {
        chatSessions = chatSessions.filter(
            (session) => session.session_id !== sessionId
        );
        renderChatSessions();
        location.reload();
        }
    } catch (error) {
        console.error("Error:", error);
        showAlertModal( "Error", "An error occurred while deleting the chat session. Please try again." );
    }
}

function showAlertModal(title, content, actions = []) {
    modalTitle.textContent = title;
    modalContent.textContent = content;
    modalActions.innerHTML = "";
    actions.forEach((action) => {
        const button = document.createElement("button");
        button.textContent = action.text;
        button.className = action.class || "button";
        button.onclick = action.onClick;
        modalActions.appendChild(button);
    });
    if (actions.length === 0) {
        const closeButton = document.createElement("button");
        closeButton.textContent = "Close";
        closeButton.className = "button button-primary";
        closeButton.onclick = hideAlertModal;
        modalActions.appendChild(closeButton);
    }
    modalOverlay.style.display = "flex";
}

function hideAlertModal() {
modalOverlay.style.display = "none";
}

searchInput.addEventListener("input", renderChatSessions);















// Fetch messages for the selected session
function fetchSessionMessages(sessionId) {
    fetch(`/get-session-messages/${sessionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: localStorage.getItem('user_id'),
        })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log(data.error);
                showModal();
                firstMessageUserInput.focus();
            } else {
                displayMessages(data.messages);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Display chat history messages in the chat container
function displayMessages(messages) {
    chatMessages.innerHTML = '';  // Clear previous messages

    messages.forEach(message => {
        if (message.sender == 'user'){
            addMessage(message.message, true);
        }
        else if (message.sender == 'TechChat' ) {
            addMessage(message.message);
        }
    });
}

// On page load, fetch the messages for the given session
window.onload = function() {
    fetchChatSessions();

    const sessionId = localStorage.getItem('currentSessionId');
    console.log("session id", localStorage.getItem('currentSessionId'));
    if (sessionId) {
        fetchSessionMessages(sessionId);
        userInput.focus();
    } else {
        showModal();
        firstMessageUserInput.focus();
    }
};








// function to save user input if there is no response
function saveUserInputToFile(input) {
    fetch("/save_user_input", {
        method: "POST",
        body: JSON.stringify({ userInput: input }),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (response.ok) {
            console.log("User input saved to file:", input);
        } else {
            console.error("Failed to save user input to file.");
        }
    })
    .catch(error => console.error("Error:", error));
}


// Function to check internet connectivity
function isConnected() {
    // check if the browser thinks it's online
    if (!navigator.onLine) {
    return false;
    }

    // ping an actual server to verify connectivity
    return new Promise((resolve) => {
    fetch("https://www.google.com", { method: "HEAD" })
        .then(() => resolve(true))
        .catch(() => resolve(false));
    });
}


function showModal() {
    console.log("show modal enable");
    addMessage("Hello! How can I assist you with KNUST admissions today?");
    
    // Hide chat elements
    userInput.style.display = 'none'
    sendButton.style.display = 'none'
    
    // Display the modal
    firstMessageUserInput.style.display = 'block';
    firstMessageSendButton.style.display = 'block';
}



function hideModal() {
    // Restore chat elements
    userInput.style.display = 'block'
    sendButton.style.display = 'block'
    
    // Hide the modal
    firstMessageUserInput.style.display = 'none';
    firstMessageSendButton.style.display = 'none';
}

// send buttons for first message
firstMessageSendButton.addEventListener('click', () => {
    if (firstMessageUserInput.value.trim() !== '') {
        console.log("first message sent by click");
        chatMessages.innerHTML = '';
        handleFirstUserMessage();
        chatMessages.appendChild(loader);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
firstMessageUserInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && firstMessageUserInput.value.trim() !== '') {
        console.log("first message sent by enter");
        chatMessages.innerHTML = '';
        handleFirstUserMessage();
        chatMessages.appendChild(loader);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});



function handleFirstUserMessage() {
    console.log("Handle first user enabled");
    
    var firstUserInput = firstMessageUserInput.value.trim();
    console.log(firstUserInput);
    if (firstUserInput === "") return;
    
    chatMessages.innerHTML = '';
    addMessage(firstUserInput, true);  //add message to chat interface 
    startNewChat(firstUserInput); // Save first message in the database

    // Clear all input fields
    firstMessageUserInput.value = "";
    userInput.value = "";
    userInput.focus();

    // Hide the modal and restore the chat interface
    hideModal();
}





// Function to start a new chat session
function startNewChat(firstMessage = '') {
    console.log("new chat started");

    fetch('/start-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: firstMessage })
    })
    .then(response => response.json())
    .then(data => {
        // Store session ID in localStorage
        localStorage.setItem('currentSessionId', data.session_id);
        if (firstMessage) {
            sendMessage(firstMessage); // send the first first message to the backend for a response
        }
    })
    .catch((error) => {
        console.error('Error starting chat session:', error);
    });
}



function continueChat(message, sender) {
    const storedSessionId = localStorage.getItem('currentSessionId');
    // Send message to backend
    fetch(`/add-message/${storedSessionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, sender })
    })
    .then(response => response.json())
    .catch((error) => {
        console.error('Error sending message:', error);
    });
}
