const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const generateBtn = document.getElementById("generateBtn");
const statusEl = document.getElementById("status");
const spinner = document.getElementById("spinner");
const statusText = document.getElementById("statusText");
const downloads = document.getElementById("downloads");
const courseTitle = document.getElementById("courseTitle");
const downloadDocx = document.getElementById("downloadDocx");
const downloadMd = document.getElementById("downloadMd");

let selectedFile = null;

// Click upload area to trigger file picker
dropZone.addEventListener("click", (e) => {
  if (e.target.tagName !== "LABEL") fileInput.click();
});

// Drag and drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith(".xlsx")) {
    selectFile(file);
  } else {
    showError("Please upload a .xlsx file");
  }
});

// File input change
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) selectFile(fileInput.files[0]);
});

function selectFile(file) {
  selectedFile = file;
  fileName.textContent = file.name;
  generateBtn.disabled = false;
  downloads.hidden = true;
  statusEl.hidden = true;
}

// Generate button
generateBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile);

  statusEl.hidden = false;
  statusEl.className = "status";
  spinner.style.display = "block";
  statusText.textContent = "Processing...";
  downloads.hidden = true;
  generateBtn.disabled = true;

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (response.ok && result.status === "success") {
      spinner.style.display = "none";
      statusEl.className = "status success";
      statusText.textContent = "Documents generated successfully!";
      courseTitle.textContent = result.course_title;
      downloadDocx.href = result.files.docx;
      downloadMd.href = result.files.md;
      downloads.hidden = false;
    } else {
      showError(result.detail || "Generation failed");
    }
  } catch (err) {
    showError(err.message);
  }

  generateBtn.disabled = false;
});

function showError(message) {
  spinner.style.display = "none";
  statusEl.hidden = false;
  statusEl.className = "status error";
  statusText.textContent = "Error: " + message;
}
