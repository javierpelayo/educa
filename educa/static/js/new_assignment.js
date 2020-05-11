let addQuestionBtn = document.querySelector("#add_question");
let removeQuestionBtn = document.querySelector("#remove_question");
let questions = document.querySelector("#questions");

let qClickAmt = 0;
let oClickAmt = 0;

let div = "<div class='col-10 mb-3'>"
let qTitle = "";
let qContent = "";
let qAnswer = "";
let qType = "";

let rqHeader = "";
let rqTitle = "";
let rqContent = "";
let rqAHeader = "";
let rqAnswer = "";
let rqType = "";

let qTypeChoice = [];
let addOptionBtn = [];
let removeOptionBtn = [];

let optionsAtIndex = [];
let lastOptionAtIndex = [];
let removedOption = "";

removeQuestionBtn.onclick = function() {

  if (qClickAmt > 0){
    qClickAmt -= 1;
    document.querySelectorAll(".qOption_" + String(qClickAmt)).forEach(e => e.parentNode.parentNode.removeChild(e.parentNode));

    // Removes both add and remove option buttons
    let aOptionBtn = document.querySelector(`#add_option_${qClickAmt}`);
    aOptionBtn.parentNode.parentNode.removeChild(aOptionBtn.parentNode);

    // removes the question fields
    rqHeader = document.querySelector(`#q_header_${qClickAmt}`);
    rqHeader.parentNode.removeChild(rqHeader);

    rqTitle = document.querySelector(`#question_title_${String(qClickAmt)}`);
    rqTitle.parentNode.parentNode.removeChild(rqTitle.parentNode);

    rqContent = document.querySelector(`#question_content_${String(qClickAmt)}`);
    rqContent.parentNode.parentNode.removeChild(rqContent.parentNode);

    rqAHeader = document.querySelector(`#q_answer_header_${qClickAmt}`);
    rqAHeader.parentNode.removeChild(rqAHeader);

    rqAnswer = document.querySelector(`#question_answer_${String(qClickAmt)}`);
    rqAnswer.parentNode.parentNode.removeChild(rqAnswer.parentNode);

    rqType = document.querySelector(`#qtype_${String(qClickAmt)}`);
    rqType.parentNode.parentNode.removeChild(rqType.parentNode);

    // resets the arrays for the option fields
    qTypeChoice = [];
    addOptionBtn = [];
    removeOptionBtn = [];
  }
};
addQuestionBtn.onclick = function() {
  // name = question_title_<q#> -- POST VARIABLE
  qTitle = `<input id='question_title_${String(qClickAmt)}' class='form-control' type='text' name='question_title_${String(qClickAmt)}' placeholder='Title'>`;

  // name = question_content_<q#> -- POST VARIABLE
  qContent = `<textarea id='question_content_${String(qClickAmt)}' class='form-control' name='question_content_${String(qClickAmt)}'  placeholder='Question (Ask your question here)'></textarea>`;

  // name = question_answer_<q#> -- POST VARIABLE
  qAnswer = `<input id='question_answer_${String(qClickAmt)}' class='form-control' type='text' name='question_answer_${String(qClickAmt)}' placeholder='Correct Answer (optional)'>`;

  // name = question_type_<q#> -- POST VARIABLE
  qType = `<select id='qtype_${String(qClickAmt)}' class='form-control' name='question_type_${String(qClickAmt)}'>
              <option value='input'>Input</option>
              <option value='multiple_choice'>Multiple Choice</option>
              <option value='paragraph'>Paragraph</option>
            </select>`;

  questions.insertAdjacentHTML('beforeend', `<h5 id='q_header_${qClickAmt}' class='mb-2 mt-5'>Question ${String(qClickAmt+1)}</h5>
                                            ${div}
                                              ${qTitle}
                                            </div>`);
  questions.insertAdjacentHTML('beforeend', div + qContent + "</div>");
  questions.insertAdjacentHTML('beforeend', div + qAnswer + "</div>");
  questions.insertAdjacentHTML('beforeend', `<b id='q_answer_header_${qClickAmt}' class='mb-2'>Answer Type</b>
                                                ${div}
                                                  ${qType}
                                                </div>
                                                <div class='col text-center'>
                                                  <button id='add_option_${String(qClickAmt)}' class='btn btn-outline-warning btn-sm my-1 d-none' type='button'>Add Option</button>
                                                  <button id='remove_option_${String(qClickAmt)}' class='btn btn-outline-danger btn-sm my-1 d-none' type='button'>Remove Option</button>
                                                </div>`)

  qTypeChoice.push(document.querySelector("#qtype_" + String(qClickAmt)));
  addOptionBtn.push(document.querySelector("#add_option_" + String(qClickAmt)));
  removeOptionBtn.push(document.querySelector("#remove_option_" + String(qClickAmt)));

  qClickAmt += 1;
};

this.onmousemove = function() {
  qTypeChoice.forEach(function(item, index, array){
    item.onchange = function() {
      // if the Question Type is Multiple Choice
      if(item.value == "multiple_choice"){
        oClickAmt = 0;
        addOptionBtn[index].classList.remove("d-none");
        removeOptionBtn[index].classList.remove("d-none");
      } else {
        // Delete all Option Fields if not Multiple Choice
        document.querySelectorAll(".qOption_" + String(index)).forEach(e => e.parentNode.parentNode.removeChild(e.parentNode));
        addOptionBtn[index].classList.add("d-none");
        removeOptionBtn[index].classList.add("d-none");
      }
    };
    // Update
    removeOptionBtn[index].onclick = function() {
      // Gets all the option fields at the index
      optionsAtIndex = document.querySelectorAll(".qOption_" + String(index))

      if (optionsAtIndex.length > 0){
        // Gets the option field that was last inserted at the index
        lastOptionAtIndex = optionsAtIndex[optionsAtIndex.length - 1].getAttribute("id").split("_")

        // sets the option click amt to the last one at the index to keep option #'s sequential
        oClickAmt = Number(lastOptionAtIndex[2]);
      }
      
      removedOption = document.querySelector(`#qOption_${String(index)}_${String(oClickAmt)}`)
      if(removedOption != null){
        removedOption.parentNode.parentNode.removeChild(removedOption.parentNode);
      }
    };
    addOptionBtn[index].onclick = function() {
      // Gets all the option fields at the index
      optionsAtIndex = document.querySelectorAll(".qOption_" + String(index))

      if (optionsAtIndex.length > 0){
        // Gets the option field that was last inserted at the index
        lastOptionAtIndex = optionsAtIndex[optionsAtIndex.length - 1].getAttribute("id").split("_")

        // sets the option click amt to the last one at the index to keep option #'s sequential
        // + 1 is for the new option that will be inserted
        oClickAmt = Number(lastOptionAtIndex[2]) + 1;
      }

      // name = question_option_<q#>_<o#> -- POST VARIABLE
      qOption = `<input id='qOption_${String(index)}_${String(oClickAmt)}' class='form-control qOption_${String(index)}' type='text' name='question_option_${String(index)}_${String(oClickAmt)}' placeholder='Option #${String(oClickAmt+1)}'>`;
      this.parentNode.insertAdjacentHTML('beforebegin', div + qOption + "</div>");

      oClickAmt += 1;
    };
  });
};
