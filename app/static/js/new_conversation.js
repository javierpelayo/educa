let search = document.querySelector(".search");
let searchResults = document.querySelector(".search-results");
let courseID = document.querySelector("#course-id");
let recipientsDiv = document.querySelector("#recipients");
let form = document.querySelector("#new_convo");
let recipientCloseBTN = `<button class="x-mini-close">
                            <svg xmlns="http://www.w3.org/2000/svg" class="" width="1em" height="1em" viewBox="0 1 24 24" stroke-width="2.5" stroke="#ffffff" fill="none" stroke-linecap="round" stroke-linejoin="round">
                                <path stroke="none" d="M0 0h24v24H0z"/>
                                <line fill="#ffffff" x1="18" y1="6" x2="6" y2="18" />
                                <line fill="#ffffff" x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                        </button>`;

function checkDefaultRecipient(){
    let bubbleRecipient = document.querySelector(".default-recipient-bubble");
    if (bubbleRecipient) {
        let id = bubbleRecipient.id.split("-")[2];
        bubbleRecipient.getElementsByTagName('button')[0].onclick = () => {
            removeRecipient(id);
        }
    }
}

function searchDefaultBorderRadius() {
    search.style.borderBottomLeftRadius = "1.25rem";
    search.style.borderBottomRightRadius =  "1.25rem";
    searchResults.classList.add("d-none");
}

function addRecipient(recipient){
    let id = Object.values(recipient)[0]
    let checkRecipient = document.querySelector(`#recipient-bubble-${id}`);

    if (!checkRecipient) {
        recipientsDiv.insertAdjacentHTML('afterbegin', `<span id="recipient-bubble-${id}" class="recipient-bubble">${Object.keys(recipient)[0]}${recipientCloseBTN}</span>`);
        form.insertAdjacentHTML('afterbegin', `<input id="recipients-${id}" type="hidden" name="recipients-${id}" value="${id}">`);
    
        let addedRecipient = document.querySelector(`#recipient-bubble-${id}`);
        addedRecipient.getElementsByTagName('button')[0].onclick = () => {
            removeRecipient(id);
        }
    }
}

function removeRecipient(id){
    let recipientBubble = document.querySelector(`#recipient-bubble-${id}`);
    let recipientHidden = document.querySelector(`#recipients-${id}`);
    recipientHidden.parentNode.removeChild(recipientHidden);
    recipientBubble.parentNode.removeChild(recipientBubble);
}

function searchResultItems(data){
    let keys = Object.keys(data);
    searchResults.innerHTML = "";
    keys.forEach((name) => {
        searchResults.insertAdjacentHTML("beforeend", `<div id="${data[name]}" class="search-item"><p class="m-0">${name}</p></div>`);
        let searchItem = document.getElementById(`${data[name]}`);
        searchItem.onclick = (e) => {
            addRecipient({[name]: data[name]});
        }
    });
}

function ajax(name, course){
    let dataQuery = `name=${name}&course_id=${course}`;
    let url = window.location.href.split("?")[0];
    fetch(`${url}/search?${dataQuery}`, {
        method: "GET",
    }).then(response => {
        return response.json();
    }).then(data => searchResultItems(data)).catch(error => console.log(error))
}

search.oninput = (e) => {
    if(search.value.length > 0) {
        search.style.borderBottomLeftRadius = "0px";
        search.style.borderBottomRightRadius =  "0px";
        searchResults.classList.remove("d-none");
    } else {
        searchDefaultBorderRadius();
    }
}

search.onkeyup = () => {
    if (search.value) {
        ajax(search.value, courseID.value);
    } else {
        searchResults.innerHTML = "";
    }
}

this.onclick = (e) => {
    if (e.target.id != search.id && e.target != searchResults) {
        searchDefaultBorderRadius();
    }
}

checkDefaultRecipient();