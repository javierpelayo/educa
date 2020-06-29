// Create an Ajax object request
let request = new XMLHttpRequest();
let form = document.querySelector("#questions");
let file = document.querySelector("#assignment");
let filename = document.querySelector("#filename");

function fn(){

  // once file is uploaded
    // change the text inside small tag
  if (file) {
    file.addEventListener('change', () => {
      console.log(file.files)
      filename.textContent = file.files[0].name;
    });
  }

  if (form) {
    form.addEventListener("submit", function(event) {
      // get the amount of questions
      let questionCount = document.getElementsByClassName("card");
      let fields = []
      let data = {};

      request.open("POST", window.location.pathname, true);
      request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");

      tinyMCE.triggerSave();

      for (var i = 0; i < questionCount.length; i++) {
        // get the question for the particular index
        let question = document.querySelector("#question_" + String(i));
        if (question.tagName == "DIV") {
          // get the input selected at that particular index
          let input_selected = document.querySelector('input[name="question_' + String(i) + '"]:checked');

          // if it exists then change the id of the input selected to the question index
          if (input_selected != null){
            input_selected.id = "question_" + String(i);
            fields.push(input_selected);
          } else {
            // creates an empty input for the question so it has an empty value
            // if no input was selected for that question
            let element = document.createElement("input");
            element.id = "question_" + String(fields.length);
            element.type = "text";
            element.name = "question_" + String(fields.length);
            fields.push(element);
          }
        } else {
          // if the question isnt multiple choice
          fields.push(question);
        }
      }

      // event handler : checks the state of the request,
      // if it is done do something
      request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
          errors = JSON.parse(request.responseText);

          // if the request has an error
          if (Object.keys(errors).length > 0) {
            fields.forEach(function(item, index, array){
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

      fields.forEach(function(item, index, array){
          data[item.id] = item.value;
      });

      let dataQuery = Object.keys(data).map(key => key + '=' + encodeURIComponent(data[key])).join('&');
      dataQuery += "&ajax=true";

      // pass data as a query string(flask converts it into an immutable multi_dict)
      request.send(dataQuery);

      // prevent request from being sent through HTML Form
      event.preventDefault();
    });
  }
}

function ready(fn) {
  if (document.readyState !== "loading"){
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

ready(fn);
