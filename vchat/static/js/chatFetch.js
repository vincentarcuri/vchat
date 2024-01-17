let last = 0;

// Fetch JSON messages object from the database
function fetchMessages() {
    fetch(`${window.origin}/fetch-msg/${FRIEND}/${last}`)
    .then(data => {
        return data.json();
    })
    .then(data => {
        if (!isEmpty(data)) {
            loadMessages(data);
        }
    });
}

// Checks if the data is empty, because we do not want to update the `last`
// variable with NaN or -Infinity
function isEmpty(data) {
    if (data.length == 0) {
        return true;
    } else {
        return false;
    }
}

// Resets the `last` (last msg id) variable to the max id number.
function resetLast(id_array) {
    max = Math.max(...id_array);
    last = max;
}

// Loops over all the messages in the JSON response.
function loadMessages (data) {
    let msg_ids = [];
    for (let obj of data) {
        msg_ids.push(Number(obj['id']));
        msgToDiv(obj);
    }

    resetLast(msg_ids);

}

// Appends a div element containing the message to chat page.
function msgToDiv(obj) {
    const conversation = document.getElementById("convo");
    div = document.createElement("div");
    div.innerText = obj['msg'];
    if (obj['from'] == USER) {
        div.classList.add("user");
    } else {
        div.classList.add("other");
    }
    conversation.appendChild(div);
}

const timeout = setInterval(fetchMessages, 1000);