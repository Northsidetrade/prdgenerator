/**
 * PRD History handler for PRD Generator
 * Following Semantic Seed Coding Standards for JavaScript implementation
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const prdListElement = document.getElementById('prd-list');
    const loadingIndicator = document.getElementById('loading-indicator');
    const noPrdsMessage = document.getElementById('no-prds-message');
    const loadingError = document.getElementById('loading-error');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const templateFilter = document.getElementById('template-filter');
    const sortOrder = document.getElementById('sort-order');
    const paginationContainer = document.getElementById('pagination-container');
    const pagination = document.getElementById('pagination');
    
    // Modal elements
    const viewPrdModal = document.getElementById('viewPrdModal');
    const modalTitle = document.getElementById('viewPrdModalLabel');
    const modalContent = document.getElementById('modal-prd-content');
    const modalCopyButton = document.getElementById('modal-copy-button');
    const modalDownloadButton = document.getElementById('modal-download-button');
    
    // State
    let currentPage = 1;
    const itemsPerPage = 10;
    let totalItems = 0;
    let currentPRDs = [];
    let filterSettings = {
        search: '',
        template: '',
        sort: 'newest'
    };
    
    // Initialize
    init();
    
    /**
     * Initialize the page
     */
    async function init() {
        // Add event listeners
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                filterSettings.search = searchInput.value.trim();
                currentPage = 1;
                loadPRDs();
            });
        }
        
        if (searchInput) {
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    filterSettings.search = searchInput.value.trim();
                    currentPage = 1;
                    loadPRDs();
                }
            });
        }
        
        if (templateFilter) {
            templateFilter.addEventListener('change', () => {
                filterSettings.template = templateFilter.value;
                currentPage = 1;
                loadPRDs();
            });
        }
        
        if (sortOrder) {
            sortOrder.addEventListener('change', () => {
                filterSettings.sort = sortOrder.value;
                currentPage = 1;
                loadPRDs();
            });
        }
        
        if (modalCopyButton) {
            modalCopyButton.addEventListener('click', copyModalContent);
        }
        
        if (modalDownloadButton) {
            modalDownloadButton.addEventListener('click', downloadModalContent);
        }
        
        // Load PRDs
        loadPRDs();
    }
    
    /**
     * Load PRDs from the API
     */
    async function loadPRDs() {
        try {
            showLoading();
            
            // Get auth headers
            const headers = window.AuthModule.getAuthHeaders();
            
            // Build query parameters
            const params = new URLSearchParams();
            params.append('skip', (currentPage - 1) * itemsPerPage);
            params.append('limit', itemsPerPage);
            
            // Send request to API
            const response = await fetch(`${API_URL}/prd/?${params.toString()}`, {
                method: 'GET',
                headers: headers
            });
            
            // Check response status
            if (!response.ok) {
                throw new Error('Failed to load PRDs');
            }
            
            // Parse response
            const data = await response.json();
            
            // Filter PRDs based on search and template filter
            let filteredPRDs = data;
            
            if (filterSettings.search) {
                filteredPRDs = filteredPRDs.filter(prd => 
                    prd.title.toLowerCase().includes(filterSettings.search.toLowerCase())
                );
            }
            
            if (filterSettings.template) {
                filteredPRDs = filteredPRDs.filter(prd => 
                    prd.template_type === filterSettings.template
                );
            }
            
            // Sort PRDs
            if (filterSettings.sort === 'newest') {
                filteredPRDs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            } else if (filterSettings.sort === 'oldest') {
                filteredPRDs.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
            } else if (filterSettings.sort === 'title') {
                filteredPRDs.sort((a, b) => a.title.localeCompare(b.title));
            }
            
            // Update state
            currentPRDs = filteredPRDs;
            totalItems = filteredPRDs.length;
            
            // Display PRDs
            displayPRDs(filteredPRDs);
            
            // Update pagination
            updatePagination();
            
            // Hide loading
            hideLoading();
            
            // Show no PRDs message if needed
            if (filteredPRDs.length === 0) {
                showNoPRDsMessage();
            } else {
                hideNoPRDsMessage();
            }
            
        } catch (error) {
            console.error('Error loading PRDs:', error);
            showError('There was an error loading your PRDs. Please try again.');
            hideLoading();
        }
    }
    
    /**
     * Display PRDs in the list
     */
    function displayPRDs(prds) {
        if (!prdListElement) return;
        
        // Clear existing PRDs (except loading indicator)
        const rows = prdListElement.querySelectorAll('tr:not(#loading-indicator)');
        rows.forEach(row => row.remove());
        
        // Display PRDs
        prds.forEach(prd => {
            const row = document.createElement('tr');
            
            // Format created date
            const createdDate = new Date(prd.created_at);
            const formattedDate = createdDate.toLocaleDateString() + ' ' + 
                                 createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            // Format template type for display
            const templateDisplay = formatTemplateType(prd.template_type);
            
            row.innerHTML = `
                <td>${prd.title}</td>
                <td><span class="badge bg-info">${templateDisplay}</span></td>
                <td><span class="badge bg-secondary">${prd.format}</span></td>
                <td>${formattedDate}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-prd" data-id="${prd.id}">View</button>
                    <button class="btn btn-sm btn-outline-danger delete-prd" data-id="${prd.id}">Delete</button>
                </td>
            `;
            
            // Add event listeners
            const viewButton = row.querySelector('.view-prd');
            if (viewButton) {
                viewButton.addEventListener('click', () => viewPRD(prd));
            }
            
            const deleteButton = row.querySelector('.delete-prd');
            if (deleteButton) {
                deleteButton.addEventListener('click', () => deletePRD(prd.id));
            }
            
            prdListElement.appendChild(row);
        });
    }
    
    /**
     * Format template type for display
     */
    function formatTemplateType(templateType) {
        switch (templateType) {
            case 'crud_application':
                return 'CRUD Application';
            case 'ai_agent':
                return 'AI Agent';
            case 'saas_platform':
                return 'SaaS Platform';
            case 'custom':
                return 'Custom Template';
            default:
                return templateType;
        }
    }
    
    /**
     * Update pagination
     */
    function updatePagination() {
        if (!pagination || !paginationContainer) return;
        
        // Calculate total pages
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        
        // Show/hide pagination container
        if (totalPages <= 1) {
            paginationContainer.classList.add('d-none');
            return;
        } else {
            paginationContainer.classList.remove('d-none');
        }
        
        // Clear existing pagination
        pagination.innerHTML = '';
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>`;
        prevLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                loadPRDs();
            }
        });
        pagination.appendChild(prevLi);
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            pageLi.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                loadPRDs();
            });
            pagination.appendChild(pageLi);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a>`;
        nextLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                loadPRDs();
            }
        });
        pagination.appendChild(nextLi);
    }
    
    /**
     * View PRD details in modal
     */
    function viewPRD(prd) {
        // Store current PRD
        window.currentPRD = prd;
        
        // Update modal title
        if (modalTitle) {
            modalTitle.textContent = prd.title;
        }
        
        // Update modal content
        if (modalContent) {
            if (prd.format === 'markdown') {
                modalContent.innerHTML = marked.parse(prd.content);
            } else if (prd.format === 'json') {
                try {
                    const formattedJson = JSON.stringify(JSON.parse(prd.content), null, 2);
                    modalContent.innerHTML = `<pre><code>${formattedJson}</code></pre>`;
                } catch (e) {
                    modalContent.innerHTML = `<pre><code>${prd.content}</code></pre>`;
                }
            } else {
                modalContent.innerHTML = `<pre>${prd.content}</pre>`;
            }
        }
        
        // Show modal
        const modal = new bootstrap.Modal(viewPrdModal);
        modal.show();
    }
    
    /**
     * Delete PRD
     */
    async function deletePRD(prdId) {
        if (!confirm('Are you sure you want to delete this PRD? This action cannot be undone.')) {
            return;
        }
        
        try {
            // Get auth headers
            const headers = window.AuthModule.getAuthHeaders();
            
            // Send request to API
            const response = await fetch(`${API_URL}/prd/${prdId}`, {
                method: 'DELETE',
                headers: headers
            });
            
            // Check response status
            if (!response.ok) {
                throw new Error('Failed to delete PRD');
            }
            
            // Reload PRDs
            loadPRDs();
            
        } catch (error) {
            console.error('Error deleting PRD:', error);
            alert('There was an error deleting the PRD. Please try again.');
        }
    }
    
    /**
     * Copy modal content to clipboard
     */
    function copyModalContent() {
        if (!window.currentPRD) return;
        
        navigator.clipboard.writeText(window.currentPRD.content)
            .then(() => {
                // Change button text temporarily
                const originalText = modalCopyButton.textContent;
                modalCopyButton.textContent = 'Copied!';
                setTimeout(() => {
                    modalCopyButton.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    }
    
    /**
     * Download modal content as a file
     */
    function downloadModalContent() {
        if (!window.currentPRD) return;
        
        const prd = window.currentPRD;
        let filename, content, fileType;
        
        if (prd.format === 'markdown') {
            filename = `${prd.title.replace(/\s+/g, '_')}.md`;
            content = prd.content;
            fileType = 'text/markdown';
        } else if (prd.format === 'json') {
            filename = `${prd.title.replace(/\s+/g, '_')}.json`;
            content = JSON.stringify(JSON.parse(prd.content), null, 2);
            fileType = 'application/json';
        } else {
            filename = `${prd.title.replace(/\s+/g, '_')}.txt`;
            content = prd.content;
            fileType = 'text/plain';
        }
        
        // Create blob and download link
        const blob = new Blob([content], { type: fileType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    /**
     * Show loading indicator
     */
    function showLoading() {
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
        hideError();
    }
    
    /**
     * Hide loading indicator
     */
    function hideLoading() {
        if (loadingIndicator) {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        if (loadingError) {
            loadingError.textContent = message;
            loadingError.classList.remove('d-none');
        }
    }
    
    /**
     * Hide error message
     */
    function hideError() {
        if (loadingError) {
            loadingError.classList.add('d-none');
        }
    }
    
    /**
     * Show "no PRDs" message
     */
    function showNoPRDsMessage() {
        if (noPrdsMessage) {
            noPrdsMessage.classList.remove('d-none');
        }
    }
    
    /**
     * Hide "no PRDs" message
     */
    function hideNoPRDsMessage() {
        if (noPrdsMessage) {
            noPrdsMessage.classList.add('d-none');
        }
    }
});
