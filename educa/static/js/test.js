let form = document.querySelector('#myForm');
let errorAlert = document.querySelector('#errorAlert');
let successAlert = document.querySelector('#successAlert');
let h1 = document.querySelector('#title');
let data = "";
let errors = 0;
// Create an Ajax request
let request = new XMLHttpRequest();

function fn(){
	form.addEventListener('submit', function(event) {
		// In this case we are doing a POST request.
		request.open('POST', '/process', true);
		request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    // pass data as a query string(flask converts it into a multi_dict)
    data = ["name=" + document.querySelector('#nameInput').value + "&" + "email=" + document.querySelector('#emailInput').value];
		request.send(data);

    // event handler : checks the state of the request,
    // if it is done do something
    request.onreadystatechange = function() {
      if (request.readyState == XMLHttpRequest.DONE) {
        data = JSON.parse(request.responseText);
        if(data.error){
          error = `<div id="errorAlert" class="col-9 my-1 alert alert-danger alert-dismissible fade show text-center" role="alert" style="display: none;">
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                          <span aria-hidden="true">&times;</span>
                        </button>
                      </div>`;
          
          h1.insertAdjacentHTML('afterend', error);
          errorAlert = document.querySelector('#errorAlert');
          let text = document.createTextNode(data.error);
          if (errors < 1) {
            errorAlert.appendChild(text);
          }
          errorAlert.style.display = "block";
          successAlert.style.display = "none";
          errors++;
        } else {
          success = `<div id="successAlert" class="col-9 my-1 alert alert-success alert-dismissible fade show text-center" role="alert" style="display: none;">
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                          <span aria-hidden="true">&times;</span>
                        </button>
                      </div>`;
          h1.insertAdjacentHTML('afterend', success);
          successAlert = document.querySelector('#successAlert');
          let text = document.createTextNode(data.name);
          successAlert.appendChild(text);
          successAlert.style.display = "block";
          errorAlert.style.display = "none";
        }
      }
    }

		// prevent request from being sent through HTML Form
		event.preventDefault();
	});
}

function ready(fn) {
  if (document.readyState !== 'loading'){
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

ready(fn);
