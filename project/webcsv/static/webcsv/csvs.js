let schemaId = document.querySelector('table').getAttribute('data-schema_id');
let statusPending = document.querySelector('table').getAttribute('data-status_pending');
let checkCsvUrl = document.querySelector('table').getAttribute('data-check-csv-url');
let genCsvUrl = document.querySelector('form').getAttribute('data-gen-csv-url');
let csvIdAttr = 'data-csv_id';
let dataStatus = 'data-status';
let pendingCSV = [];
let pendingWaitTime = 5000;
initialCheckStatus();

function initialCheckStatus() {
	let csvs = document.querySelectorAll(`button[${dataStatus}='${statusPending}']`);
	csvs.forEach(csv => {
		pendingCSV.push(+csv.getAttribute(csvIdAttr));
	});
	if (pendingCSV.length) {
		setTimeout(() => {
			updatePendingStatus();
		}, pendingWaitTime);
	}
}

function updatePendingStatus(csv_id) {
	if (pendingCSV.length) {
		let data = JSON.stringify({
			'pendingCSV': pendingCSV,
		});
		ajaxData(checkCsvUrl, data, method = 'POST', onSuccessFunc = onSuccessGetStatus);
	}
}

function onSuccessGetStatus(response) {
	let readyCSV = response.result.ready_csv;
	let errorCSV = response.result.error_csv;
	pendingCSV = response.result.pending_csv;

	for (csvId of readyCSV) {
		let currentButton = document.querySelector(`button[${csvIdAttr}='${csvId}']`);
		let downloadLink = document.querySelector(`a[${csvIdAttr}='${csvId}']`);

		currentButton.removeAttribute(dataStatus);
		currentButton.innerText = 'Ready';
		currentButton.classList.remove('btn-secondary');
		currentButton.classList.add('btn-success');

		downloadLink.hidden = false;
	}
	for (csvId of errorCSV) {
		let currentButton = document.querySelector(`button[${csvIdAttr}='${csvId}']`);

		currentButton.removeAttribute(dataStatus);
		currentButton.innerText = 'Error';
		currentButton.classList.remove('btn-secondary');
		currentButton.classList.add('btn-danger');
	}
	if (pendingCSV.length) {
		setTimeout(() => {
			updatePendingStatus();
		}, pendingWaitTime);
	}
}


function generateCSV(event) {
	event.preventDefault();
	let form = event.target;
	let lastCSV = document.querySelector('#allCSV').lastElementChild;

	let data = JSON.stringify({
		'count': form.querySelector("input[name='count']").value,
		'lastNumber': lastCSV ? lastCSV.querySelector("#order-csv").innerText : 0,
	});

	ajaxData(genCsvUrl, data, method = 'POST', onSuccessFunc = (response) => {
			document.querySelector('#allCSV').insertAdjacentHTML('beforeend', response.result);
			pendingCSV.push(response.csv_id);
			setTimeout(() => {
				updatePendingStatus();
			}, pendingWaitTime);
		}
	);
}

function ajaxData(url, data, method = 'POST',
                  onSuccessFunc = (data) => (console.log(data)),
                  onErrorFunc = (data) => (console.log(data))) {
	let headers = {
		'credentials': 'same-origin',
		'Content-Type': 'application/json',
		'X-Requested-With': 'XMLHttpRequest',
		"X-CSRFToken": document.querySelector("input[name='csrfmiddlewaretoken']").value
	};

	fetch(url, {
		method: method,
		body: data,
		headers: headers
	}).then(response => response.json())
		.then(data => {
			data.error_ajax ? onErrorFunc(data) : onSuccessFunc(data);
		})
		.catch(error => onErrorFunc(error));
}
