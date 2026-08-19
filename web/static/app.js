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
let activeTaskId = "";

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
function init() {
    loadDirectories();
    browseFolders();
    loadConfig();
    loadMultiScans();
    setupEventListeners();
    checkInitialResults();
    // Regular status polling (for progress sync)
    setInterval(checkScanStatus, 1000);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}

async function checkInitialResults() {
    try {
        const response = await fetch(`${API_BASE}/api/status?_t=${Date.now()}`);
        const state = await response.json();

        const isCurrentlyScanning = state.scanning || ["discovering", "hashing", "scanning", "running"].includes(state.status);

        if (isCurrentlyScanning) {
            isScanning = true;
            if (progressContainer) progressContainer.classList.remove("hidden");
            if (welcomeContainer) welcomeContainer.classList.add("hidden");
            if (resultsContainer) resultsContainer.classList.add("hidden");
            pollProgress();
        } else {
            hideToast();
        }
    } catch (err) {
        hideToast();
        console.error("Initial results check failed:", err);
    }
}

function setupEventListeners() {
    if (addManualPathBtn) {
        addManualPathBtn.addEventListener("click", () => {
            const path = manualPathInput ? manualPathInput.value.trim() : "";
            if (path) {
                addDirectory(path);
                if (manualPathInput) manualPathInput.value = "";
            }
        });
    }

    if (manualPathInput) {
        manualPathInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && addManualPathBtn) {
                addManualPathBtn.click();
            }
        });
    }

    const clearAllDirsBtn = document.getElementById("clear-all-dirs-btn");
    if (clearAllDirsBtn) {
        clearAllDirsBtn.addEventListener("click", clearAllDirectories);
    }

    if (browserUpBtn) {
        browserUpBtn.addEventListener("click", () => {
            if (currentBrowserPath && currentBrowserPath.includes("/")) {
                const parts = currentBrowserPath.split("/");
                parts.pop();
                const parent = parts.join("/") || "/";
                browseFolders(parent);
            }
        });
    }

    if (startScanBtn) {
        startScanBtn.addEventListener("click", () => {
            const scanModal = document.getElementById("scan-modal");
            if (scanModal) {
                scanModal.classList.remove("hidden");
            }
        });
    }

    const viewCardsBtn = document.getElementById("scans-view-cards-btn");
    const viewTableBtn = document.getElementById("scans-view-table-btn");
    const toggleScansBtn = document.getElementById("toggle-multiscan-btn");
    const searchScansInput = document.getElementById("search-scans-input");
    const scansWrapper = document.getElementById("scans-content-wrapper");

    if (viewCardsBtn && viewTableBtn) {
        viewCardsBtn.addEventListener("click", () => {
            scansViewMode = "cards";
            viewCardsBtn.style.background = "var(--accent)";
            viewCardsBtn.style.color = "#fff";
            viewTableBtn.style.background = "transparent";
            viewTableBtn.style.color = "var(--text-secondary)";
            loadMultiScans();
        });
        viewTableBtn.addEventListener("click", () => {
            scansViewMode = "table";
            viewTableBtn.style.background = "var(--accent)";
            viewTableBtn.style.color = "#fff";
            viewCardsBtn.style.background = "transparent";
            viewCardsBtn.style.color = "var(--text-secondary)";
            loadMultiScans();
        });
    }

    if (toggleScansBtn && scansWrapper) {
        toggleScansBtn.addEventListener("click", () => {
            isScansSectionCollapsed = !isScansSectionCollapsed;
            if (isScansSectionCollapsed) {
                scansWrapper.style.display = "none";
                toggleScansBtn.textContent = "▲ Show DBs";
            } else {
                scansWrapper.style.display = "block";
                toggleScansBtn.textContent = "▼ Hide DBs";
            }
        });
    }

    if (searchScansInput) {
        searchScansInput.addEventListener("input", () => {
            loadMultiScans();
        });
    }

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

    if (deleteMarkedBtn) deleteMarkedBtn.addEventListener("click", deleteMarked);
    if (cancelScanBtn) cancelScanBtn.addEventListener("click", cancelScan);
    if (loadScanBtn) loadScanBtn.addEventListener("click", loadResultsFromFile);
    if (saveResultsBtn) saveResultsBtn.addEventListener("click", saveResultsToFile);
    const toast = document.getElementById("toast");
    if (toast) {
        toast.addEventListener("click", () => {
            toast.classList.add("hidden");
        });
    }

    // Navigation Tabs setup
    const tabScan = document.getElementById("tab-scan");
    const tabResultsStudio = document.getElementById("tab-results-studio");
    const tabCrossDb = document.getElementById("tab-cross-db");
    const tabCache = document.getElementById("tab-cache");

    const scanViewContent = document.getElementById("scan-view-content");
    const resultsStudioContainer = document.getElementById("results-studio-container");
    const crossDbContainer = document.getElementById("cross-db-container");
    const cacheContainer = document.getElementById("cache-container");

    function activateTab(activeTab, activeContainer) {
        [tabScan, tabResultsStudio, tabCrossDb, tabCache].forEach(t => t && t.classList.remove("active"));
        [scanViewContent, resultsStudioContainer, crossDbContainer, cacheContainer].forEach(c => c && c.classList.add("hidden"));
        if (activeTab) activeTab.classList.add("active");
        if (activeContainer) activeContainer.classList.remove("hidden");
    }
    window.activateTab = activateTab;

    if (tabScan) {
        tabScan.addEventListener("click", () => activateTab(tabScan, scanViewContent));
    }
    if (tabResultsStudio) {
        tabResultsStudio.addEventListener("click", () => {
            activateTab(tabResultsStudio, resultsStudioContainer);
            renderResultsStudio();
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

    // Results Studio Event Listeners
    const studioSearch = document.getElementById("studio-search-input");
    if (studioSearch) {
        studioSearch.addEventListener("input", renderResultsStudio);
    }

    const prevGroupBtn = document.getElementById("studio-prev-group-btn");
    const nextGroupBtn = document.getElementById("studio-next-group-btn");
    if (prevGroupBtn) {
        prevGroupBtn.addEventListener("click", () => {
            if (studioCurrentGroupIndex > 0) {
                studioCurrentGroupIndex--;
                renderResultsStudio();
            }
        });
    }
    if (nextGroupBtn) {
        nextGroupBtn.addEventListener("click", () => {
            if (resultsData && studioCurrentGroupIndex < resultsData.length - 1) {
                studioCurrentGroupIndex++;
                renderResultsStudio();
            }
        });
    }

    const compactBtn = document.getElementById("density-compact-btn");
    const standardBtn = document.getElementById("density-standard-btn");
    if (compactBtn && standardBtn) {
        compactBtn.addEventListener("click", () => {
            studioDensity = "compact";
            compactBtn.classList.add("active");
            standardBtn.classList.remove("active");
            renderResultsStudio();
        });
        standardBtn.addEventListener("click", () => {
            studioDensity = "standard";
            standardBtn.classList.add("active");
            compactBtn.classList.remove("active");
            renderResultsStudio();
        });
    }

    const toggleSidebarBtn = document.getElementById("toggle-sidebar-collapse-btn");
    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    const sidebar = document.querySelector(".sidebar");

    function updateSidebarCollapseUI(collapsed) {
        if (!sidebar) return;
        isSidebarCollapsed = collapsed;
        if (isSidebarCollapsed) {
            sidebar.classList.add("collapsed");
            if (toggleSidebarBtn) toggleSidebarBtn.textContent = "🔍 Exit Focus";
            if (sidebarToggleBtn) {
                sidebarToggleBtn.textContent = "▶";
                sidebarToggleBtn.title = "Expand Sidebar";
            }
        } else {
            sidebar.classList.remove("collapsed");
            if (toggleSidebarBtn) toggleSidebarBtn.textContent = "⤢ Focus Workspace";
            if (sidebarToggleBtn) {
                sidebarToggleBtn.textContent = "◀";
                sidebarToggleBtn.title = "Minimize Sidebar";
            }
        }
    }

    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener("click", () => updateSidebarCollapseUI(!isSidebarCollapsed));
    }
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener("click", () => updateSidebarCollapseUI(!isSidebarCollapsed));
    }

    const markAllBtn = document.getElementById("studio-mark-all-dupes-btn");
    const unmarkAllBtn = document.getElementById("studio-unmark-all-btn");
    const invertBtn = document.getElementById("studio-invert-selection-btn");
    const studioDeleteBtn = document.getElementById("studio-delete-marked-btn");

    if (markAllBtn) {
        markAllBtn.addEventListener("click", () => {
            resultsData.forEach(group => {
                group.files.forEach(file => {
                    if (!file.is_ref) file.marked = true;
                });
            });
            renderResultsStudio();
        });
    }
    if (unmarkAllBtn) {
        unmarkAllBtn.addEventListener("click", () => {
            resultsData.forEach(group => {
                group.files.forEach(file => {
                    file.marked = false;
                });
            });
            renderResultsStudio();
        });
    }
    if (invertBtn) {
        invertBtn.addEventListener("click", () => {
            resultsData.forEach(group => {
                group.files.forEach(file => {
                    if (!file.is_ref) file.marked = !file.marked;
                });
            });
            renderResultsStudio();
        });
    }
    if (studioDeleteBtn) {
        studioDeleteBtn.addEventListener("click", deleteMarked);
    }

    // Live DB name preview listener
    const sidebarScanNameInput = document.getElementById("sidebar-scan-name-input");
    const dbPreviewLabel = document.getElementById("db-preview-label");
    if (sidebarScanNameInput && dbPreviewLabel) {
        sidebarScanNameInput.addEventListener("input", () => {
            const val = sidebarScanNameInput.value.trim();
            if (val) {
                dbPreviewLabel.textContent = `Saves scan to isolated file: ${val}.db`;
                dbPreviewLabel.style.color = "var(--accent-color)";
            } else {
                dbPreviewLabel.textContent = "Saves scan to isolated SQLite database file.";
                dbPreviewLabel.style.color = "var(--text-secondary)";
            }
        });
    }

    // New Scan Modal listeners
    const newScanBtn = document.getElementById("new-scan-task-btn");
    const newScanModal = document.getElementById("new-scan-modal");
    const cancelNewScanBtn = document.getElementById("cancel-new-scan-btn");
    const submitNewScanBtn = document.getElementById("submit-new-scan-btn");
    const useSidebarPathsBtn = document.getElementById("use-sidebar-paths-btn");
    const newScanPathInput = document.getElementById("new-scan-path-input");

    if (newScanBtn) {
        newScanBtn.addEventListener("click", () => {
            if (newScanModal) newScanModal.classList.remove("hidden");
            if (newScanPathInput && !newScanPathInput.value.trim()) {
                if (addedPaths && addedPaths.length > 0) {
                    newScanPathInput.value = addedPaths[0];
                } else if (currentBrowserPath) {
                    newScanPathInput.value = currentBrowserPath;
                }
            }
        });
    }
    if (cancelNewScanBtn) {
        cancelNewScanBtn.addEventListener("click", () => {
            if (newScanModal) newScanModal.classList.add("hidden");
        });
    }

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

    const runCrossMatchBtn = document.getElementById("run-cross-match-btn");
    if (runCrossMatchBtn) {
        runCrossMatchBtn.addEventListener("click", runCrossMatch);
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
    const resultsPrevBtnTop = document.getElementById("results-prev-btn-top");
    const resultsNextBtnTop = document.getElementById("results-next-btn-top");

    const goPrevPage = () => {
        if (resultsOffset >= resultsLimit) {
            resultsOffset -= resultsLimit;
            loadResults();
        }
    };

    const goNextPage = () => {
        if (resultsOffset + resultsLimit < resultsTotal) {
            resultsOffset += resultsLimit;
            loadResults();
        }
    };

    if (resultsPrevBtn) resultsPrevBtn.addEventListener("click", goPrevPage);
    if (resultsNextBtn) resultsNextBtn.addEventListener("click", goNextPage);
    if (resultsPrevBtnTop) resultsPrevBtnTop.addEventListener("click", goPrevPage);
    if (resultsNextBtnTop) resultsNextBtnTop.addEventListener("click", goNextPage);

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

async function addDirectory(path, clearExisting = true) {
    try {
        const response = await fetch(`${API_BASE}/api/directories`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path, clear_existing: clearExisting })
        });
        const result = await response.json();
        if (result.success) {
            await loadDirectories();
            await browseFolders(currentBrowserPath);
            showToast("Target directory set successfully!");
        } else {
            alert("Error setting target path: " + (result.error || "Invalid path"));
        }
    } catch (err) {
        console.error("Failed to set target directory:", err);
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

async function clearAllDirectories() {
    if (!confirm("Are you sure you want to remove all target directories from the list?")) return;
    try {
        const response = await fetch(`${API_BASE}/api/directories?clear_all=true`, {
            method: "DELETE",
        });
        const result = await response.json();
        if (result.success) {
            await loadDirectories();
            await browseFolders(currentBrowserPath);
            showToast("All target directories removed.");
        } else {
            showToast(`Failed to clear directories: ${result.error}`);
        }
    } catch (err) {
        showToast(`Failed to clear directories: ${err.message}`);
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
            folderList.innerHTML = `<li style="color: var(--text-secondary); text-align: center; padding: 12px; font-size: 0.85rem;">⚠️ Cannot access folder</li>`;
            return;
        }

        currentBrowserPath = data.current;
        currentDirSpan.textContent = currentBrowserPath;
        currentDirSpan.title = currentBrowserPath;

        folderList.innerHTML = "";
        if (!data.folders || data.folders.length === 0) {
            folderList.innerHTML = `<li style="color: var(--text-secondary); text-align: center; padding: 12px; font-size: 0.85rem;">No subfolders found</li>`;
            return;
        }

        data.folders.forEach(f => {
            const isAdded = addedPaths.includes(f.path);
            const li = document.createElement("li");

            let actionHtml = "";
            if (isAdded) {
                actionHtml = `<span class="folder-status added">✓ Added</span>`;
            } else {
                actionHtml = `
                    <div style="display: flex; gap: 4px; align-items: center;">
                        <span class="folder-select" onclick="addDirectory('${escapeJS(f.path)}', true)" title="Set as main target directory">Add</span>
                        <span class="folder-select" onclick="addDirectory('${escapeJS(f.path)}', false)" title="Append to target directories list" style="padding: 2px 6px; font-weight: bold;">+</span>
                    </div>
                `;
            }

            li.innerHTML = `
                <span class="folder-name" onclick="browseFolders('${escapeJS(f.path)}')">📁 ${f.name}</span>
                ${actionHtml}
            `;
            folderList.appendChild(li);
        });
    } catch (err) {
        console.error("Browse folders failed:", err);
        if (folderList) {
            folderList.innerHTML = `<li style="color: var(--text-secondary); text-align: center; padding: 12px; font-size: 0.85rem;">Failed to load folders</li>`;
        }
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
        const isCurrentlyScanning = state.scanning || ["discovering", "hashing", "scanning", "running"].includes(state.status);
        if (isCurrentlyScanning) {
            isScanning = true;
            if (progressContainer) progressContainer.classList.remove("hidden");
            if (welcomeContainer) welcomeContainer.classList.add("hidden");
            if (resultsContainer) resultsContainer.classList.add("hidden");
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

        const isCurrentlyScanning = state.scanning || ["discovering", "hashing", "scanning", "running"].includes(state.status);

        if (isCurrentlyScanning) {
            if (progressContainer) progressContainer.classList.remove("hidden");
            if (welcomeContainer) welcomeContainer.classList.add("hidden");
            if (resultsContainer) resultsContainer.classList.add("hidden");

            progressBarFill.style.width = `${state.progress || 0}%`;
            progressPercent.textContent = `${state.progress || 0}%`;
            if (isStopping) {
                progressDesc.textContent = "Stopping scan, writing database checkpoints...";
            } else {
                progressDesc.textContent = state.progress_msg || "Processing scan task...";
            }

            const targetsDiv = document.getElementById("progress-targets");
            if (targetsDiv && state.targets && state.targets.length > 0) {
                targetsDiv.innerHTML = `<strong>Scanning Target(s):</strong><br><span style="opacity: 0.85;">${state.targets.join("<br>")}</span>`;
            } else if (targetsDiv) {
                targetsDiv.innerHTML = "";
            }

            loadMultiScans();
            setTimeout(pollProgress, 500);
        } else {
            isScanning = false;
            isStopping = false;
            cancelScanBtn.disabled = false;
            progressContainer.classList.add("hidden");
            hideToast();
            loadMultiScans();
            if (state.status === "completed") {
                showToast("Scan completed! Rendering duplicate results...", true);
                await loadResults();
                hideToast();
                if (resultsContainer) {
                    resultsContainer.classList.remove("hidden");
                }
                if (welcomeContainer) welcomeContainer.classList.add("hidden");
            } else {
                welcomeContainer.classList.remove("hidden");
                resultsContainer.classList.add("hidden");

                if (cancelStats) {
                    let msg = "Scan was stopped. Progress saved to database.";
                    showToast(msg, true);
                    cancelStats = null;
                } else {
                    showToast("Scan reached idle or stopped state.");
                }
            }
        }
    } catch (err) {
        console.error("Poll progress failed:", err);
        showToast("Connection to server lost. Polling stopped.");
    }
}

// 4. Results Management
async function loadResults() {
    try {
        const url = activeTaskId
            ? `${API_BASE}/api/results?task_id=${encodeURIComponent(activeTaskId)}&limit=${resultsLimit}&offset=${resultsOffset}&_t=${Date.now()}`
            : `${API_BASE}/api/results?limit=${resultsLimit}&offset=${resultsOffset}&_t=${Date.now()}`;
        const response = await fetch(url);
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
    if (welcomeContainer) welcomeContainer.classList.add("hidden");
    if (resultsContainer) resultsContainer.classList.remove("hidden");

    // Force layout reflow so scrollbars render immediately without page refresh
    const wrapper = document.querySelector(".table-wrapper");
    if (wrapper) {
        wrapper.scrollTop = 0;
        wrapper.style.display = "none";
        wrapper.offsetHeight; // Trigger DOM layout repaint
        wrapper.style.display = "";
    }

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
        const groupNum = group.id !== undefined ? group.id + 1 : "";
        const headerRow = document.createElement("tr");
        headerRow.className = "group-header-row";
        headerRow.innerHTML = `
            <td colspan="6" style="font-weight: 600;">Duplicate Group ${groupNum} of ${resultsTotal} (Max Match: ${group.percentage}%)</td>
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
    const resultsPrevBtnTop = document.getElementById("results-prev-btn-top");
    const resultsNextBtnTop = document.getElementById("results-next-btn-top");
    const resultsPageInfoTop = document.getElementById("results-page-info-top");

    const currentPage = Math.floor(resultsOffset / resultsLimit) + 1;
    const totalPages = Math.max(1, Math.ceil(resultsTotal / resultsLimit));
    const isFirstPage = resultsOffset === 0;
    const isLastPage = resultsOffset + resultsLimit >= resultsTotal;

    if (resultsPageInfo) resultsPageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    if (resultsPageInfoTop) resultsPageInfoTop.textContent = `Page ${currentPage} of ${totalPages}`;
    if (resultsPrevBtn) resultsPrevBtn.disabled = isFirstPage;
    if (resultsNextBtn) resultsNextBtn.disabled = isLastPage;
    if (resultsPrevBtnTop) resultsPrevBtnTop.disabled = isFirstPage;
    if (resultsNextBtnTop) resultsNextBtnTop.disabled = isLastPage;

    const overallMarked = totalMarkedCount !== undefined ? totalMarkedCount : 0;
    resultsSummary.textContent = `Found ${totalGroups} duplicate groups. Showing page ${currentPage} of ${totalPages}. ${overallMarked} files marked for deletion.`;
    deleteMarkedBtn.disabled = overallMarked === 0;
    deleteMarkedBtn.textContent = `Delete ${overallMarked} Marked File(s)`;

    renderResultsStudio();
}

// Results Studio State & Renderer
let studioCurrentGroupIndex = 0;
let studioDensity = "compact";
let isSidebarCollapsed = false;

function renderResultsStudio() {
    const studioBadge = document.getElementById("studio-summary-badge");
    const studioBody = document.getElementById("studio-results-body");
    const studioCounter = document.getElementById("studio-group-counter");
    const studioSearch = document.getElementById("studio-search-input");
    const studioMarkedStats = document.getElementById("studio-marked-stats");
    const studioDeleteBtn = document.getElementById("studio-delete-marked-btn");

    if (!studioBody) return;

    const filterQuery = studioSearch ? studioSearch.value.trim().toLowerCase() : "";
    const filteredGroups = (resultsData || []).filter(group => {
        if (!filterQuery) return true;
        return group.files.some(f =>
            (f.name && f.name.toLowerCase().includes(filterQuery)) ||
            (f.folder && f.folder.toLowerCase().includes(filterQuery)) ||
            (f.path && f.path.toLowerCase().includes(filterQuery))
        );
    });

    if (studioBadge) studioBadge.textContent = `${filteredGroups.length} Duplicate Groups`;
    if (studioCounter) {
        if (filteredGroups.length === 0) {
            studioCounter.textContent = "Group 0 of 0";
        } else {
            studioCounter.textContent = `Group ${studioCurrentGroupIndex + 1} of ${filteredGroups.length}`;
        }
    }

    studioBody.innerHTML = "";

    if (!filteredGroups || filteredGroups.length === 0) {
        studioBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 48px; color: var(--text-secondary);">No duplicate results found. Launch a scan or select a scan database to view duplicates.</td></tr>`;
        if (studioMarkedStats) studioMarkedStats.textContent = "0 files marked for deletion (0 B)";
        if (studioDeleteBtn) studioDeleteBtn.disabled = true;
        return;
    }

    let markedCount = 0;
    let markedBytes = 0;

    filteredGroups.forEach((group, gIdx) => {
        const groupHeader = document.createElement("tr");
        groupHeader.className = "studio-group-header";
        const groupNum = group.id !== undefined ? group.id + 1 : gIdx + 1;
        groupHeader.innerHTML = `
            <td colspan="7">
                📁 Duplicate Group #${groupNum} &nbsp;•&nbsp; ${group.files.length} Files &nbsp;•&nbsp; Match Score: ${group.percentage}%
            </td>
        `;
        studioBody.appendChild(groupHeader);

        group.files.forEach(file => {
            if (file.marked && !file.is_ref) {
                markedCount++;
                markedBytes += (file.size_bytes || 0);
            }

            const row = document.createElement("tr");
            if (studioDensity === "compact") row.classList.add("compact-row");

            const checkboxHtml = file.is_ref
                ? `<span style="font-size: 0.72rem; padding: 2px 6px; background: rgba(85, 239, 196, 0.15); color: var(--success); border-radius: 4px; font-weight: 600;">PIVOT</span>`
                : `
                    <label class="checkbox-container">
                        <input type="checkbox" ${file.marked ? "checked" : ""} onchange="toggleMark('${escapeJS(file.path)}', this.checked)">
                        <span class="checkmark"></span>
                    </label>
                `;

            const ext = file.name ? file.name.split('.').pop().toUpperCase() : "FILE";

            row.innerHTML = `
                <td style="text-align: center;">${checkboxHtml}</td>
                <td style="text-align: center; color: var(--accent); font-weight: 600;">${file.is_ref ? "-" : file.percentage + "%"}</td>
                <td style="text-align: center;"><span style="font-size: 0.72rem; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">${ext}</span></td>
                <td class="expandable-cell" style="font-weight: 500;" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</td>
                <td class="expandable-cell" style="font-size: 0.8rem; font-family: monospace; color: var(--text-secondary);" title="${escapeHtml(file.folder)}">${escapeHtml(file.folder)}</td>
                <td style="text-align: right; font-weight: 500;">${file.size}</td>
                <td style="color: var(--text-secondary); font-size: 0.8rem;">${file.mtime}</td>
            `;
            studioBody.appendChild(row);
        });
    });

    const formatBytesStr = (bytes) => {
        if (!bytes) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB", "TB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    if (studioMarkedStats) {
        studioMarkedStats.textContent = `${markedCount} file(s) marked for deletion (${formatBytesStr(markedBytes)})`;
    }
    if (studioDeleteBtn) {
        studioDeleteBtn.disabled = markedCount === 0;
        studioDeleteBtn.textContent = `🗑️ Delete ${markedCount} Marked File(s)`;
    }
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
    const markedPaths = [];
    (resultsData || []).forEach(group => {
        group.files.forEach(file => {
            if (file.marked && !file.is_ref) {
                markedPaths.push(file.path);
            }
        });
    });

    const targetCount = totalMarkedFilesCount || markedPaths.length;

    if (targetCount === 0 && markedPaths.length === 0) {
        showToast("No marked files selected for deletion.");
        return;
    }

    const displayCount = targetCount > 0 ? targetCount : markedPaths.length;

    if (!confirm(`Are you sure you want to permanently delete all ${displayCount} marked duplicate file(s)? This cannot be undone.`)) {
        return;
    }

    try {
        showToast(`Deleting ${displayCount} marked duplicate file(s)... Please wait.`, true);
        const response = await fetch(`${API_BASE}/api/results/delete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                task_id: activeTaskId,
                delete_all_marked: true,
                paths: markedPaths,
            }),
        });
        const result = await response.json();
        if (result.success) {
            showToast(`Successfully deleted ${result.deleted_count || displayCount} duplicate file(s).`);
            await loadResults();
            await loadMultiScans();
        } else {
            showToast(`Error deleting files: ${result.error}`);
        }
    } catch (err) {
        console.error("Delete marked failed:", err);
        showToast(`Error deleting files: ${err.message}`);
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
    if (!str) return "";
    return String(str).replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/"/g, '\\"');
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

async function loadResultsFromFile() {
    const path = prompt("Enter the absolute file path to a saved .dedupresults file to load:");
    if (!path) return;
    try {
        const response = await fetch(`${API_BASE}/api/results/load`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: path }),
        });
        const res = await response.json();
        if (res.success) {
            showToast("Results loaded successfully!");
            await loadResults();
        } else {
            showToast(`Failed to load results: ${res.error}`);
        }
    } catch (err) {
        showToast(`Error loading results: ${err.message}`);
    }
}

async function saveResultsToFile() {
    const path = prompt("Enter the absolute file path where you want to save the results (e.g. /path/to/results.dedupresults):");
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

    const duration = persistent ? 8000 : 3500;
    toast.timeoutId = setTimeout(() => {
        toast.classList.add("hidden");
        toast.timeoutId = null;
    }, duration);
}

function hideToast() {
    const toast = document.getElementById("toast");
    if (!toast) return;
    if (toast.timeoutId) {
        clearTimeout(toast.timeoutId);
        toast.timeoutId = null;
    }
    toast.classList.add("hidden");
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

// Multi-DB View Mode & Collapse State
let scansViewMode = "cards";
let isScansSectionCollapsed = false;

// 7. Multi-DB Dashboard Management
async function loadMultiScans() {
    const scansGrid = document.getElementById("scans-grid");
    const scansTableContainer = document.getElementById("scans-table-container");
    const scansTableBody = document.getElementById("scans-table-body");
    const countBadge = document.getElementById("scans-count-badge");
    const searchInput = document.getElementById("search-scans-input");

    if (!scansGrid) return;

    try {
        const response = await fetch(`${API_BASE}/api/scans?_t=${Date.now()}`);
        const tasks = await response.json();

        if (countBadge) countBadge.textContent = tasks ? tasks.length : 0;

        const filterQuery = searchInput ? searchInput.value.trim().toLowerCase() : "";
        const filteredTasks = (tasks || []).filter(t => {
            if (!filterQuery) return true;
            return (
                (t.name && t.name.toLowerCase().includes(filterQuery)) ||
                (t.db_path && t.db_path.toLowerCase().includes(filterQuery)) ||
                (t.directories && t.directories.some(d => d.toLowerCase().includes(filterQuery)))
            );
        });

        if (scansViewMode === "cards") {
            scansGrid.classList.remove("hidden");
            if (scansTableContainer) scansTableContainer.classList.add("hidden");
            scansGrid.innerHTML = "";

            if (!filteredTasks || filteredTasks.length === 0) {
                scansGrid.innerHTML = `<div style="grid-column: 1 / -1; color: var(--text-secondary); font-size: 0.9rem; padding: 12px 0;">${filterQuery ? "No matching scan databases found." : "No scan databases created yet."} Add directories in the sidebar and click <strong>Start Duplicate Scan</strong>.</div>`;
                return;
            }

            filteredTasks.forEach(task => {
                const card = document.createElement("div");
                card.className = "section-card";
                card.style.position = "relative";
                card.style.display = "flex";
                card.style.flexDirection = "column";
                card.style.gap = "10px";
                card.style.overflow = "hidden";

                let statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(99, 102, 241, 0.2); color: #818cf8;">${task.status}</span>`;
                if (task.status === "completed") {
                    statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(16, 185, 129, 0.2); color: #34d399;">COMPLETED</span>`;
                } else if (task.status === "needs_hashing") {
                    statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(245, 158, 11, 0.2); color: #fbbf24;">UNHASHED (${task.hashed_count || 0}/${task.file_count || 0})</span>`;
                } else if (task.status === "failed") {
                    statusBadge = `<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: rgba(239, 68, 68, 0.2); color: #f87171;">FAILED</span>`;
                }

                const sizeMb = (task.db_size_bytes / (1024 * 1024)).toFixed(2);
                const foldersHtml = task.directories && task.directories.length
                    ? task.directories.map(d => `<div style="padding: 2px 0; border-bottom: 1px dashed rgba(255,255,255,0.05);">${escapeHtml(d)}</div>`).join("")
                    : `<em>Target: ${escapeHtml(task.name)}</em>`;

                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">${escapeHtml(task.name)}</h3>
                        ${statusBadge}
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-secondary); word-break: break-all; font-family: monospace; background: rgba(0,0,0,0.15); padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-color);">
                        <strong style="color: var(--text-primary);">DB:</strong> ${escapeHtml(task.db_path)} <span style="color: var(--accent); margin-left: 4px;">(${sizeMb} MB)</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-primary);">Folders:</span>
                        <div style="max-height: 70px; overflow-y: auto; font-size: 0.78rem; font-family: monospace; color: var(--text-secondary); background: rgba(0,0,0,0.2); padding: 6px 10px; border-radius: 6px; word-break: break-all; border: 1px solid rgba(255,255,255,0.05);">
                            ${foldersHtml}
                        </div>
                    </div>
                    <div style="display: flex; gap: 12px; font-size: 0.78rem; color: var(--text-secondary); margin-top: auto; padding-top: 4px; flex-wrap: wrap;">
                        <span><strong style="color: var(--text-primary);">Total Files:</strong> ${task.file_count || 0}</span>
                        <span><strong style="color: var(--text-primary);">Hashed:</strong> ${task.hashed_count !== undefined ? task.hashed_count : task.file_count || 0}</span>
                        <span><strong style="color: var(--text-primary);">Matches:</strong> ${task.match_count || 0}</span>
                    </div>
                    <div style="margin-top: 6px; display: flex; gap: 8px; justify-content: flex-end; padding-top: 8px; border-top: 1px solid var(--border-color);">
                        <button class="btn secondary-btn text-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="viewTaskResults('${task.task_id}', this)">View Results</button>
                        <button class="btn secondary-btn text-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="rescanTaskDatabase('${task.task_id}', this)">Refresh Scan</button>
                        <button class="btn danger-btn text-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="deleteScanTask('${task.task_id}')">Delete DB</button>
                    </div>
                `;

                scansGrid.appendChild(card);
            });
        } else {
            // Table View Mode
            scansGrid.classList.add("hidden");
            if (scansTableContainer) scansTableContainer.classList.remove("hidden");
            if (scansTableBody) {
                scansTableBody.innerHTML = "";

                if (!filteredTasks || filteredTasks.length === 0) {
                    scansTableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 20px; color: var(--text-secondary);">${filterQuery ? "No matching scan databases found." : "No scan databases created yet."}</td></tr>`;
                    return;
                }

                filteredTasks.forEach(task => {
                    const row = document.createElement("tr");
                    row.style.borderBottom = "1px solid var(--border-color)";

                    let statusBadge = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: rgba(99, 102, 241, 0.2); color: #818cf8;">${task.status}</span>`;
                    if (task.status === "completed") {
                        statusBadge = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: rgba(16, 185, 129, 0.2); color: #34d399;">COMPLETED</span>`;
                    } else if (task.status === "needs_hashing") {
                        statusBadge = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: rgba(245, 158, 11, 0.2); color: #fbbf24;">UNHASHED</span>`;
                    } else if (task.status === "failed") {
                        statusBadge = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: rgba(239, 68, 68, 0.2); color: #f87171;">FAILED</span>`;
                    }

                    const folderText = (task.directories || []).join(", ") || "None";
                    const sizeMb = (task.db_size_bytes / (1024 * 1024)).toFixed(1);

                    row.innerHTML = `
                        <td style="padding: 8px 12px; font-weight: 600; color: var(--text-primary);">${escapeHtml(task.name)}</td>
                        <td style="padding: 8px 12px;">${statusBadge}</td>
                        <td style="padding: 8px 12px; text-align: right; font-family: monospace;">${task.file_count || 0}</td>
                        <td style="padding: 8px 12px; text-align: right; font-family: monospace;">${task.hashed_count !== undefined ? task.hashed_count : task.file_count || 0}</td>
                        <td style="padding: 8px 12px; text-align: right; font-family: monospace; color: var(--accent); font-weight: 600;">${task.match_count || 0}</td>
                        <td style="padding: 8px 12px; text-align: right; font-family: monospace;">${sizeMb} MB</td>
                        <td style="padding: 8px 12px; font-family: monospace; font-size: 0.78rem; color: var(--text-secondary); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(folderText)}">${escapeHtml(folderText)}</td>
                        <td style="padding: 8px 12px; text-align: right;">
                            <button class="btn secondary-btn text-btn" style="font-size: 0.75rem; padding: 3px 8px;" onclick="viewTaskResults('${task.task_id}', this)">View Results</button>
                            <button class="btn secondary-btn text-btn" style="font-size: 0.75rem; padding: 3px 8px; margin-left: 4px;" onclick="rescanTaskDatabase('${task.task_id}', this)">Refresh Scan</button>
                            <button class="btn danger-btn text-btn" style="font-size: 0.75rem; padding: 3px 8px; margin-left: 4px;" onclick="deleteScanTask('${task.task_id}')">Delete</button>
                        </td>
                    `;
                    scansTableBody.appendChild(row);
                });
            }
        }
    } catch (err) {
        console.error("Failed to load multi-scans:", err);
    }
}

async function rescanTaskDatabase(taskId, btn) {
    let originalHtml = "";
    if (btn) {
        originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = "🔄 Refreshing...";
    }
    try {
        showToast("Initiating Refresh Scan across target directories...", true);
        const response = await fetch(`${API_BASE}/api/scans/rescan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });
        const res = await response.json();
        if (res.success) {
            isScanning = true;
            if (progressContainer) progressContainer.classList.remove("hidden");
            if (welcomeContainer) welcomeContainer.classList.add("hidden");
            if (resultsContainer) resultsContainer.classList.add("hidden");
            showToast(`Re-scanning directory paths for '${res.task.name}'... Please wait.`, true);
            pollProgress();
        } else {
            showToast(`Error refreshing scan: ${res.error}`);
        }
    } catch (err) {
        showToast(`Failed to refresh scan: ${err.message}`);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    }
}

async function viewTaskResults(taskId, btn) {
    activeTaskId = taskId;
    let originalHtml = "";
    if (btn) {
        originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = "⏳ Loading...";
    }
    try {
        showToast("Loading scan results from database...", true);
        const response = await fetch(`${API_BASE}/api/scans/load`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });
        const res = await response.json();
        if (res.success) {
            if (res.is_scanning) {
                isScanning = true;
                if (progressContainer) progressContainer.classList.remove("hidden");
                if (welcomeContainer) welcomeContainer.classList.add("hidden");
                if (resultsContainer) resultsContainer.classList.add("hidden");
                showToast(`Hashing & scanning candidate files for '${res.task.name}'... Please wait.`, true);
                pollProgress();
            } else {
                showToast("Rendering duplicate matches...", true);
                await loadResults();
                await loadMultiScans();
                hideToast();
                if (resultsContainer) {
                    resultsContainer.classList.remove("hidden");
                }
                if (welcomeContainer) welcomeContainer.classList.add("hidden");
                if (progressContainer) progressContainer.classList.add("hidden");
            }
        } else {
            showToast(`Error loading scan: ${res.error}`);
        }
    } catch (err) {
        showToast(`Failed to load scan: ${err.message}`);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    }
}

async function launchNewDBScan(overwrite = false) {
    const nameInput = document.getElementById("new-scan-name-input");
    const pathInput = document.getElementById("new-scan-path-input");
    const modal = document.getElementById("new-scan-modal");

    const name = nameInput.value.trim() || "Scan";
    const path = pathInput.value.trim();

    if (!path) {
        pathInput.style.borderColor = "#ef4444";
        pathInput.focus();
        showToast("⚠️ Target directory path is required. Please select or enter a folder path.");
        return;
    }
    pathInput.style.borderColor = "";

    try {
        const response = await fetch(`${API_BASE}/api/scans/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, directories: [path], overwrite: overwrite }),
        });
        const result = await response.json();

        if (result.exists && !overwrite) {
            const doOverwrite = confirm(
                `A database scan named '${name}' already exists.\n\n` +
                `Click OK to re-run the scan (overwriting existing data), or Cancel to choose a different name.`
            );
            if (doOverwrite) {
                launchNewDBScan(true);
            }
            return;
        }

        if (result.success) {
            showToast(`Launched isolated scan: ${name}`);
            if (modal) modal.classList.add("hidden");
            nameInput.value = "";
            pathInput.value = "";
            isScanning = true;
            if (progressContainer) progressContainer.classList.remove("hidden");
            if (welcomeContainer) welcomeContainer.classList.add("hidden");
            if (resultsContainer) resultsContainer.classList.add("hidden");
            pollProgress();
            await loadDirectories();
            loadMultiScans();
        } else {
            showToast(`Error: ${result.error || "Failed to launch scan"}`);
        }
    } catch (err) {
        showToast(`Error: ${err.message}`);
    }
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

let crossDbResultsData = [];
let crossDbSelectedDBs = [];

function toggleCrossMark(groupIndex, fileIndex, isChecked) {
    if (crossDbResultsData[groupIndex] && crossDbResultsData[groupIndex].files[fileIndex]) {
        crossDbResultsData[groupIndex].files[fileIndex].marked = isChecked;
        updateCrossStats();
    }
}

function updateCrossStats() {
    let markedCount = 0;
    let markedBytes = 0;
    (crossDbResultsData || []).forEach(g => {
        g.files.forEach(f => {
            if (f.marked) {
                markedCount++;
                markedBytes += (f.size || 0);
            }
        });
    });

    const formatBytesStr = (bytes) => {
        if (!bytes) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB", "TB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    const statsEl = document.getElementById("cross-marked-stats");
    const deleteBtn = document.getElementById("cross-delete-marked-btn");

    if (statsEl) statsEl.textContent = `${markedCount} file(s) marked for deletion (${formatBytesStr(markedBytes)})`;
    if (deleteBtn) {
        deleteBtn.disabled = markedCount === 0;
        deleteBtn.textContent = `🗑️ Delete ${markedCount} Marked File(s) Across Databases`;
    }
}

async function runCrossMatch() {
    const checked = Array.from(document.querySelectorAll(".cross-db-checkbox:checked")).map(c => c.value);
    crossDbSelectedDBs = checked;
    const resultsWrapper = document.getElementById("cross-results-wrapper");
    const resultsSummary = document.getElementById("cross-results-summary");

    if (checked.length < 2) {
        showToast("Please select at least 2 database files to compare.");
        return;
    }

    try {
        showToast("Comparing hashes across selected databases...");
        const response = await fetch(`${API_BASE}/api/cross_scan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ db_paths: checked }),
        });
        const result = await response.json();

        if (result.success) {
            if (resultsWrapper) resultsWrapper.classList.remove("hidden");
            if (result.total_groups > 0) {
                if (resultsSummary) {
                    resultsSummary.textContent = `Completed cross-DB comparison: Found ${result.total_groups} duplicate groups matching across ${checked.length} databases.`;
                }
                showToast(`Found ${result.total_groups} cross-database duplicate groups.`);
            } else {
                if (resultsSummary) {
                    resultsSummary.textContent = `Completed cross-DB comparison across ${checked.length} databases: No matching duplicate files found.`;
                }
                showToast("Comparison complete: No cross-database duplicates found.");
            }
            renderCrossResultsTable(result.groups);
        } else {
            showToast(`Error: ${result.error}`);
        }
    } catch (err) {
        showToast(`Cross match error: ${err.message}`);
    }
}

function renderCrossResultsTable(groups) {
    crossDbResultsData = groups || [];
    const tbody = document.getElementById("cross-results-body");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!crossDbResultsData || crossDbResultsData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 32px; color: var(--text-secondary);">No cross-database duplicate matches found.</td></tr>`;
        updateCrossStats();
        return;
    }

    crossDbResultsData.forEach((g, gIdx) => {
        g.files.forEach((f, fIdx) => {
            if (f.marked === undefined) {
                f.marked = fIdx > 0;
            }

            const row = document.createElement("tr");
            if (fIdx === 0) {
                row.style.borderTop = "2px solid var(--border-color)";
            }

            const checkTd = document.createElement("td");
            checkTd.style.textAlign = "center";
            checkTd.innerHTML = fIdx === 0
                ? `<span style="font-size: 0.72rem; padding: 2px 6px; background: rgba(85, 239, 196, 0.15); color: var(--success); border-radius: 4px; font-weight: 600;">PIVOT</span>`
                : `<label class="checkbox-container">
                        <input type="checkbox" class="cross-dupe-file-checkbox" ${f.marked ? "checked" : ""} onchange="toggleCrossMark(${gIdx}, ${fIdx}, this.checked)">
                        <span class="checkmark"></span>
                   </label>`;

            const groupTd = document.createElement("td");
            groupTd.textContent = fIdx === 0 ? `#${g.group_id}` : "";

            const dbTd = document.createElement("td");
            dbTd.innerHTML = `<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: rgba(99, 102, 241, 0.2); color: #818cf8;">${escapeHtml(f.db_name)}</span>`;

            const pathTd = document.createElement("td");
            pathTd.className = "expandable-cell";
            pathTd.title = escapeHtml(f.path);
            pathTd.textContent = f.path;

            const sizeTd = document.createElement("td");
            sizeTd.textContent = (f.size / 1024).toFixed(1) + " KB";

            const hashTd = document.createElement("td");
            hashTd.style.fontFamily = "monospace";
            hashTd.style.fontSize = "0.8rem";
            hashTd.textContent = f.checksum ? f.checksum.substring(0, 16) + "..." : "N/A";

            row.appendChild(checkTd);
            row.appendChild(groupTd);
            row.appendChild(dbTd);
            row.appendChild(pathTd);
            row.appendChild(sizeTd);
            row.appendChild(hashTd);

            tbody.appendChild(row);
        });
    });

    updateCrossStats();
}

async function deleteCrossMarked() {
    const markedPaths = [];
    (crossDbResultsData || []).forEach(g => {
        g.files.forEach(f => {
            if (f.marked) {
                markedPaths.push(f.path);
            }
        });
    });

    if (markedPaths.length === 0) {
        showToast("No files selected for deletion.");
        return;
    }

    if (!confirm(`Are you sure you want to permanently delete ${markedPaths.length} marked duplicate file(s) across selected databases? This cannot be undone.`)) {
        return;
    }

    try {
        showToast(`Deleting ${markedPaths.length} cross-database duplicate file(s)...`);
        const response = await fetch(`${API_BASE}/api/results/delete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                db_paths: crossDbSelectedDBs,
                paths: markedPaths,
            }),
        });
        const result = await response.json();
        if (result.success) {
            showToast(`Successfully deleted ${result.deleted_count || markedPaths.length} duplicate file(s) across databases.`);
            crossDbResultsData.forEach(g => {
                g.files = g.files.filter(f => !markedPaths.includes(f.path));
            });
            crossDbResultsData = crossDbResultsData.filter(g => g.files.length > 1);
            renderCrossResultsTable(crossDbResultsData);
            loadMultiScans();
        } else {
            showToast(`Error deleting files: ${result.error}`);
        }
    } catch (err) {
        console.error("Cross delete failed:", err);
        showToast(`Error deleting files: ${err.message}`);
    }
}

function transferCrossToStudio() {
    if (!crossDbResultsData || crossDbResultsData.length === 0) {
        showToast("No cross-database results available to open in Results Studio.");
        return;
    }

    resultsData = crossDbResultsData.map((g, idx) => {
        const pivotFile = g.files[0] || {};
        const dupeFiles = g.files.slice(1);
        const pivotDTO = {
            path: pivotFile.path,
            name: pivotFile.path.split("/").pop(),
            folder: pivotFile.path.substring(0, pivotFile.path.lastIndexOf("/")),
            size: (pivotFile.size / 1024).toFixed(1) + " KB",
            size_bytes: pivotFile.size,
            mtime: "N/A",
            percentage: 100,
            is_ref: true,
            marked: false,
        };
        const dupeDTOs = dupeFiles.map(df => ({
            path: df.path,
            name: df.path.split("/").pop(),
            folder: df.path.substring(0, df.path.lastIndexOf("/")),
            size: (df.size / 1024).toFixed(1) + " KB",
            size_bytes: df.size,
            mtime: "N/A",
            percentage: 100,
            is_ref: false,
            marked: df.marked !== undefined ? df.marked : true,
        }));
        return {
            id: idx,
            percentage: 100,
            files: [pivotDTO, ...dupeDTOs],
        };
    });

    const tabResultsStudio = document.getElementById("tab-results-studio");
    const resultsStudioContainer = document.getElementById("results-studio-container");
    if (typeof window.activateTab === "function") {
        window.activateTab(tabResultsStudio, resultsStudioContainer);
    } else {
        [document.getElementById("tab-scan"), tabResultsStudio, document.getElementById("tab-cross-db"), document.getElementById("tab-cache")].forEach(t => t && t.classList.remove("active"));
        [document.getElementById("scan-view-content"), resultsStudioContainer, document.getElementById("cross-db-container"), document.getElementById("cache-container")].forEach(c => c && c.classList.add("hidden"));
        if (tabResultsStudio) tabResultsStudio.classList.add("active");
        if (resultsStudioContainer) resultsStudioContainer.classList.remove("hidden");
    }
    renderResultsStudio();
    showToast("Transferred cross-database duplicate groups into Results Studio.");
}

const crossMarkAllBtn = document.getElementById("cross-mark-all-btn");
const crossUnmarkAllBtn = document.getElementById("cross-unmark-all-btn");
const crossTransferBtn = document.getElementById("cross-transfer-studio-btn");
const crossDeleteBtn = document.getElementById("cross-delete-marked-btn");

if (crossMarkAllBtn) {
    crossMarkAllBtn.addEventListener("click", () => {
        (crossDbResultsData || []).forEach(g => {
            g.files.forEach((f, idx) => {
                if (idx > 0) f.marked = true;
            });
        });
        renderCrossResultsTable(crossDbResultsData);
    });
}
if (crossUnmarkAllBtn) {
    crossUnmarkAllBtn.addEventListener("click", () => {
        (crossDbResultsData || []).forEach(g => {
            g.files.forEach(f => {
                f.marked = false;
            });
        });
        renderCrossResultsTable(crossDbResultsData);
    });
}
if (crossTransferBtn) {
    crossTransferBtn.addEventListener("click", transferCrossToStudio);
}
if (crossDeleteBtn) {
    crossDeleteBtn.addEventListener("click", deleteCrossMarked);
}
