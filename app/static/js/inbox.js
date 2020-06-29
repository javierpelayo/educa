let url = window.location.href;
let returnInbox = document.querySelector(".return-inbox");
let inbox = document.querySelector(".inbox");
let inboxSnippets = document.querySelector(".inbox-convos");
let conversation = document.querySelector(".convo");

function slideRight() {
    inbox.style.animation = `.2s ease-out slide-right`;
}

function resize(){
    if (url.includes('conversation') && window.innerWidth < 768){
        returnInbox.classList.remove('d-none');
        inboxSnippets.style.display = "none";
        conversation.style.width = "100%";
        inbox.style.margin = ".5rem 1rem 2rem 1rem";
    } else if (window.innerWidth > 768) {
        returnInbox.classList.add('d-none');
        inboxSnippets.style.display = "flex";
        conversation.style.display = "flex";
        inboxSnippets.style.width = "20%";
        conversation.style.width = "80%";
        inbox.style.margin = "1rem 2rem 1rem 4rem";
    } else {
        returnInbox.classList.remove('d-none');
        conversation.style.display = "none";
        inboxSnippets.style.width = "100%";
        inbox.style.margin = ".5rem 1rem 2rem 1rem";
    }
}

// if in browser
window.onresize = () => {
    resize();
}

// on browser load or mobile
if (window.innerWidth < 768) {
    slideRight();
    resize();
}