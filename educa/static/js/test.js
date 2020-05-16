let form = document.querySelector('#myForm');
let errorAlert = document.querySelector('#errorAlert');
let successAlert = document.querySelector('#successAlert');
let h1 = document.querySelector('#title');
let data;
let text;

let errorHTML = `<div id="errorAlert" class="col-9 my-1 alert alert-danger alert-dismissible fade show text-center" role="alert">
							<button type="button" class="close" data-dismiss="alert" aria-label="Close">
								<span aria-hidden="true">&times;</span>
							</button>
						</div>`;
let successHTML = `<div id="successAlert" class="col-9 my-1 alert alert-success alert-dismissible fade show text-center" role="alert">
		              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
		                <span aria-hidden="true">&times;</span>
		              </button>
		            </div>`;

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

				// checks if the alerts exist(in-case user has dismissed them)
				errorAlert = document.querySelector('#errorAlert');
				successAlert = document.querySelector('#successAlert');

				// if the request has an error
        if(data.error){
					// if the alert already exists
					if(errorAlert) {
						errorAlert.parentNode.removeChild(errorAlert);
					} else if(successAlert) {
						successAlert.parentNode.removeChild(successAlert);
					}

          h1.insertAdjacentHTML('afterend', errorHTML);
          errorAlert = document.querySelector('#errorAlert');
          text = document.createTextNode(data.error);
          errorAlert.appendChild(text);
        } else {
					if(successAlert) {
						successAlert.parentNode.removeChild(successAlert);
					} else if (errorAlert) {
						errorAlert.parentNode.removeChild(errorAlert);
					}

          h1.insertAdjacentHTML('afterend', successHTML);
          successAlert = document.querySelector('#successAlert');
          text = document.createTextNode(data.name);
          successAlert.appendChild(text);
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
