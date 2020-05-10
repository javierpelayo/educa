let addQuestionBtn = document.querySelector("#add_question");
let questions = document.querySelector("#questions");
let qClickAmt = 0;
let oClickAmt = 0;
let div = "<div class='col-10 mb-3'>"
let qTitle = "";
let qContent = "";
let qAnswer = "";
let qType = "";

let qTypeChoice = [];
let addOptionBtn = [];
let optionsAtIndex = [];
let lastOptionAtIndex = [];

addQuestionBtn.onclick = function() {
  // name = question_title_<q#> -- POST VARIABLE
  qTitle = "<input class='form-control' type='text' name='question_title_" + String(qClickAmt) + "'  placeholder='Question Title'></div>";
  // name = question_content_<q#> -- POST VARIABLE
  qContent = "<textarea class='form-control' name='question_content_" + String(qClickAmt) + "'  placeholder='Question Content'></textarea></div>";
  // name = question_answer_<q#> -- POST VARIABLE
  qAnswer = "<input class='form-control' type='text' name='question_answer_" + String(qClickAmt) + "'  placeholder='Question Answer'></div>";
  // name = question_type_<q#> -- POST VARIABLE
  qType = "<select id='qtype_" + String(qClickAmt) + "' class='form-control' name='question_type_" + String(qClickAmt) + "'>";
  qType += "<option value='input'>Input</option>";
  qType += "<option value='multiple_choice'>Multiple Choice</option>";
  qType += "<option value='paragraph'>Paragraph</option></select>";

  questions.insertAdjacentHTML('beforeend', "<h5 class='mb-2'>Question " + String(qClickAmt+1) + "</h5>" + div + qTitle);
  questions.insertAdjacentHTML('beforeend', div + qContent);
  questions.insertAdjacentHTML('beforeend', div + qAnswer);
  questions.insertAdjacentHTML('beforeend', "<b class='mb-2'>Answer Type</b>" + div + qType + "</div><button id='add_option_" + String(qClickAmt) + "' class='btn btn-outline-warning mt-1 mb-2 d-none' type='button'>Add Option</button>");

  qTypeChoice.push(document.querySelector("#qtype_" + String(qClickAmt)));
  addOptionBtn.push(document.querySelector("#add_option_" + String(qClickAmt)));

  qClickAmt += 1;
};

this.onmousemove = function() {
  qTypeChoice.forEach(function(item, index, array){
    item.onchange = function() {
      // if the Question Type is Multiple Choice
      if(item.value == "multiple_choice"){
        oClickAmt = 0;
        addOptionBtn[index].classList.remove("d-none");
      } else {
        // Delete all Option Fields if not Multiple Choice
        document.querySelectorAll(".qOption_" + String(index)).forEach(e => e.parentNode.parentNode.removeChild(e.parentNode));
        addOptionBtn[index].classList.add("d-none");
      }
    };
    addOptionBtn[index].onclick = function() {
      // Gets all the option fields at the index
      optionsAtIndex = document.querySelectorAll(".qOption_" + String(index))

      if (optionsAtIndex.length > 0){
        // Gets the option field that was last inserted at the index
        lastOptionAtIndex = optionsAtIndex[optionsAtIndex.length - 1].getAttribute("id").split("_")

        // sets the option click amt to the last one at the index to keep option #'s sequential
        oClickAmt = Number(lastOptionAtIndex[2]) + 1;
      }

      // name = question_option_<q#>_<o#> -- POST VARIABLE
      qOption = "<input id='qOption_" + String(index) + "_" + String(oClickAmt) + "' class='form-control qOption_" + String(index) + "' type='text' name='question_option_" + String(index) + "_" + String(oClickAmt) + "'  placeholder='Option #" + String(oClickAmt+1) + "'></div>";
      this.insertAdjacentHTML('beforebegin', div + qOption);

      oClickAmt += 1;
    };
  });
};
