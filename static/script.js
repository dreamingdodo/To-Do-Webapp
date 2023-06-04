// script.js

function toggleCollapse(id, button) {
  var container = document.getElementById(id);
  container.classList.toggle('collapsed');
  toggleButtonText(button);
}

function toggleSaveButton(input) {
  var saveButton = input.parentNode.querySelector('.save-button');
  if (input.value.trim() === '') {
    saveButton.style.display = 'none';
  } else {
    saveButton.style.display = 'inline-block';
  }
}

function toggleButtonText(button) {
  var arrow = button.querySelector('.arrow');
  arrow.classList.toggle('down');
  arrow.classList.toggle('right');
}


function showAddForm() {
  var addForm = document.getElementById('add-form');
  addForm.classList.toggle('hidden');
  toggleButtonText(document.getElementById('add-button'));
}

function showEditForm(id) {
  var editForm = document.getElementById('edit-form-' + id);
  editForm.classList.toggle('hidden');
  toggleButtonText(document.getElementById('edit-button-' + id));
}

function toggleDarkMode() {
  var body = document.getElementsByTagName("body")[0];
  body.classList.toggle("dark-mode");
  var darkMode = body.classList.contains("dark-mode");
  updateDarkModePreference(darkMode); // Update dark mode preference
  updateDarkModeToggleButton(darkMode);
}

function updateDarkModePreference(darkMode) {
  // store preference in  localStorage:
  localStorage.setItem("darkModePreference", darkMode ? "1" : "0");
}

function updateDarkModeToggleButton(darkMode) {
  var darkModeToggleButton = document.getElementById("dark-mode-toggle-button");
  darkModeToggleButton.textContent = darkMode ? "Change to Light Mode" : "Change to Dark Mode";
}

// Retrieve the user's dark mode preference from localStorage
var darkModePreference = localStorage.getItem("darkModePreference");
if (darkModePreference === "1") {
  document.body.classList.add("dark-mode"); // Set the mode to dark mode
}

// Update the dark mode toggle button based on the retrieved preference
updateDarkModeToggleButton(document.body.classList.contains("dark-mode"));

// Add event listener to the dark mode toggle button
var darkModeToggleButton = document.getElementById("dark-mode-toggle-button");
darkModeToggleButton.addEventListener("click", toggleDarkMode);

xhr.send();
