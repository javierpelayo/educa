let messages = document.querySelectorAll(".msg");

function updateScroll(){
    let msgBox = document.querySelector(".messages");
    console.log(msgBox);
    msgBox.scrollTop = msgBox.scrollHeight;
}

function slideRight() {
    messages = Array.from(messages).reverse();
    let msgs = messages.slice(0, 4);
    let ticker = 0;
    msgs.forEach((item) => {
        ticker += .1;
        item.style.animation = `${ticker}s ease-out slide-right`;
    });
}

slideRight();
updateScroll();