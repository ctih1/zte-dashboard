const dismissNotifButton = document.createElement("button");
dismissNotifButton.innerHTML = "Clear all"
dismissNotifButton.style.width = "100%";
dismissNotifButton.onclick = _ => clearNotificationBox();
let onCooldown = false;


// from https://stackoverflow.com/a/59777755 but minified
// because the standard sha256 API isn't available in non-https contexts that arent localhost.
// man this takes me back to the good ol days of frii.saite where I was doing this exact same thing lol. 
// Also note: I might implement better authentication in the future. This is just to add a *bit* of extra security until I do so
var sha256=function r($){function _(r,$){return r>>>$|r<<32-$}for(var o,f,n=Math.pow,t=n(2,32),a="length",c="",e=[],i=8*$[a],h=r.h=r.h||[],u=r.k=r.k||[],v=u[a],l={},s=2;v<64;s++)if(!l[s]){for(o=0;o<313;o+=s)l[o]=s;h[v]=n(s,.5)*t|0,u[v++]=n(s,1/3)*t|0}for($+="\x80";$[a]%64-56;)$+="\0";for(o=0;o<$[a];o++){if((f=$.charCodeAt(o))>>8)return;e[o>>2]|=f<<(3-o)%4*8}for(f=0,e[e[a]]=i/t|0,e[e[a]]=i;f<e[a];){var g=e.slice(f,f+=16),k=h;for(o=0,h=h.slice(0,8);o<64;o++){var x=g[o-15],d=g[o-2],p=h[0],w=h[4],A=h[7]+(_(w,6)^_(w,11)^_(w,25))+(w&h[5]^~w&h[6])+u[o]+(g[o]=o<16?g[o]:g[o-16]+(_(x,7)^_(x,18)^x>>>3)+g[o-7]+(_(d,17)^_(d,19)^d>>>10)|0),C=(_(p,2)^_(p,13)^_(p,22))+(p&h[1]^p&h[2]^h[1]&h[2]);(h=[A+C|0].concat(h))[4]=h[4]+A|0}for(o=0;o<8;o++)h[o]=h[o]+k[o]|0}for(o=0;o<8;o++)for(f=3;f+1;f--){var S=h[o]>>8*f&255;c+=(S<16?0:"")+S.toString(16)}return c};

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
            <li><a href="/ntools">Network tools</a></li>
        </ul>
    `
    document.body.prepend(navbar);

    const data = await (await req).json();
    const lockButton = document.createElement("button");
    if(data["cooldown"]) {
        lockButton.innerText = "Disable cooldown";
        lockButton.classList.add("destructive");
    } else {
        lockButton.innerText = "Enable cooldown";
        lockButton.classList.add("primary");
    }
    if(!data.authenticated && window.location.pathname !== "/login") {
        window.location.href = "/login";
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