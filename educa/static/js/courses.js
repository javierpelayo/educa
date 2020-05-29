const BLUE = "#3F88C5";
const RED = "#D00814";
const YELLOW = "#FEBA2C";
const GREEN = "#136F63";
const NAVY = "#022B43";
let i = 0;

let colors = [YELLOW, RED, GREEN, BLUE]
let courseHeaders = document.querySelectorAll(".card-course-header");

courseHeaders.forEach(function(item, index, array){
  if (i > colors.length-1) {
    i = 0;
  }

  item.style.backgroundColor = colors[i];
  i++;
});
