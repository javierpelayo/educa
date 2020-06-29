let assignments = document.querySelector("#assignments");
let courses = document.querySelector("#courses");
let assignments_list = document.querySelector("#assignments_list");
let courses_list = document.querySelector("#courses_list");

tinymce.remove("#biography");

assignments.onclick = function() {
  this.classList.add("student-info-selected");
  assignments_list.classList.remove("d-none");
  courses_list.classList.add("d-none");
  courses.classList.remove("student-info-selected");
};

courses.onclick = function() {
  this.classList.add("student-info-selected");
  courses_list.classList.remove("d-none");
  assignments_list.classList.add("d-none");
  assignments.classList.remove("student-info-selected");
};
