function updateScroll(){
    const element = document.querySelector(".messages");
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
}

updateScroll();