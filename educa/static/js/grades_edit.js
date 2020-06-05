let form = document.querySelector("#grades");
let request = new XMLHttpRequest();

function loaded() {
  form.addEventListener("submit", function(event){
    let data = {}

    request.open("POST", window.location.pathname, true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");

    let fields = document.forms["grades"].querySelectorAll('input');

    request.onreadystatechange = function() {
      if (request.readyState == 4 && request.status == 200) {
        errors = JSON.parse(request.responseText);

        console.log(errors);
        // if the request has an error
        if (Object.keys(errors).length > 0) {
          // Remove previous errors to make room for new errors
          fields.forEach(function(item, index, array){
            item.classList.remove("is-invalid");
            smallTag = document.querySelector(`#${item.id}_error`);
            smallTag.innerText = "";
          });

          for(const key in errors){
            field = document.querySelector(`#${key}`);
            smallTag = document.querySelector(`#${key}_error`);
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

    event.preventDefault();
  });
}

function ready(loaded) {
  if (document.readyState !== "loading"){
    loaded();
  } else {
    document.addEventListener("DOMContentLoaded", loaded);
  }
}

ready(loaded);
