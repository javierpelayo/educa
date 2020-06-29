let dropBtnList = document.querySelectorAll(".drop-btn");
let yesBtn = document.querySelector("#yesBtn");
let student_id = ""

dropBtnList.forEach(function(item, index, array) {
  item.addEventListener("click", function() {
    student_id = item.id;
    yesBtn.value = student_id;
  });
});
