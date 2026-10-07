const dismissNotifButton = document.createElement("button");
dismissNotifButton.innerHTML = "Clear all"
dismissNotifButton.style.width = "100%";
dismissNotifButton.onclick = _ => clearNotificationBox();
let onCooldown = false;

async function toggleCooldown(lockEnabled) {
    const id = showNotification("Locking API...", "loading");
    const res = await fetch("/api/cooldown", {
        method: lockEnabled ? "DELETE" : "POST"
    });
    removeNotification(id);
    const targetText = lockEnabled ? "unlock" : "lock"; 
    if(res.ok) {
        showNotification(`Successfully ${targetText}ed API!`);
    } else {
        showNotification(`Failed to ${targetText} API.`, "error");
    }
}

window.onload = async ()  => {
    let req = fetch("/api/cooldown");

    const navbar = document.createElement("nav");
    navbar.style = "display: flex; justify-content: space-between; align-items: center;";
    navbar.innerHTML = `
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/sms">SMS</a></li>
            <li><a href="/devices">Devices</a></li>
            <li><a href="/portforwarding">Port forwarding / mapping</a></li>
        </ul>
    `
    document.body.prepend(navbar);

    const data = await (await req).json();
    console.log(data);
    const lockButton = document.createElement("button");
    if(data["cooldown"]) {
        lockButton.innerText = "Disable cooldown";
        lockButton.classList.add("destructive");
    } else {
        lockButton.innerText = "Enable cooldown";
        lockButton.classList.add("primary");
    }

    lockButton.onclick = async () => {
        toggleCooldown(data["cooldown"]);
    }
    navbar.appendChild(lockButton);
};

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
    node.style = "position: fixed; background: white; filter: drop-shadow(12px -12px 24px #00000066); padding: 12px; padding-top: 0px; padding-bottom: 0px; border-bottom-left-radius: 12px; top: 0px; right: 0px; z-index: 69"
    node.appendChild(dismissNotifButton);
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

function handleButtonVisibility() {
    const elements = document.getElementsByClassName("notification-element");

    if(elements.length !== 0) {
        dismissNotifButton.style.display="block";
    } else {
        dismissNotifButton.style.display="none";
    }
}

function showNotification(text, type = "info") {
    const logElement = document.createElement("p");
    logElement.classList.add('notification-element')
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
    getNotificationBox().prepend(logElement);

    handleButtonVisibility();

    return notifId;
}

function removeNotification(id) {
    try {
        document.getElementById(`notification-${id}`).remove();

    } catch(err) {
        console.warn("Failed to delete notification")
    }

    handleButtonVisibility();
}

function clearNotificationBox() {
    const elements = document.getElementsByClassName("notification-element");
    for(let element of elements) {
        element.remove();
    }

    handleButtonVisibility();
}