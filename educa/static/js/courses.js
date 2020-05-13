const BLUE = "#007bff";
const RED = "#dc3545";
const YELLOW = "#ffc107";
const GREEN = "#28a745";
const PURPLE = "#6E2594";
const PINK = "#EBBAB9";
let i = 0;

let colors = [BLUE, RED, YELLOW, GREEN, PURPLE, PINK]
let courseHeaders = document.querySelectorAll(".card-title-header");

courseHeaders.forEach(function(item, index, array){
  if (i > colors.length-1) {
    i = 0;
  }

  item.style.backgroundColor = colors[i];
  i++;
});
