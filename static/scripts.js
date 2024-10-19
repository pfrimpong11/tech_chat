document.addEventListener("DOMContentLoaded", function() {
    var inputField = document.getElementById("user-input");

    inputField.focus();

    inputField.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            sendMessage();
            console.log("message sent by enter");
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var menuIcon = document.getElementById('menu-icon');
    var sidebar = document.getElementById('sidebar');
    var mainContent = document.querySelector('.main-content');
    var darkModeToggle = document.querySelector(".fa-circle-half-stroke");
    var chatbotLogo = document.querySelector(".chatbot_logo");
    var trashIcon = document.querySelector('.fa-trash-alt');
    var shareIcon = document.querySelector('.fa-share-alt');

    // Get the modal trash modal and buttons
    var modal = document.getElementById("trashModal");
    var span = document.getElementsByClassName("close")[0];
    var confirmBtn = document.getElementById("confirmClearChat");
    var cancelBtn = document.getElementById("cancelClearChat");


    shareIcon.addEventListener('click', function () {
        var chatContent = document.getElementById('chat-container').textContent.trim();

        // Check if Web Share API is supported by the browser
        if (navigator.share) {
            navigator.share({
                title: 'Chat Content',
                text: chatContent
                // url: window.location.href // Optionally share the current page URL
            })
            .then(() => console.log('Shared successfully'))
            .catch((error) => console.error('Error sharing:', error));
        } else {
            alert('Sharing is not supported in your browser.');
            console.log('Sharing is not supported in this browser.');
        }
    });



    // When the user clicks the trash icon, open the modal 
    trashIcon.onclick = function() {
        modal.style.display = "flex";
    }
    span.onclick = function() {
        modal.style.display = "none";
    }
    cancelBtn.onclick = function() {
        modal.style.display = "none";
    }
    confirmBtn.onclick = function() {
        clearChat();
        modal.style.display = "none";
    }

    // Function to clear the chat
    function clearChat() {
        var chatContainer = document.getElementById('chat-container');
        chatContainer.innerHTML = '';
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

     // Dark mode toggle
    darkModeToggle.addEventListener("click", function() {
        document.body.classList.toggle("dark-mode");
        document.body.classList.toggle("light-mode");

        updateBotAvatars();

        if (document.body.classList.contains("dark-mode")) {
            chatbotLogo.src = "/static/techchat_logo_dark.png"; // Update with dark mode bot logo path
        } else {
            chatbotLogo.src = "/static/techchat_logo_light.png"; // Update with light mode bot logo path
        }
    });


    menuIcon.addEventListener('click', function () {
        sidebar.classList.toggle('open');
    });


    mainContent.addEventListener('click', function (event) {
        if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });


    sidebar.addEventListener('click', function (event) {
        event.stopPropagation();
    });


    var faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(function(item) {
        item.addEventListener('click', function() {
            var userInput = item.textContent.trim();
            if (userInput !== "") {
                var userInputField = document.getElementById("user-input");
                userInputField.value = userInput;
                userInputField.focus();
                // Close the side panel on smaller screens
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                }
            }
        });
    });
});



document.addEventListener("DOMContentLoaded", function() {
    var sendFeedbackBtn = document.getElementById("send-feedback-btn");
    sendFeedbackBtn.addEventListener("click", function(event) {
        event.preventDefault(); 

        console.log("Clicked feedback button");
        var firstName = document.getElementById("first-name").value;
        var lastName = document.getElementById("last-name").value;
        var email = document.getElementById("email").value;
        var feedbackText = document.getElementById("feedback-text").value;
        var fileInput = document.getElementById("file");
        var file = fileInput.files[0];

        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = ''; // Clear any previous error message
    

        if (firstName.trim() === "" || lastName.trim() === "" || email.trim() === "" || feedbackText.trim() === "") {
            errorMessage.innerText = 'Please fill in all fields'; 
            return;
        }

        if (!validateEmail(email)) {
            errorMessage.innerText = 'Please enter a valid email'; 
            return;
        }

        if (file) {
            var reader = new FileReader();
            reader.onloadend = function() {
                var base64File = reader.result.split(',')[1];
                sendUserFeedback(firstName, lastName, email, feedbackText, base64File, file.name);
            }
            reader.readAsDataURL(file);
        } else {
            sendUserFeedback(firstName, lastName, email, feedbackText, null, null);
        }

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
            window.location.href = "/pages/emailSent.html";
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


function sendMessage() {
    //check if user is connected to the internet
    if (isConnected()) {
        console.log("Connected to the internet. Processing input");
        console.log("message sent by button");
        var userInput = document.getElementById("user-input").value;
        if (userInput.trim() === "") return;

        addUserMessage(userInput);
        document.getElementById("user-input").value = "";

        // Create and append loader element to chat container
        var loader = document.createElement("div");
        loader.className = "loader";
        document.getElementById("chat-container").appendChild(loader);


        // Delay for 1s before displaying the response
        setTimeout(async function() {
            try {
                // Make request to backend with user input
                const response = await fetch("/get_response", {
                    method: "POST",
                    body: JSON.stringify({ message: userInput }),
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                // Check if response is okay (status code 200-299)
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }

                const data = await response.json();

                // Remove loader element when response is received
                loader.remove();

                if (data.response == "I'm sorry, I don't understand that.") {
                    // Save user input to file if the bot doesn't understand
                    saveUserInputToFile(userInput);
                    // Prompt for feedback
                    addBotMessage("I don't have an answer for that. Kindly rephrase your question for a better response. Was this helpful?");
                } 
                else if (data.response == "Please check your internet connection."){
                    addMessageForError("An unexpected error has occurred. Please try again later. If the issue persists, kindly reach out to our support team for assistance.");
                }
                else {
                    // display response from bot
                    addBotMessage(data.response);
                }

            } catch (error) {
                // Handle any errors, including network issues
                console.error("Error:", error);

                // Remove loader element in case of error
                loader.remove();

                // Add error message to chat
                addMessageForError("An unexpected error has occurred. Please try again later. If the issue persists, kindly reach out to our support team for assistance.");
            }
        }, 1000);

    } else {
        // alert("You are not connected to the internet. Please check your connection.");
        addMessageForError("You are not connected to the internet. Please check your connection.");
    }
}



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


function addUserMessage(message) {
    var chatContainer = document.getElementById("chat-container");
    var userMessage = document.createElement("div");
    userMessage.className = "message user-message";
    userMessage.innerHTML = `
        <i class="fa-solid fa-user"></i>
        <div>${message}</div>
    `;
    chatContainer.appendChild(userMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addBotMessage(message) {
    var chatContainer = document.getElementById("chat-container");

    // Remove the error message if present before adding a new bot message
    var existingError = document.getElementById("error-message");
    if (existingError) {
        chatContainer.removeChild(existingError);
    }

    var botMessage = document.createElement("div");
    botMessage.className = "message bot-message";
    
    var botAvatar = document.createElement("img");
    updateBotAvatar(botAvatar);
    botAvatar.alt = "Bot Avatar";
    botAvatar.className = "bot-avatar";
    botMessage.appendChild(botAvatar);

    // Create a new div for the bot's message
    var messageDiv = document.createElement("div");
    messageDiv.className = "message-content";
    // Set innerHTML to the message directly
    messageDiv.innerHTML = message;
    botMessage.appendChild(messageDiv);

    // Append the message div to the chat container
    chatContainer.appendChild(botMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Add feedback buttons for every bot response
    var feedbackButtons = document.createElement("div");
    feedbackButtons.className = "feedback-buttons";

    var helpfulButton = document.createElement("span");
    helpfulButton.innerHTML = '<i class="fa-regular fa-thumbs-up"></i>';
    helpfulButton.setAttribute("title", "Good response");
    helpfulButton.onclick = function() {
        // Handle helpful feedback
        console.log("User found the response helpful");
        sendFeedback(true); // Send feedback to the server
        helpfulButton.remove(); // Remove feedback buttons after feedback is given
        notHelpfulButton.remove();
    };
    var notHelpfulButton = document.createElement("span");
    notHelpfulButton.innerHTML = '<i class="fa-regular fa-thumbs-down"></i>';
    notHelpfulButton.setAttribute("title", "Bad response");
    notHelpfulButton.onclick = function() {
        // Handle not helpful feedback
        console.log("User found the response not helpful");
        sendFeedback(false); // Send feedback to the server
        notHelpfulButton.remove(); // Remove feedback buttons after feedback is given
        helpfulButton.remove();
    };
    var copyButton = document.createElement('span');
    copyButton.innerHTML = '<i class="fa-regular fa-copy"></i>';
    copyButton.setAttribute('title', 'Copy response');
    copyButton.onclick = function () {
        copyTextToClipboard(message);
    };
    var speakButton = document.createElement('span');
    speakButton.innerHTML = '<i class="fa-regular fa-solid fa-volume-low"></i>';
    speakButton.setAttribute('title', 'Speak response');
    speakButton.onclick = function () {
        toggleSpeech(message);
    };
    feedbackButtons.appendChild(helpfulButton);
    feedbackButtons.appendChild(notHelpfulButton);
    feedbackButtons.appendChild(copyButton);
    feedbackButtons.appendChild(speakButton);
    chatContainer.appendChild(feedbackButtons);

    // animation effect for bot message
    animateMessage(messageDiv);
}


// bot message to display no internet connection or other errors
function addMessageForError(message) {
    var chatContainer = document.getElementById("chat-container");

    // Check if there's already an error message, remove it if found
    var existingError = document.getElementById("error-message");
    if (existingError) {
        chatContainer.removeChild(existingError);
    }

    var botMessage = document.createElement("div");
    botMessage.className = "message bot-message";
    botMessage.id = "error-message"; // Give the error message a specific id for easy identification

    var botAvatar = document.createElement("img");
    updateBotAvatar(botAvatar);
    botAvatar.alt = "Bot Avatar";
    botAvatar.className = "bot-avatar";
    botMessage.appendChild(botAvatar);

    // Create a new div for the error message
    var messageDiv = document.createElement("div");
    messageDiv.className = "message-content";
    messageDiv.style.color = "red"; // Set the color of the error message to red
    messageDiv.innerHTML = message;
    botMessage.appendChild(messageDiv);

    // Append the error message to the chat container
    chatContainer.appendChild(botMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


function updateBotAvatar(botAvatar) {
    if (document.body.classList.contains("dark-mode")) {
        botAvatar.src = "/static/bot_avatar_dark.png";
    } else {
        botAvatar.src = "/static/bot_avatar_light.png";
    }
}

function updateBotAvatars() {
    var botAvatars = document.querySelectorAll(".bot-avatar");
    botAvatars.forEach(function(avatar) {
        updateBotAvatar(avatar);
    });
}


// Get the modal copy modal
var modal = document.getElementById("copyModal");
var span = document.getElementsByClassName("close")[0];
var closeModalButton = document.getElementById("closeModalButton");


// Function to copy text to clipboard
function copyTextToClipboard(text) {
    var tempElement = removeHTMLTags(text);
    console.log(tempElement);
    navigator.clipboard.writeText(tempElement).then(function() {
        // Show the modal
        modal.style.display = "flex";
    });
}
span.onclick = function() {
    modal.style.display = "none";
}
closeModalButton.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function removeHTMLTags(htmlString) {
    // Create a new DOMParser instance
    const parser = new DOMParser();
    // Parse the HTML string into a DOM document
    const doc = parser.parseFromString(htmlString, 'text/html');
    // Extract the text content from the parsed document
    const textContent = doc.body.textContent || "";
    return textContent.trim(); // Trim any leading or trailing whitespace
}





var isSpeaking = false;
var currentUtterance = null;
// Function to toggle speech on and off
function toggleSpeech(text) {
    if (isSpeaking) {
        stopSpeaking();
    } else {
        startSpeaking(removeHTMLTags(text));
    }
}
// Function to start speaking text using SpeechSynthesis API
function startSpeaking(text) {
    var utterance = new SpeechSynthesisUtterance(removeHTMLTags(text));

    var voices = window.speechSynthesis.getVoices();
    utterance.voice = voices[2];
    utterance.rate = 0.7;
    // speechSynthesis.speak(utterance);
    

    window.speechSynthesis.speak(utterance);

    // speechSynthesis.getVoices().forEach(function(voice) {
    //     console.log(voice.name, voice.default ? voice.default :'');
    // });

    isSpeaking = true;
    currentUtterance = utterance;
}
// Function to stop speaking
function stopSpeaking() {
    if (currentUtterance !== null) {
        window.speechSynthesis.cancel(currentUtterance);
    }

    isSpeaking = false;
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


function sendFeedback(isHelpful) {
    // Get the last user message
    var userMessages = document.querySelectorAll(".user-message");
    var userMessage = userMessages[userMessages.length - 1].querySelector("div").textContent;

    // Get the last bot response
    var botMessages = document.querySelectorAll(".bot-message");
    var botResponse = botMessages[botMessages.length - 1].querySelector(".message-content").textContent;

    // Prepare feedback data
    var feedbackData = {
        userMessage: userMessage,
        botResponse: botResponse,
        isHelpful: isHelpful
    };

    // Send feedback data to the server
    fetch("/record_icon_feedback", {
        method: "POST",
        body: JSON.stringify(feedbackData),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (response.ok) {
            console.log("Feedback recorded successfully.");
        } else {
            console.error("Failed to record feedback.");
        }
    })
    .catch(error => console.error("Error:", error));
}


function animateMessage(element) {
    element.style.opacity = 0;

    // Animate the opacity to make it appear gradually
    var opacity = 0;
    var animationInterval = setInterval(function() {
        opacity += 0.05; // animation speed
        element.style.opacity = opacity;
        if (opacity >= 1) {
            clearInterval(animationInterval);
        }
    }, 50);
}


function writeAnimateMessage(element, message) {
    // Clear the element's content
    element.innerHTML = '';

    // Define the typing speed (characters per millisecond)
    var typingSpeed = 15;

    // Initialize index to keep track of the current position in the message
    var index = 0;

    // Define the typing function
    function typeText() {
        // Check if the entire message has been typed
        if (index < message.length) {
            // Append the next character to the element's content
            element.innerHTML += message.charAt(index);
            
            // Increment the index to move to the next character
            index++;

            // Call the typing function recursively after a delay
            setTimeout(typeText, typingSpeed);
        }
    }

    // Start typing the message
    typeText();
}






document.addEventListener('DOMContentLoaded', function () {
    var microphoneButton = document.querySelector('.microphone-button');
    var microphoneIcon = document.getElementById('microphone-icon');
    var userInputField = document.getElementById('user-input');
    var recognition;

    microphoneButton.addEventListener('click', function () {
        // Check if SpeechRecognition API is supported by the browser
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            if (!recognition) {
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                
                recognition.onresult = function(event) {
                    var transcript = event.results[0][0].transcript;
                    userInputField.value += transcript;
                };

                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                };

                recognition.onend = function() {
                    console.log('Speech recognition ended');
                    microphoneIcon.className = 'fa-solid fa-microphone-alt-slash microphone-icon'; // Change back to the static microphone icon
                };
            }

            if (recognition.started) {
                recognition.stop();
                microphoneIcon.className = 'fa-solid fa-microphone-alt-slash microphone-icon'; // Change back to the static microphone icon
                recognition.started = false;
            } else {
                recognition.start();
                microphoneIcon.className = 'fa-solid fa-microphone microphone-icon'; // Change to a different icon or use the GIF method
                recognition.started = true;
            }
        } else {
            alert('Speech recognition is not supported in your browser.');
        }
    });

    // userInputField.addEventListener('keypress', function(event) {
    //     if (event.key === 'Enter') {
    //         sendMessage();
    //     }
    // });
});
