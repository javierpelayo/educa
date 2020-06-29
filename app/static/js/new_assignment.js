let addQuestionBtn = document.querySelector("#add_question");
let removeQuestionBtn = document.querySelector("#remove_question");
let questions = document.querySelector("#questions");
let aType = document.querySelector("#type");

// Create an Ajax object request
let request = new XMLHttpRequest();
let form = document.querySelector("#assignment");
let errors;
let field;
let smallTag;
let dataQuery;

let qClickAmt = 0;
let oClickAmt = 0;

let selfRemoveBtn;
let qTitle;
let qContent;
let qAnswer;
let qPoints;
let qType;
let oAddBtn;
let oRemoveBtn;

let qOption;

let question;
let rQuestion;
function editor(){
  tinymce.init({
      selector: "textarea",
  });
}
function change(type, add, remove, index) {
  // selfRemove.onclick = function() {
  //   // to be continued
  // }
  type.onchange = function() {
    // if the Question Type is Multiple Choice
    if(type.value == "multiple_choice"){
      oClickAmt = 0;
      add.classList.remove("d-none");
      remove.classList.remove("d-none");
    } else {
      // Delete all Option Fields if not Multiple Choice
      document.querySelectorAll(".qOption_" + String(index)).forEach(e => e.parentNode.parentNode.removeChild(e.parentNode));
      add.classList.add("d-none");
      remove.classList.add("d-none");
    }
  }

  remove.onclick = function() {
    // Gets all the option fields at the index
    let optionsAtIndex = document.querySelectorAll(".qOption_" + String(index))

    if (optionsAtIndex.length > 0){
      // Gets the option field that was last inserted at the index
      let lastOptionAtIndex = optionsAtIndex[optionsAtIndex.length - 1].getAttribute("id").split("_")

      // sets the option click amt to the last one at the index to keep option #'s sequential
      oClickAmt = Number(lastOptionAtIndex[2]);
    }

    let removedOption = document.querySelector(`#qOption_${index}_${oClickAmt}`);
    if(removedOption != null){
      removedOption.parentNode.parentNode.removeChild(removedOption.parentNode);
    }
  };

  add.onclick = function() {
    // Gets all the option fields at the index
    let optionsAtIndex = document.querySelectorAll(".qOption_" + String(index))

    if (optionsAtIndex.length > 0){
      // Gets the option field that was last inserted at the index
      let lastOptionAtIndex = optionsAtIndex[optionsAtIndex.length - 1].getAttribute("id").split("_")

      // sets the option click amt to the last one at the index to keep option #'s sequential
      // + 1 is for the new option that will be inserted
      oClickAmt = Number(lastOptionAtIndex[2]) + 1;
    }

    let options = document.querySelector("#options_" + String(index));

    // name = question_option_<q#>_<o#> -- POST VARIABLE
    qOption = `<input id='qOption_${index}_${oClickAmt}' class='form-control qOption_${index}' type='text' name='question_option_${index}_${oClickAmt}' placeholder='Option #${oClickAmt+1}'>
              <div class="invalid-feedback">
                  <small id="assignment_qOption_${index}_${oClickAmt}_error"></small>
              </div>`;
    options.insertAdjacentHTML('beforeend', "<div class='col-12 mb-3'>" + qOption + "</div>");

    oClickAmt += 1;
  };
}

function fn(){
  form.addEventListener("submit", function(event) {
    // resets the data object incase user removes or adds content to assignment
    let data = {};

    request.open("POST", window.location.pathname, true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");

    tinyMCE.triggerSave();
    let fields = document.forms["assignment"].querySelectorAll('input,textarea,select');

    // event handler : checks the state of the request,
    // if it is done do something
    request.onreadystatechange = function() {
      if (request.readyState == 4 && request.status == 200) {
        console.log("REQUEST SENT")
        errors = JSON.parse(request.responseText);

        // if the request has an error
        if (Object.keys(errors).length > 0) {
          fields.forEach(function(item, index, array){
            if (item.tagName === "INPUT" || item.tagName === "TEXTAREA"){
              item.classList.remove("is-invalid");
              smallTag = document.querySelector(`#assignment_${item.id}_error`);

              // check is needed since some INPUTS don't need validation(CSRF token or question_answer) and may not have small element
              if(smallTag) {
                smallTag.innerText = "";
              }
            }
          });

          for(const key in errors){
            field = document.querySelector(`#${key}`);
            smallTag = document.querySelector(`#assignment_${key}_error`);
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

  // if assignment type is instructions hide buttons
  aType.onchange = function(){
    if (aType.value === "Instructions"){
      questions.innerHTML = "";
      removeQuestionBtn.classList.add('d-none');
      addQuestionBtn.classList.add('d-none');
      qClickAmt = 0;
    } else {
      rQuestions =
      removeQuestionBtn.classList.remove('d-none');
      addQuestionBtn.classList.remove('d-none');
    }
  }

  removeQuestionBtn.onclick = function() {
    if (qClickAmt > 0){
      qClickAmt -= 1;
      rQuestion = document.querySelector("#question_" + String(qClickAmt));
      tinymce.remove();
      rQuestion.parentNode.removeChild(rQuestion);
      editor();
    }
  };

  addQuestionBtn.onclick = function() {
    /*
      Individual Question Components
    */

    // name = question_title_<q#> -- POST VARIABLE
    qTitle = `<input id='question_title_${qClickAmt}' class='form-control' type='text' name='question_title_${qClickAmt}' placeholder='Title'>
              <div class="invalid-feedback">
                  <small id="assignment_question_title_${qClickAmt}_error"></small>
              </div>`;

    // name = question_content_<q#> -- POST VARIABLE
    qContent = `<textarea id='question_content_${qClickAmt}' class='form-control' name='question_content_${qClickAmt}'  placeholder='Question (Ask your question here)'></textarea>
                <div class="invalid-feedback">
                    <small id="assignment_question_content_${qClickAmt}_error"></small>
                </div>`;

    // name = question_answer_<q#> -- POST VARIABLE
    qAnswer = `<input id='question_answer_${qClickAmt}' class='form-control' type='text' name='question_answer_${qClickAmt}' placeholder='Correct Answer (optional)'>`;

    // name = question_points_<q#> -- POST VARIABLE
    qPoints = `<input id='question_points_${qClickAmt}' class='form-control' type='text' name='question_points_${qClickAmt}' placeholder='Points'>
              <div class="invalid-feedback">
                  <small id="assignment_question_points_${qClickAmt}_error"></small>
              </div>`;

    // name = question_type_<q#> -- POST VARIABLE
    qType = `<select id='qtype_${qClickAmt}' class='form-control' name='question_type_${qClickAmt}'>
                <option value='input'>Input</option>
                <option value='multiple_choice'>Multiple Choice</option>
                <option value='paragraph'>Paragraph</option>
              </select>`;
    // selfRemoveBtn = `<button id="remove_question_${qClickAmt}" type="button" class="close pr-2" aria-label="Close">
    //                     <span aria-hidden="true">&times;</span>
    //                   </button>`;
    oAddBtn = `<button id='add_option_${qClickAmt}' class='btn btn-outline-warning btn-sm my-1 d-none' type='button'>Add Option</button>`;
    oRemoveBtn = `<button id='remove_option_${qClickAmt}' class='btn btn-outline-danger btn-sm my-1 d-none' type='button'>Remove Option</button>`;

    /*
      Question Components Together
    */


    // new feature - self remove btn added after q_header_<q#>
    question = `<div id="question_${qClickAmt}" class="d-flex flex-column align-items-center my-2">
                  <div class='col-10 d-flex flex-column align-items-center border pb-3'>
                    <div class='col-12 mb-3 pt-3 px-0'>
                      <div class="d-flex justify-content-center align-items-center">
                        <h5 id='q_header_${qClickAmt}'>Question ${qClickAmt+1}</h5>
                      </div>
                    </div>
                    <div class='col-12 mb-3'>${qTitle}</div>
                    <div class='col-12 mb-3'>${qContent}</div>
                    <div class='col-12 mb-3'>${qAnswer}</div>
                    <div class='col-12 mb-3'>${qPoints}</div>
                    <b id='q_answer_header_${qClickAmt}' class='mb-2'>Answer Type</b>
                    <div class='col-12 mb-3'>${qType}</div>
                    <div id='options_${qClickAmt}' class="col-12 d-flex flex-column align-items-center p-0"></div>
                    <div class='col text-center'>${oAddBtn} ${oRemoveBtn}</div>
                  </div>
                </div>`;

    questions.insertAdjacentHTML('beforeend', question);

    editor();

    // selfRemoveBtn = document.querySelector('#remove_question_' + String(qClickAmt));
    qType = document.querySelector("#qtype_" + String(qClickAmt));
    oAddBtn = document.querySelector("#add_option_" + String(qClickAmt));
    oRemoveBtn = document.querySelector("#remove_option_" + String(qClickAmt));

    change(qType, oAddBtn, oRemoveBtn, qClickAmt);

    qClickAmt += 1;
  };
}

function ready(fn) {
  if (document.readyState !== "loading"){
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

ready(fn);
