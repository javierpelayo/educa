let add_o_btn = document.querySelector("#add_o_btn");
let q_type = document.querySelector("#question_form_type");

q_type.onchange = function() {
  if(this.value == "Multiple Choice"){
    add_o_btn.classList.remove("d-none");
  } else {
    add_o_btn.classList.add("d-none");
  }
};
