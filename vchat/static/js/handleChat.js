/*
Add event listners to the contact cards that open the chat in an iFrame.
*/
let CURRENT_FRIEND = "";
const friends = document.querySelectorAll("div.contact_card");
const msgWindow = document.getElementById("msg-window");
const sendWindow = document.getElementById("send-window");

console.log(`${window.origin}`)
console.log(friends);

for (const friend of friends)
{
    friend.addEventListener("click", function() {
        msgWindow.src = `${window.origin}/conv/${friend.dataset.id}`;
        sendWindow.src = `${window.origin}/send/${friend.dataset.id}`;
        CURRENT_FRIEND = friend.dataset.id;
        console.log("clicked");
    });
}

const chatBtn = document.getElementById("chat");
chatBtn.addEventListener("click", function() {
    if (CURRENT_FRIEND != "") {
        msgWindow.src = `${window.origin}/conv/${CURRENT_FRIEND}`;
        sendWindow.src = `${window.origin}/send/${CURRENT_FRIEND}`;
    }
});

const fileBtn = document.getElementById("file");
fileBtn.addEventListener("click", function() {
    if (CURRENT_FRIEND != "") {
        msgWindow.src = `${window.origin}/files/${CURRENT_FRIEND}`;
        sendWindow.src = `${window.origin}/file_upload/${CURRENT_FRIEND}`;
    }
});


// Slidebar
const slideBtn = document.getElementById("arrow");
slideBtn.addEventListener("click", function() {
    console.log("arrow");
    const contacts = document.querySelector(".contacts");
    if (contacts.classList.contains("hidden")) {
        contacts.classList.remove("hidden");
        slideBtn.innerHTML = "&#60";
    } else {
        contacts.classList.add("hidden");
        slideBtn.innerHTML = "&#62";
    }
});