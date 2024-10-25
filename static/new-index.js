const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-message');
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
                    } 
                    else if (data.response == "Please check your internet connection.") {
                        addErrorMessage("An unexpected error has occurred. Please try again later. If the issue persists, kindly reach out to our support team for assistance.");
                    } else {
                        // display response from bot
                        addMessage(data.response);
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
        userInput.value = "";
        sendMessage(message);   //send message to backend for response
        chatMessages.appendChild(loader);   //add a loader
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
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
        userInput.focus();
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

// Initial greeting
window.onload = function () {
    addMessage("Hello! How can I assist you with KNUST admissions today?");
    userInput.focus();
};

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
