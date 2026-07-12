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
const loadScanBtn = document.getElementById("load-scan-btn");
const saveResultsBtn = document.getElementById("save-results-btn");

// Global states
let currentBrowserPath = "";
let isScanning = false;
let resultsData = [];
let addedPaths = [];

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    loadDirectories();
    browseFolders();
    loadConfig();
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
    loadScanBtn.addEventListener("click", loadScan);
    saveResultsBtn.addEventListener("click", saveResults);
    const toast = document.getElementById("toast");
    if (toast) {
        toast.addEventListener("click", () => {
            toast.classList.add("hidden");
        });
    }
    setupConfigListeners();
}

// 1. Directory List Management
async function loadDirectories() {
    try {
        const response = await fetch(`${API_BASE}/api/directories?_t=${Date.now()}`);
        const dirs = await response.json();

        addedPaths = dirs.map(d => d.path);
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
            await loadDirectories();
            await browseFolders(currentBrowserPath);
            showToast("Directory added successfully!");
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
            await loadDirectories();
            await browseFolders(currentBrowserPath);
            showToast("Directory removed.");
        }
    } catch (err) {
        console.error("Failed to remove directory:", err);
    }
}

// 2. Folder Browser
async function browseFolders(path = "") {
    try {
        const url = path ? `${API_BASE}/api/browse?path=${encodeURIComponent(path)}&_t=${Date.now()}` : `${API_BASE}/api/browse?_t=${Date.now()}`;
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
            const isAdded = addedPaths.includes(f.path);
            const li = document.createElement("li");

            let actionHtml = "";
            if (isAdded) {
                actionHtml = `<span class="folder-status added">✓ Added</span>`;
            } else {
                actionHtml = `<span class="folder-select" onclick="addDirectory('${escapeJS(f.path)}')">Add</span>`;
            }

            li.innerHTML = `
                <span class="folder-name" onclick="browseFolders('${escapeJS(f.path)}')">📁 ${f.name}</span>
                ${actionHtml}
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
        const response = await fetch(`${API_BASE}/api/status?_t=${Date.now()}`);
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
        const response = await fetch(`${API_BASE}/api/status?_t=${Date.now()}`);
        const state = await response.json();

        if (state.status === "scanning") {
            progressBarFill.style.width = `${state.progress}%`;
            progressPercent.textContent = `${state.progress}%`;
            progressDesc.textContent = state.progress_msg || "Scanning...";

            const targetsDiv = document.getElementById("progress-targets");
            if (targetsDiv && state.targets && state.targets.length > 0) {
                targetsDiv.innerHTML = `<strong>Scanning Target(s):</strong><br><span style="opacity: 0.85;">${state.targets.join("<br>")}</span>`;
            } else if (targetsDiv) {
                targetsDiv.innerHTML = "";
            }

            setTimeout(pollProgress, 300);
        } else {
            isScanning = false;
            progressContainer.classList.add("hidden");
            if (state.status === "completed") {
                loadResults();
            } else {
                welcomeContainer.classList.remove("hidden");
                resultsContainer.classList.add("hidden");
                showToast("Scan was stopped. Hashing progress saved to database checkpoints.");
            }
        }
    } catch (err) {
        console.error("Poll progress failed:", err);
        isScanning = false;
        progressContainer.classList.add("hidden");
        welcomeContainer.classList.remove("hidden");
        resultsContainer.classList.add("hidden");
    }
}

// 4. Results Management
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/api/results?_t=${Date.now()}`);
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

            let msg = "Scan was stopped. Hashing progress saved to database checkpoints.";
            const scanned = result.scanned_count || 0;
            const reused = result.reused_count || 0;
            if (scanned > 0 || reused > 0) {
                msg += `\n- Saved ${scanned} new file hashes to cache.`;
                msg += `\n- Reused ${reused} cached file hashes.`;
                if (result.last_file) {
                    const filename = result.last_file.split("/").pop();
                    msg += `\n- Last scanned file: ${filename}`;
                }
            } else {
                msg += "\n- No files were processed.";
            }
            msg += "\n\n(Click this message to dismiss)";
            showToast(msg, true);
        }
    } catch (err) {
        console.error("Cancel scan failed:", err);
    }
}
// Helpers
function escapeJS(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// Configuration Management
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config?_t=${Date.now()}`);
        const config = await response.json();

        document.getElementById("pref-hardness").value = config.FilterHardness;
        document.getElementById("pref-hardness-val").innerText = config.FilterHardness + "%";
        document.getElementById("pref-mix-file-kind").checked = config.MixFileKind;
        document.getElementById("pref-use-regexp").checked = config.UseRegexp;
        document.getElementById("pref-ignore-hardlink").checked = config.IgnoreHardlinkMatches;
        document.getElementById("pref-remove-empty").checked = config.RemoveEmptyFolders;
        document.getElementById("pref-rehash-ignore-mtime").checked = config.RehashIgnoreMTime;
        document.getElementById("pref-include-exists").checked = config.IncludeExistsCheck;
        document.getElementById("pref-checkpoint").value = config.CheckpointFrequency;
    } catch (err) {
        console.error("Failed to load config:", err);
    }
}

async function saveConfig() {
    const config = {
        FilterHardness: parseInt(document.getElementById("pref-hardness").value),
        MixFileKind: document.getElementById("pref-mix-file-kind").checked,
        UseRegexp: document.getElementById("pref-use-regexp").checked,
        IgnoreHardlinkMatches: document.getElementById("pref-ignore-hardlink").checked,
        RemoveEmptyFolders: document.getElementById("pref-remove-empty").checked,
        RehashIgnoreMTime: document.getElementById("pref-rehash-ignore-mtime").checked,
        IncludeExistsCheck: document.getElementById("pref-include-exists").checked,
        CheckpointFrequency: parseInt(document.getElementById("pref-checkpoint").value) || 100
    };

    try {
        await fetch(`${API_BASE}/api/config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config)
        });
    } catch (err) {
        console.error("Failed to save config:", err);
    }
}

function setupConfigListeners() {
    const hardnessSlider = document.getElementById("pref-hardness");
    const hardnessVal = document.getElementById("pref-hardness-val");
    hardnessSlider.addEventListener("input", (e) => {
        hardnessVal.innerText = e.target.value + "%";
    });

    hardnessSlider.addEventListener("change", saveConfig);
    document.getElementById("pref-mix-file-kind").addEventListener("change", saveConfig);
    document.getElementById("pref-use-regexp").addEventListener("change", saveConfig);
    document.getElementById("pref-ignore-hardlink").addEventListener("change", saveConfig);
    document.getElementById("pref-remove-empty").addEventListener("change", saveConfig);
    document.getElementById("pref-rehash-ignore-mtime").addEventListener("change", saveConfig);
    document.getElementById("pref-include-exists").addEventListener("change", saveConfig);
    document.getElementById("pref-checkpoint").addEventListener("change", saveConfig);
}

async function loadScan() {
    const path = prompt("Enter the absolute file path to a saved .dupegururesults file to load:");
    if (!path) return;
    try {
        const response = await fetch(`${API_BASE}/api/results/load`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path.trim() })
        });
        const result = await response.json();
        if (result.success) {
            alert("Scan results loaded successfully!");
            welcomeContainer.classList.add("hidden");
            resultsContainer.classList.remove("hidden");
            loadResults();
        } else {
            alert("Error loading scan: " + result.error);
        }
    } catch (err) {
        console.error("Load scan failed:", err);
    }
}

async function saveResults() {
    const path = prompt("Enter the absolute file path where you want to save the results (e.g. /path/to/results.dupegururesults):");
    if (!path) return;
    try {
        const response = await fetch(`${API_BASE}/api/results/save`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path.trim() })
        });
        const result = await response.json();
        if (result.success) {
            alert("Results saved successfully!");
        } else {
            alert("Error saving results: " + result.error);
        }
    } catch (err) {
        console.error("Save results failed:", err);
    }
}

function showToast(message, persistent = false) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");

    if (toast.timeoutId) {
        clearTimeout(toast.timeoutId);
        toast.timeoutId = null;
    }

    if (!persistent) {
        toast.timeoutId = setTimeout(() => {
            toast.classList.add("hidden");
            toast.timeoutId = null;
        }, 3000);
    }
}
