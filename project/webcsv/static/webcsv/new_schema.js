let formSetPrefix = document.querySelector('#newRow').getAttribute('data-base_prefix');
let dataWithExtra = document.querySelector('#newRow').getAttribute('data-with_extra');
let newRowContainer = document.getElementById('newRow');
let totalCountForms = document.querySelector(`input[name='${formSetPrefix}-TOTAL_FORMS']`);
let emptyForm = totalCountForms.value;

updateRowElementsId(newRowContainer, true);
checkAllSelectorsType();

function addRow() {
	let newRow = newRowContainer.firstElementChild.cloneNode(true);
	updateRowElementsId(newRow);
	document.getElementById('addedRows').appendChild(newRow);
	let formSetError = document.getElementById('non_form_errors');
	if (formSetError) {
		formSetError.remove();
	}
}

function updateRowElementsId(newRow, initial = false) {
	let replacedPrefix, count, newPrefix;

	if (initial) {
		replacedPrefix = `${formSetPrefix}-${totalCountForms.value - 1}`;
		newPrefix = `${formSetPrefix}-new`;
	} else {
		replacedPrefix = `${formSetPrefix}-new`;
		count = totalCountForms.value++ - emptyForm;
		newPrefix = `${formSetPrefix.split('-')[0]}-${count}`;
	}

	newRow.querySelectorAll('label').forEach((label) => {
		label.htmlFor = label.htmlFor.replace(replacedPrefix, newPrefix);
	});
	newRow.querySelectorAll('input').forEach((input) => {
		input.name = input.name.replace(replacedPrefix, newPrefix);
		input.id = input.id.replace(replacedPrefix, newPrefix);
		if (!initial && !input.hidden) {
			input.required = true;
		}
	});
	newRow.querySelectorAll('select').forEach((select) => {
		let oldSelect = document.getElementById(select.id);
		select.options[oldSelect.selectedIndex].setAttribute("selected", "");
		select.name = select.name.replace(replacedPrefix, newPrefix);
		select.id = select.id.replace(replacedPrefix, newPrefix);
		if (select.id.endsWith('datatype')) {
			select.onchange = checkSelectorType;
		}
	});
}

function deleteColumn(event) {
	let row = event.target.parentElement.parentElement;
	if (row.parentElement.id === 'addedRows') {
		row.remove();
		totalCountForms.value--;
	}
}

function checkAllSelectorsType() {
	document.querySelectorAll("select[id$='-datatype']").forEach(select => {
		checkSelectorType(select);
		select.onchange = checkSelectorType;
	});
}

function checkSelectorType(event) {
	let select;
	if (event.target) {
		select = event.target;
	} else {
		select = event;
	}
	let currentPrefix = select.id.substr(0, select.id.lastIndexOf('-datatype'));
	if (!dataWithExtra.includes(select.value)) {
		document.querySelector(`label[for='${currentPrefix}-to_column']`).hidden = true;
		document.querySelector(`input#${currentPrefix}-to_column`).hidden = true;
		document.querySelector(`label[for='${currentPrefix}-from_column']`).hidden = true;
		document.querySelector(`input#${currentPrefix}-from_column`).hidden = true;
	} else {
		document.querySelector(`label[for='${currentPrefix}-to_column']`).hidden = false;
		document.querySelector(`input#${currentPrefix}-to_column`).hidden = false;
		document.querySelector(`label[for='${currentPrefix}-from_column']`).hidden = false;
		document.querySelector(`input#${currentPrefix}-from_column`).hidden = false;
	}
}