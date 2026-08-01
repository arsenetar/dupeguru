// de-dup Web Console Frontend

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
let isStopping = false;
let cancelStats = null;
let resultsData = [];
let addedPaths = [];

// Cache Viewer state
let cacheSearch = "";
let cacheLimit = 20;
let cacheOffset = 0;
let cacheTotal = 0;

// Scan results pagination state
let resultsLimit = 50;
let resultsOffset = 0;
let resultsTotal = 0;

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    loadDirectories();
    browseFolders();
    loadConfig();
    loadMultiScans();
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

    startScanBtn.addEventListener("click", () => {
        const scanModal = document.getElementById("scan-modal");
        if (scanModal) {
            scanModal.classList.remove("hidden");
        }
    });

    const modeResume = document.getElementById("mode-resume");
    const modeFresh = document.getElementById("mode-fresh");
    const cancelModalBtn = document.getElementById("cancel-modal-btn");
    const scanModal = document.getElementById("scan-modal");

    if (modeResume) {
        modeResume.addEventListener("click", () => {
            if (scanModal) scanModal.classList.add("hidden");
            startScan(false);
        });
    }

    if (modeFresh) {
        modeFresh.addEventListener("click", () => {
            if (scanModal) scanModal.classList.add("hidden");
            startScan(true);
        });
    }

    if (cancelModalBtn) {
        cancelModalBtn.addEventListener("click", () => {
            if (scanModal) scanModal.classList.add("hidden");
        });
    }

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

    // Navigation Tabs setup
    const tabScan = document.getElementById("tab-scan");
    const tabMultiscan = document.getElementById("tab-multiscan");
    const tabCrossDb = document.getElementById("tab-cross-db");
    const tabCache = document.getElementById("tab-cache");

    const scanViewContent = document.getElementById("scan-view-content");
    const multiscanContainer = document.getElementById("multiscan-container");
    const crossDbContainer = document.getElementById("cross-db-container");
    const cacheContainer = document.getElementById("cache-container");

    function activateTab(activeTab, activeContainer) {
        [tabScan, tabMultiscan, tabCrossDb, tabCache].forEach(t => t && t.classList.remove("active"));
        [scanViewContent, multiscanContainer, crossDbContainer, cacheContainer].forEach(c => c && c.classList.add("hidden"));
        if (activeTab) activeTab.classList.add("active");
        if (activeContainer) activeContainer.classList.remove("hidden");
    }

    if (tabScan) {
        tabScan.addEventListener("click", () => activateTab(tabScan, scanViewContent));
    }
    if (tabMultiscan) {
        tabMultiscan.addEventListener("click", () => {
            activateTab(tabMultiscan, multiscanContainer);
            loadMultiScans();
        });
    }
    if (tabCrossDb) {
        tabCrossDb.addEventListener("click", () => {
            activateTab(tabCrossDb, crossDbContainer);
            loadCrossDBSelectionList();
        });
    }
    if (tabCache) {
        tabCache.addEventListener("click", () => {
            activateTab(tabCache, cacheContainer);
            loadCache();
        });
    }

    // New Scan Modal listeners
    const newScanBtn = document.getElementById("new-scan-task-btn");
    const newScanModal = document.getElementById("new-scan-modal");
    const cancelNewScanBtn = document.getElementById("cancel-new-scan-btn");
    const submitNewScanBtn = document.getElementById("submit-new-scan-btn");

    if (newScanBtn) {
        newScanBtn.addEventListener("click", () => {
            if (newScanModal) newScanModal.classList.remove("hidden");
        });
    }
    if (cancelNewScanBtn) {
        cancelNewScanBtn.addEventListener("click", () => {
            if (newScanModal) newScanModal.classList.add("hidden");
        });
    }
    const useSidebarPathsBtn = document.getElementById("use-sidebar-paths-btn");
    const newScanPathInput = document.getElementById("new-scan-path-input");

    if (useSidebarPathsBtn && newScanPathInput) {
        useSidebarPathsBtn.addEventListener("click", () => {
            if (addedPaths && addedPaths.length > 0) {
                newScanPathInput.value = addedPaths[0];
            } else if (currentBrowserPath) {
                newScanPathInput.value = currentBrowserPath;
            }
        });
    }

    if (submitNewScanBtn) {
        submitNewScanBtn.addEventListener("click", launchNewDBScan);
    }

    const refreshScansBtn = document.getElementById("refresh-scans-btn");
    if (refreshScansBtn) {
        refreshScansBtn.addEventListener("click", () => {
            loadMultiScans();
            showToast("Scan database tasks refreshed.");
        });
    }

    const cachePrevBtn = document.getElementById("cache-prev-btn");
    const cacheNextBtn = document.getElementById("cache-next-btn");
    const cacheSearchInput = document.getElementById("cache-search");

    if (cachePrevBtn) {
        cachePrevBtn.addEventListener("click", () => {
            if (cacheOffset >= cacheLimit) {
                cacheOffset -= cacheLimit;
                loadCache();
            }
        });
    }

    if (cacheNextBtn) {
        cacheNextBtn.addEventListener("click", () => {
            if (cacheOffset + cacheLimit < cacheTotal) {
                cacheOffset += cacheLimit;
                loadCache();
            }
        });
    }

    if (cacheSearchInput) {
        let searchTimeout = null;
        cacheSearchInput.addEventListener("input", () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                cacheOffset = 0;
                cacheSearch = cacheSearchInput.value.trim();
                loadCache();
            }, 300);
        });
    }

    const resultsPrevBtn = document.getElementById("results-prev-btn");
    const resultsNextBtn = document.getElementById("results-next-btn");

    if (resultsPrevBtn) {
        resultsPrevBtn.addEventListener("click", () => {
            if (resultsOffset >= resultsLimit) {
                resultsOffset -= resultsLimit;
                loadResults();
            }
        });
    }

    if (resultsNextBtn) {
        resultsNextBtn.addEventListener("click", () => {
            if (resultsOffset + resultsLimit < resultsTotal) {
                resultsOffset += resultsLimit;
                loadResults();
            }
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
async function startScan(clearCache = false) {
    try {
        const scanNameInput = document.getElementById("sidebar-scan-name-input");
        const scanName = scanNameInput ? scanNameInput.value.trim() : "";
        const response = await fetch(`${API_BASE}/api/scan`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ clear_cache: clearCache, name: scanName })
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
    if (isScanning || isStopping) return;
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
            if (isStopping) {
                progressDesc.textContent = "Stopping scan, writing database checkpoints...";
            } else {
                progressDesc.textContent = state.progress_msg || "Scanning...";
            }

            const targetsDiv = document.getElementById("progress-targets");
            if (targetsDiv && state.targets && state.targets.length > 0) {
                targetsDiv.innerHTML = `<strong>Scanning Target(s):</strong><br><span style="opacity: 0.85;">${state.targets.join("<br>")}</span>`;
            } else if (targetsDiv) {
                targetsDiv.innerHTML = "";
            }

            setTimeout(pollProgress, 300);
        } else {
            isScanning = false;
            isStopping = false;
            cancelScanBtn.disabled = false;
            progressContainer.classList.add("hidden");
            if (state.status === "completed") {
                loadResults();
            } else {
                welcomeContainer.classList.remove("hidden");
                resultsContainer.classList.add("hidden");

                if (cancelStats) {
                    let msg = "Scan was stopped. Hashing progress saved to database checkpoints.";
                    const scanned = cancelStats.scanned_count || 0;
                    const reused = cancelStats.reused_count || 0;
                    if (scanned > 0 || reused > 0) {
                        msg += `\n- Saved ${scanned} new file hashes to cache.`;
                        msg += `\n- Reused ${reused} cached file hashes.`;
                        if (cancelStats.last_file) {
                            const filename = cancelStats.last_file.split("/").pop();
                            msg += `\n- Last scanned file: ${filename}`;
                        }
                    } else {
                        msg += "\n- No files were processed.";
                    }
                    msg += "\n\n(Click this message to dismiss)";
                    showToast(msg, true);
                    cancelStats = null;
                } else {
                    showToast("Scan was stopped. Hashing progress saved to database checkpoints.");
                }
            }
        }
    } catch (err) {
        console.error("Poll progress failed:", err);
        if (isScanning) {
            setTimeout(pollProgress, 1000);
        }
    }
}

// 4. Results Management
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/api/results?limit=${resultsLimit}&offset=${resultsOffset}&_t=${Date.now()}`);
        const data = await response.json();

        resultsData = data.groups;
        resultsTotal = data.total;

        renderResults(data.total_marked);
    } catch (err) {
        console.error("Load results failed:", err);
    }
}

function renderResults(totalMarkedCount) {
    resultsBody.innerHTML = "";
    welcomeContainer.classList.add("hidden");
    resultsContainer.classList.remove("hidden");

    let totalGroups = resultsTotal;
    let totalFiles = 0;
    const paginationContainer = document.getElementById("results-pagination");

    if (totalGroups === 0) {
        resultsSummary.textContent = "No duplicates found.";
        resultsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary);">Your scan completed. No duplicate files were found!</td></tr>`;
        deleteMarkedBtn.disabled = true;
        if (paginationContainer) paginationContainer.classList.add("hidden");
        return;
    }

    if (paginationContainer) paginationContainer.classList.remove("hidden");

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

    // Update pagination info
    const resultsPrevBtn = document.getElementById("results-prev-btn");
    const resultsNextBtn = document.getElementById("results-next-btn");
    const resultsPageInfo = document.getElementById("results-page-info");

    const currentPage = Math.floor(resultsOffset / resultsLimit) + 1;
    const totalPages = Math.max(1, Math.ceil(resultsTotal / resultsLimit));

    if (resultsPageInfo) resultsPageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    if (resultsPrevBtn) resultsPrevBtn.disabled = resultsOffset === 0;
    if (resultsNextBtn) resultsNextBtn.disabled = resultsOffset + resultsLimit >= resultsTotal;

    const overallMarked = totalMarkedCount !== undefined ? totalMarkedCount : 0;
    resultsSummary.textContent = `Found ${totalGroups} duplicate groups. Showing page ${currentPage} of ${totalPages}. ${overallMarked} files marked for deletion.`;
    deleteMarkedBtn.disabled = overallMarked === 0;
    deleteMarkedBtn.textContent = `Delete ${overallMarked} Marked File(s)`;
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
            const overallMarked = result.total_marked !== undefined ? result.total_marked : 0;
            const currentPage = Math.floor(resultsOffset / resultsLimit) + 1;
            const totalPages = Math.max(1, Math.ceil(resultsTotal / resultsLimit));
            resultsSummary.textContent = `Found ${resultsTotal} duplicate groups. Showing page ${currentPage} of ${totalPages}. ${overallMarked} files marked for deletion.`;
            deleteMarkedBtn.disabled = overallMarked === 0;
            deleteMarkedBtn.textContent = `Delete ${overallMarked} Marked File(s)`;
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
        isStopping = true;
        cancelScanBtn.disabled = true;
        progressDesc.textContent = "Stopping scan, writing database checkpoints...";
        const response = await fetch(`${API_BASE}/api/scan/cancel`, {
            method: "POST"
        });
        const result = await response.json();
        if (result.success) {
            cancelStats = {
                scanned_count: result.scanned_count,
                reused_count: result.reused_count,
                last_file: result.last_file
            };
        } else {
            isStopping = false;
            cancelScanBtn.disabled = false;
            alert("Could not stop scan: " + (result.error || "Unknown error"));
        }
    } catch (err) {
        console.error("Cancel scan failed:", err);
        isStopping = false;
        cancelScanBtn.disabled = false;
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

// 6. Cache Database Viewer Management
async function loadCache() {
    try {
        const response = await fetch(`${API_BASE}/api/cache/files?search=${encodeURIComponent(cacheSearch)}&limit=${cacheLimit}&offset=${cacheOffset}`);
        const result = await response.json();
        if (result.success) {
            cacheTotal = result.total;
            renderCacheTable(result.files);
            renderCachePagination();
        }
    } catch (err) {
        console.error("Load cache failed:", err);
    }
}

function renderCacheTable(files) {
    const tbody = document.getElementById("cache-body");
    const totalEl = document.getElementById("cache-total");
    if (!tbody) return;

    totalEl.textContent = cacheTotal;
    tbody.innerHTML = "";

    if (files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; padding: 32px; color: var(--text-secondary);">No cached files found.</td></tr>`;
        return;
    }

    files.forEach(f => {
        const row = document.createElement("tr");

        // Path
        const pathTd = document.createElement("td");
        pathTd.className = "path-cell";
        pathTd.textContent = f.path;
        pathTd.title = f.path;

        // Size
        const sizeTd = document.createElement("td");
        sizeTd.textContent = f.size;

        // Date
        const dateTd = document.createElement("td");
        dateTd.textContent = f.entry_dt || "Unknown";

        row.appendChild(pathTd);
        row.appendChild(sizeTd);
        row.appendChild(dateTd);

        tbody.appendChild(row);
    });
}

function renderCachePagination() {
    const info = document.getElementById("cache-page-info");
    const prevBtn = document.getElementById("cache-prev-btn");
    const nextBtn = document.getElementById("cache-next-btn");
    if (!info || !prevBtn || !nextBtn) return;

    const currentPage = Math.floor(cacheOffset / cacheLimit) + 1;
    const totalPages = Math.ceil(cacheTotal / cacheLimit) || 1;

    info.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

// Helper to escape HTML characters
function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 7. Multi-DB Dashboard Management
async function loadMultiScans() {
    const scansGrid = document.getElementById("scans-grid");
    if (!scansGrid) return;

    try {
        const response = await fetch(`${API_BASE}/api/scans`);
        const tasks = await response.json();

        scansGrid.innerHTML = "";

        if (!tasks || tasks.length === 0) {
            scansGrid.innerHTML = `<div style="grid-column: 1 / -1; color: var(--text-secondary); font-size: 0.9rem; padding: 12px 0;">No scan databases created yet. Add directories in the sidebar and click <strong>Start Duplicate Scan</strong>.</div>`;
            return;
        }

        tasks.forEach(task => {
            const card = document.createElement("div");
            card.className = "section-card";
            card.style.position = "relative";
            card.style.display = "flex";
            card.style.flexDirection = "column";
            card.style.gap = "10px";

            let statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(99, 102, 241, 0.2); color: #818cf8;">${task.status}</span>`;
            if (task.status === "completed") {
                statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(16, 185, 129, 0.2); color: #34d399;">COMPLETED</span>`;
            } else if (task.status === "failed") {
                statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(239, 68, 68, 0.2); color: #f87171;">FAILED</span>`;
            }

            const sizeMb = (task.db_size_bytes / (1024 * 1024)).toFixed(2);

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 1rem; color: var(--text-primary);">${escapeHtml(task.name)}</h3>
                    ${statusBadge}
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); word-break: break-all;">
                    <strong>DB:</strong> ${escapeHtml(task.db_path)} (${sizeMb} MB)
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">
                    <strong>Folders:</strong> ${task.directories && task.directories.length ? task.directories.map(d => escapeHtml(d)).join(", ") : "All"}
                </div>
                <div style="display: flex; gap: 16px; font-size: 0.8rem; color: var(--text-secondary); margin-top: 2px;">
                    <span><strong>Matches:</strong> ${task.match_count || 0}</span>
                    <span><strong>Dupes:</strong> ${task.dupe_count || 0}</span>
                </div>
                <div style="margin-top: 6px; display: flex; gap: 8px; justify-content: flex-end;">
                    <button class="btn secondary-btn text-btn" style="font-size: 0.8rem;" onclick="viewTaskResults('${task.task_id}')">View Results</button>
                    <button class="btn danger-btn text-btn" style="font-size: 0.8rem;" onclick="deleteScanTask('${task.task_id}')">Delete DB</button>
                </div>
            `;

            scansGrid.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load multi-scans:", err);
    }
}

async function launchNewDBScan() {
    const nameInput = document.getElementById("new-scan-name-input");
    const pathInput = document.getElementById("new-scan-path-input");
    const modal = document.getElementById("new-scan-modal");

    const name = nameInput.value.trim() || "Scan";
    const path = pathInput.value.trim();

    if (!path) {
        showToast("Please enter a valid directory path.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/scans/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, directories: [path] }),
        });
        const result = await response.json();
        if (result.success) {
            showToast(`Launched isolated scan: ${name}`);
            if (modal) modal.classList.add("hidden");
            nameInput.value = "";
            pathInput.value = "";
            loadMultiScans();
        } else {
            showToast(`Error: ${result.error || "Failed to launch scan"}`);
        }
    } catch (err) {
        showToast(`Error: ${err.message}`);
    }
}

async function viewTaskResults(taskId) {
    showToast("Loading results for database task...");
    await loadResults();
}

async function deleteScanTask(taskId) {
    if (!confirm("Are you sure you want to delete this database scan task?")) return;
    try {
        const response = await fetch(`${API_BASE}/api/scans/delete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });
        const result = await response.json();
        if (result.success) {
            showToast("Database scan deleted.");
            loadMultiScans();
        }
    } catch (err) {
        showToast(`Failed to delete: ${err.message}`);
    }
}

// 8. Cross-DB Deduplication Management
async function loadCrossDBSelectionList() {
    const listEl = document.getElementById("cross-db-selection-list");
    const btn = document.getElementById("run-cross-match-btn");
    if (!listEl) return;

    try {
        const response = await fetch(`${API_BASE}/api/scans`);
        const tasks = await response.json();

        listEl.innerHTML = "";

        if (!tasks || tasks.length === 0) {
            listEl.innerHTML = `<p style="color: var(--text-secondary);">No database files found. Create scans first in the Multi-DB Dashboard.</p>`;
            if (btn) btn.disabled = true;
            return;
        }

        tasks.forEach(t => {
            const label = document.createElement("label");
            label.className = "pref-checkbox-label";
            label.style.display = "flex";
            label.style.alignItems = "center";
            label.style.gap = "12px";
            label.style.padding = "10px 14px";
            label.style.background = "var(--bg-secondary)";
            label.style.borderRadius = "8px";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.value = t.db_path;
            checkbox.className = "cross-db-checkbox";

            checkbox.addEventListener("change", updateCrossMatchButton);

            const sizeMb = (t.db_size_bytes / (1024 * 1024)).toFixed(2);
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${t.name} (${t.db_path}) — ${sizeMb} MB`));

            listEl.appendChild(label);
        });

        updateCrossMatchButton();
    } catch (err) {
        console.error("Failed to load cross-DB selection:", err);
    }
}

function updateCrossMatchButton() {
    const btn = document.getElementById("run-cross-match-btn");
    const checked = document.querySelectorAll(".cross-db-checkbox:checked");
    if (btn) {
        btn.disabled = checked.length < 2;
    }
}

async function runCrossMatch() {
    const checked = Array.from(document.querySelectorAll(".cross-db-checkbox:checked")).map(c => c.value);
    const resultsWrapper = document.getElementById("cross-results-wrapper");
    const resultsSummary = document.getElementById("cross-results-summary");

    if (checked.length < 2) return;

    try {
        showToast("Comparing hashes across selected databases...");
        const response = await fetch(`${API_BASE}/api/cross_scan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ db_paths: checked }),
        });
        const result = await response.json();

        if (result.success) {
            resultsWrapper.classList.remove("hidden");
            resultsSummary.textContent = `Found ${result.total_groups} duplicate groups matching across databases.`;
            renderCrossResultsTable(result.groups);
        } else {
            showToast(`Error: ${result.error}`);
        }
    } catch (err) {
        showToast(`Cross match error: ${err.message}`);
    }
}

function renderCrossResultsTable(groups) {
    const tbody = document.getElementById("cross-results-body");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!groups || groups.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 32px; color: var(--text-secondary);">No cross-database duplicate matches found.</td></tr>`;
        return;
    }

    groups.forEach(g => {
        g.files.forEach((f, fIdx) => {
            const row = document.createElement("tr");
            if (fIdx === 0) {
                row.style.borderTop = "2px solid var(--border-color)";
            }

            const groupTd = document.createElement("td");
            groupTd.textContent = fIdx === 0 ? `#${g.group_id}` : "";

            const dbTd = document.createElement("td");
            dbTd.innerHTML = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: rgba(99, 102, 241, 0.2); color: #818cf8;">${escapeHtml(f.db_name)}</span>`;

            const pathTd = document.createElement("td");
            pathTd.className = "path-cell";
            pathTd.textContent = f.path;

            const sizeTd = document.createElement("td");
            sizeTd.textContent = (f.size / 1024).toFixed(1) + " KB";

            const hashTd = document.createElement("td");
            hashTd.style.fontFamily = "monospace";
            hashTd.style.fontSize = "0.8rem";
            hashTd.textContent = f.checksum ? f.checksum.substring(0, 16) + "..." : "N/A";

            row.appendChild(groupTd);
            row.appendChild(dbTd);
            row.appendChild(pathTd);
            row.appendChild(sizeTd);
            row.appendChild(hashTd);

            tbody.appendChild(row);
        });
    });
}
