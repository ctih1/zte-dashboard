// https://stackoverflow.com/questions/1349404/generate-a-string-of-random-characters
function randomString(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function initNotifBox() {
    const node = document.createElement("div");
    window.document.body.appendChild(node);
    node.id = "notif-box"
    node.style = "position: fixed; background: white; filter: drop-shadow(12px -12px 24px #00000066); padding: 12px; padding-top: 0px; padding-bottom: 0px; border-bottom-left-radius: 12px; top: 0px; right: 0px"

    return node;
}

function getNotificationBox() {
    let target = document.getElementById("notif-box");
    if(!target) {
        console.log("Initializing notification box")
        return initNotifBox();
    }

    return target;
}

function showNotification(text, type = "error") {
    const logElement = document.createElement("p");
    const notifId = randomString(8);

    if(type === "loading") {
        logElement.style = "display: flex; align-items: center"
        logElement.innerHTML = `<span>${text}</span> <div style="scale: 0.35" class="spinner"></div>`
    } else {
        logElement.innerText = text;

        if(type === "error") {
            logElement.classList.add("danger");
        }
    }

    logElement.id = `notification-${notifId}`;
    getNotificationBox().appendChild(logElement);

    return notifId;
}

function removeNotification(id) {
    try {
        document.getElementById(`notification-${id}`).remove();

    } catch(err) {
        console.warn("Failed to delete notification")
    }
}

function clearNotificationBox() {
    getNotificationBox().innerHTML = "";
}