let messages = document.querySelectorAll(".msg");
let msgBox = document.querySelector(".messages");
var loader = document.querySelector("#loading");

function updateScroll() {
    msgBox.scrollTop = msgBox.scrollHeight;
}

function insertNewMsg(msgs, msgTime, top) {
    let msgPoint = document.querySelector(`input[value='${msgTime}']`).parentNode;
    msgs.forEach((msg) => {
        let profileImg = `<img class="profile-img-small" src="${window.location.href.split("dashboard")[0]}static/profile_images/${msg.profile_img}">`;
        
        if (msg.profession == "Student") {
            var name = `<h6 class="m-0 ml-3">${msg.name} #${msg.user_id}</h6>`;
        } else {
            var name = `<h6 class="teacher-msg-name m-0 ml-3">${msg.name} - Teacher</h6>`;
        }

        let content = `<p class="m-2 pl-3">${msg.message}</p>`
        let time = `<small class="m-2 pl-3">${msg.created_ctime}</small>`;
        let hidden = `<input type="hidden" name="timestamp_${msg.id}" value="${msg.timestamp}">`;

        if (msg.type == "left") {
            var fullMsg = `<div class="msg">
                                <div class="d-flex justify-content-center align-items-center m-2">
                                    <p class="left-msg">${msg.message}</p>
                                </div>
                            </div>`
        } else {
            var fullMsg = `<div class="msg">
                                <div class="d-flex align-items-center m-2">
                                    ${profileImg}
                                    ${name}
                                </div>
                                ${content}
                                ${time}
                                ${hidden}
                            </div`;
        }
        
        // reverse is dependant on the vantage point of the message
        if (top) {
            // no reverse needed
            msgPoint.insertAdjacentHTML('beforebegin', fullMsg);
        } else {
            // reversed list here
            msgPoint.insertAdjacentHTML('afterend', fullMsg);
        }
    });
    
    if (top) {
        setTimeout(() => {
            loader.classList.add("d-none");
        }, 2000);
    }
}

function ajax(msgTime, top) {
    url = window.location.href;
    fetch(`${url}/update?timestamp=${msgTime}&top=${top}`, {
        method: "GET",
    }).then(response => {
        return response.json()
    }).then(data => insertNewMsg(data, msgTime, top)).catch(error => console.log(error));
}

function slideRight() {
    messages = Array.from(messages).reverse();
    let msgs = messages.slice(0, 5);
    let ticker = 0;
    msgs.forEach((item) => {
        ticker += .1;
        item.style.animation = `${ticker}s ease-out slide-right`;
    });
}

msgBox.onscroll = () => {
    if (msgBox.scrollTop == 0 && messages.length > 2) {
        let msgs = document.querySelectorAll(".msg");
        loader.classList.remove("d-none");
        let timeoutID = setTimeout(() => {
            ajax(msgs[0].getElementsByTagName("input")[0].value, true);
        }, 3000);
    }
}

let intervalID = setInterval(() => {
    let msgs = document.querySelectorAll(".msg");
    ajax(msgs[msgs.length - 1].getElementsByTagName("input")[0].value, false);
}, 6000);

slideRight();
updateScroll();