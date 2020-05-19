// Create an Ajax object request
let request = new XMLHttpRequest();
let form = document.querySelector("#questions");

function fn(){
  form.addEventListener("submit", function(event) {
    // resets the data object incase user removes or adds content to assignment
    let data = {};

    request.open("POST", window.location.pathname, true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");

    tinyMCE.triggerSave();
    let fields = document.forms["questions"].querySelectorAll('input,textarea,select');
    let question_answers = []
    fields.forEach(function(item, index, array){
      if(item.id == "question_" + String(index)){
        question_answers.push(item);
      }
    });

    // Checks for any multiple choice type questions
    let options = document.querySelectorAll(".option_question");

    // loop through those divs to check for any inputs selected
    options.forEach(function(item, index, array){
      if(item.id === "question_" + String(question_answers.length)){
        let input_selected = document.querySelector('input[name="question_' + String(question_answers.length) + '"]:checked');

        if (input_selected == null){
          // creates an empty input for the question so it has an empty value
          // if no input is selected
          let element = document.createElement("input");
          element.id = "question_" + String(question_answers.length);
          element.type = "text";
          element.name = "question_" + String(question_answers.length);
          question_answers.push(element);
        } else {
          // appends the input selected inside the question div
          input_selected.id = "question_" + String(question_answers.length)
          question_answers.push(input_selected);
        }
      }
    });

    // event handler : checks the state of the request,
    // if it is done do something
    request.onreadystatechange = function() {
      if (request.readyState == 4 && request.status == 200) {
        console.log("REQUEST SENT")
        errors = JSON.parse(request.responseText);

        // if the request has an error
        if (Object.keys(errors).length > 0) {
          question_answers.forEach(function(item, index, array){
            if (item.tagName === "INPUT" || item.tagName === "TEXTAREA"){
              item.classList.remove("is-invalid");
              smallTag = document.querySelector(`#${item.id}_error`);

              // check is needed since some INPUTS don't need validation
              if(smallTag) {
                smallTag.innerText = "";
              }
            }
          });

          for(const key in errors){
            field = document.querySelector(`#${key}`);
            smallTag = document.querySelector(`#${key}_error`);
            field.classList.add("is-invalid");
            smallTag.innerText = errors[key];
          }
        } else {
          // if no errors exist then submit the form
          form.submit();
        }
      } else {
        console.log("HTTP request not 200.");
      }
    }

    question_answers.forEach(function(item, index, array){
        data[item.id] = item.value;
    });

    let dataQuery = Object.keys(data).map(key => key + '=' + encodeURIComponent(data[key])).join('&');
    dataQuery += '&ajax=true';
    // pass data as a query string(flask converts it into an immutable multi_dict)
    request.send(dataQuery);

    // prevent request from being sent through HTML Form
    event.preventDefault();
  });
}

function ready(fn) {
  if (document.readyState !== "loading"){
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

ready(fn);
