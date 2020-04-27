btn_drop = document.getElementById("btn-drop");
nav_drop = document.getElementById("navDropdown");

btn_drop.addEventListener("click", function(){
  nav_drop.classList.toggle("d-flex");
});
