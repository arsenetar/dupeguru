// dupeGuru Web Console Frontend

const API_BASE = "";

// Element Selectors
const manualPathInput = document.getElementById("manual-path-input");
const addManualPathBtn = document.getElementById("add-manual-path-btn");
const currentDirSpan = document.getElementById("current-dir-span");
const folderList = document.getElementById("folder-list");
const browserUpBtn = document.getElementById("browser-up-btn");
const directoriesList = document.getElementById("directories-list");
const startScanBtn = document.getElementById("start-scan-btn");

const progressContainer = document.getElementById("progress-container");
const progressBarFill = document.getElementById("progress-bar-fill");
const progressDesc = document.getElementById("progress-desc");
const progressPercent = document.getElementById("progress-percent");

const welcomeContainer = document.getElementById("welcome-container");
const resultsContainer = document.getElementById("results-container");
const resultsSummary = document.getElementById("results-summary");
const resultsBody = document.getElementById("results-body");
const deleteMarkedBtn = document.getElementById("delete-marked-btn");
const cancelScanBtn = document.getElementById("cancel-scan-btn");

// Global states
let currentBrowserPath = "";
let isScanning = false;
let resultsData = [];

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    loadDirectories();
    browseFolders();
    setupEventListeners();
    // Regular status polling (for progress sync)
    setInterval(checkScanStatus, 1000);
});

function setupEventListeners() {
    addManualPathBtn.addEventListener("click", () => {
        const path = manualPathInput.value.trim();
        if (path) {
            addDirectory(path);
            manualPathInput.value = "";
        }
    });

    manualPathInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            addManualPathBtn.click();
        }
    });

    browserUpBtn.addEventListener("click", () => {
        if (currentBrowserPath && currentBrowserPath.includes("/")) {
            const parts = currentBrowserPath.split("/");
            parts.pop();
            const parent = parts.join("/") || "/";
            browseFolders(parent);
        }
    });

    startScanBtn.addEventListener("click", startScan);
    deleteMarkedBtn.addEventListener("click", deleteMarked);
    cancelScanBtn.addEventListener("click", cancelScan);
}

// 1. Directory List Management
async function loadDirectories() {
    try {
        const response = await fetch(`${API_BASE}/api/directories`);
        const dirs = await response.json();
        
        directoriesList.innerHTML = "";
        if (dirs.length === 0) {
            directoriesList.innerHTML = `<li class="path-text" style="justify-content: center; opacity: 0.5;">No folders added yet</li>`;
            startScanBtn.disabled = true;
            return;
        }

        startScanBtn.disabled = false;
        dirs.forEach((d, idx) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span class="path-text" title="${d.path}">${d.path}</span>
                <button class="btn icon-btn" onclick="removeDirectory(${idx})">×</button>
            `;
            directoriesList.appendChild(li);
        });
    } catch (err) {
        console.error("Failed to load directories:", err);
    }
}

async function addDirectory(path) {
    try {
        const response = await fetch(`${API_BASE}/api/directories`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path })
        });
        const result = await response.json();
        if (result.success) {
            loadDirectories();
        } else {
            alert("Error adding path: " + (result.error || "Invalid path"));
        }
    } catch (err) {
        console.error("Failed to add directory:", err);
    }
}

async function removeDirectory(index) {
    try {
        const response = await fetch(`${API_BASE}/api/directories?index=${index}`, {
            method: "DELETE"
        });
        const result = await response.json();
        if (result.success) {
            loadDirectories();
        }
    } catch (err) {
        console.error("Failed to remove directory:", err);
    }
}

// 2. Folder Browser
async function browseFolders(path = "") {
    try {
        const url = path ? `${API_BASE}/api/browse?path=${encodeURIComponent(path)}` : `${API_BASE}/api/browse`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            console.error("Browse error:", data.error);
            return;
        }

        currentBrowserPath = data.current;
        currentDirSpan.textContent = currentBrowserPath;
        currentDirSpan.title = currentBrowserPath;

        folderList.innerHTML = "";
        data.folders.forEach(f => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span class="folder-name" onclick="browseFolders('${escapeJS(f.path)}')">📁 ${f.name}</span>
                <span class="folder-select" onclick="addDirectory('${escapeJS(f.path)}')">Add</span>
            `;
            folderList.appendChild(li);
        });
    } catch (err) {
        console.error("Browse folders failed:", err);
    }
}

// 3. Scan & Progress Management
async function startScan() {
    try {
        const response = await fetch(`${API_BASE}/api/scan`, {
            method: "POST"
        });
        const result = await response.json();
        if (result.success) {
            isScanning = true;
            progressContainer.classList.remove("hidden");
            welcomeContainer.classList.add("hidden");
            resultsContainer.classList.add("hidden");
            pollProgress();
        } else {
            alert("Could not start scan: " + result.error);
        }
    } catch (err) {
        console.error("Start scan failed:", err);
    }
}

async function checkScanStatus() {
    // Light status checks to sync UI
    if (isScanning) return;
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const state = await response.json();
        if (state.status === "scanning") {
            isScanning = true;
            progressContainer.classList.remove("hidden");
            welcomeContainer.classList.add("hidden");
            resultsContainer.classList.add("hidden");
            pollProgress();
        }
    } catch (err) {
        console.error("Check status failed:", err);
    }
}

async function pollProgress() {
    if (!isScanning) return;
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const state = await response.json();
        
        if (state.status === "scanning") {
            progressBarFill.style.width = `${state.progress}%`;
            progressPercent.textContent = `${state.progress}%`;
            progressDesc.textContent = state.progress_msg || "Scanning...";
            setTimeout(pollProgress, 300);
        } else {
            isScanning = false;
            progressContainer.classList.add("hidden");
            loadResults();
        }
    } catch (err) {
        console.error("Poll progress failed:", err);
        isScanning = false;
        progressContainer.classList.add("hidden");
    }
}

// 4. Results Management
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/api/results`);
        resultsData = await response.json();
        
        renderResults();
    } catch (err) {
        console.error("Load results failed:", err);
    }
}

function renderResults() {
    resultsBody.innerHTML = "";
    welcomeContainer.classList.add("hidden");
    resultsContainer.classList.remove("hidden");

    let totalGroups = resultsData.length;
    let totalFiles = 0;
    let markedCount = 0;
    
    if (totalGroups === 0) {
        resultsSummary.textContent = "No duplicates found.";
        resultsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary);">Your scan completed. No duplicate files were found!</td></tr>`;
        deleteMarkedBtn.disabled = true;
        return;
    }

    resultsData.forEach(group => {
        // Group Header separating rows
        const headerRow = document.createElement("tr");
        headerRow.className = "group-header-row";
        headerRow.innerHTML = `
            <td colspan="6">Duplicate Group (Max Match: ${group.percentage}%)</td>
        `;
        resultsBody.appendChild(headerRow);

        group.files.forEach(file => {
            totalFiles++;
            if (file.marked) markedCount++;

            const row = document.createElement("tr");
            if (file.is_ref) {
                row.className = "ref-row";
            }

            const checkboxHtml = file.is_ref 
                ? `<span style="font-size: 0.75rem; padding: 2px 6px; background: rgba(85, 239, 196, 0.15); border-radius: 4px;">REF</span>`
                : `
                    <label class="checkbox-container">
                        <input type="checkbox" ${file.marked ? "checked" : ""} onchange="toggleMark('${escapeJS(file.path)}', this.checked)">
                        <span class="checkmark"></span>
                    </label>
                `;

            row.innerHTML = `
                <td style="text-align: center;">${checkboxHtml}</td>
                <td style="color: var(--accent); font-weight: 500;">${file.is_ref ? "-" : file.percentage + "%"}</td>
                <td title="${file.name}" style="font-weight: 500;">${file.name}</td>
                <td title="${file.path}" style="font-size: 0.8rem; font-family: monospace; color: var(--text-secondary); max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${file.folder}</td>
                <td>${file.size}</td>
                <td style="color: var(--text-secondary); font-size: 0.8rem;">${file.mtime}</td>
            `;
            resultsBody.appendChild(row);
        });
    });

    resultsSummary.textContent = `Found ${totalGroups} duplicate groups (${totalFiles} total files). ${markedCount} files currently marked for deletion.`;
    deleteMarkedBtn.disabled = markedCount === 0;
    deleteMarkedBtn.textContent = `Delete ${markedCount} Marked File(s)`;
}

async function toggleMark(path, isChecked) {
    try {
        const response = await fetch(`${API_BASE}/api/results/mark`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path, marked: isChecked })
        });
        const result = await response.json();
        if (result.success) {
            // Update local state to save load requests
            resultsData.forEach(group => {
                group.files.forEach(file => {
                    if (file.path === path) {
                        file.marked = isChecked;
                    }
                });
            });
            // Recount and update texts
            let markedCount = 0;
            resultsData.forEach(group => {
                group.files.forEach(file => {
                    if (file.marked) markedCount++;
                });
            });
            resultsSummary.textContent = `Found ${resultsData.length} duplicate groups. ${markedCount} files currently marked for deletion.`;
            deleteMarkedBtn.disabled = markedCount === 0;
            deleteMarkedBtn.textContent = `Delete ${markedCount} Marked File(s)`;
        }
    } catch (err) {
        console.error("Toggle mark failed:", err);
    }
}

async function deleteMarked() {
    if (!confirm("Are you sure you want to permanently delete the marked duplicate files? This cannot be undone.")) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE}/api/results/delete`, {
            method: "POST"
        });
        const result = await response.json();
        if (result.success) {
            alert("Marked files deleted successfully!");
            loadResults();
        }
    } catch (err) {
        console.error("Delete marked failed:", err);
    }
}
async function cancelScan() {
    try {
        const response = await fetch(`${API_BASE}/api/scan/cancel`, {
            method: "POST"
        });
        const result = await response.json();
        if (result.success) {
            isScanning = false;
            progressContainer.classList.add("hidden");
            welcomeContainer.classList.remove("hidden");
            loadDirectories();
        }
    } catch (err) {
        console.error("Cancel scan failed:", err);
    }
}
// Helpers
function escapeJS(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}
