let addQuestionBtn = document.querySelector("#add_question");
let removeQuestionBtn = document.querySelector("#remove_question");
let questions = document.querySelector("#questions");

let qClickAmt = 0;
let oClickAmt = 0;

let qTitle;
let qContent;
let qAnswer;
let qType;
let oAddBtn;
let oRemoveBtn;

let question;
let rQuestion;

removeQuestionBtn.onclick = function() {
  if (qClickAmt > 0){
    qClickAmt -= 1;
    rQuestion = document.querySelector("#question_" + String(qClickAmt));
    rQuestion.parentNode.removeChild(rQuestion);
  }
};

addQuestionBtn.onclick = function() {
  /*
    Individual Question Components
  */

  // name = question_title_<q#> -- POST VARIABLE
  qTitle = `<input id='question_title_${qClickAmt}' class='form-control' type='text' name='question_title_${qClickAmt}' placeholder='Title'>`;

  // name = question_content_<q#> -- POST VARIABLE
  qContent = `<textarea id='question_content_${qClickAmt}' class='form-control' name='question_content_${qClickAmt}'  placeholder='Question (Ask your question here)'></textarea>`;

  // name = question_answer_<q#> -- POST VARIABLE
  qAnswer = `<input id='question_answer_${qClickAmt}' class='form-control' type='text' name='question_answer_${qClickAmt}' placeholder='Correct Answer (optional)'>`;

  // name = question_type_<q#> -- POST VARIABLE
  qType = `<select id='qtype_${qClickAmt}' class='form-control' name='question_type_${qClickAmt}'>
              <option value='input'>Input</option>
              <option value='multiple_choice'>Multiple Choice</option>
              <option value='paragraph'>Paragraph</option>
            </select>`;
  oAddBtn = `<button id='add_option_${qClickAmt}' class='btn btn-outline-warning btn-sm my-1 d-none' type='button'>Add Option</button>`;
  oRemoveBtn = `<button id='remove_option_${qClickAmt}' class='btn btn-outline-danger btn-sm my-1 d-none' type='button'>Remove Option</button>`;

  /*
    Question Components Together
  */

  question = `<div id="question_${qClickAmt}" class="d-flex flex-column align-items-center my-2">
                <div class='col-10 d-flex flex-column align-items-center border pb-3'>
                  <h5 id='q_header_${qClickAmt}' class='my-3'>Question ${qClickAmt+1}</h5>
                  <div class='col-12 mb-3'>${qTitle}</div>
                  <div class='col-12 mb-3'>${qContent}</div>
                  <div class='col-12 mb-3'>${qAnswer}</div>
                  <b id='q_answer_header_${qClickAmt}' class='mb-2'>Answer Type</b>
                  <div class='col-12 mb-3'>${qType}</div>
                  <div id='options_${qClickAmt}' class="col-12 d-flex flex-column align-items-center p-0"></div>
                  <div class='col text-center'>${oAddBtn} ${oRemoveBtn}</div>
                </div>
              </div>`;

  questions.insertAdjacentHTML('beforeend', question);

  qType = document.querySelector("#qtype_" + String(qClickAmt));
  oAddBtn = document.querySelector("#add_option_" + String(qClickAmt));
  oRemoveBtn = document.querySelector("#remove_option_" + String(qClickAmt));

  change(qType, oAddBtn, oRemoveBtn, qClickAmt);

  qClickAmt += 1;
};

function change(type, add, remove, index) {
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
    qOption = `<input id='qOption_${index}_${oClickAmt}' class='form-control qOption_${index}' type='text' name='question_option_${index}_${oClickAmt}' placeholder='Option #${oClickAmt+1}'>`;
    options.insertAdjacentHTML('beforeend', "<div class='col-12 mb-3'>" + qOption + "</div>");

    oClickAmt += 1;
  };
}
