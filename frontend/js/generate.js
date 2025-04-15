/**
 * PRD Generation handler for PRD Generator
 * Following Semantic Seed Coding Standards for JavaScript implementation
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const generateForm = document.getElementById('generate-form');
    const errorAlert = document.getElementById('generate-error');
    const generateButton = document.getElementById('generate-button');
    const generateSpinner = document.getElementById('generate-spinner');
    const resultSection = document.getElementById('result-section');
    const resultTitle = document.getElementById('result-title');
    const copyButton = document.getElementById('copy-button');
    const downloadButton = document.getElementById('download-button');
    
    // Initialize Markdown editor for the result
    let editor = null;
    if (document.getElementById('prd-content')) {
        editor = new EasyMDE({
            element: document.getElementById('prd-content'),
            spellChecker: false,
            toolbar: false,
            status: false,
            readOnly: true
        });
    }
    
    // Event listeners
    if (generateForm) {
        generateForm.addEventListener('submit', handleGenerate);
    }
    
    if (copyButton) {
        copyButton.addEventListener('click', copyPRDContent);
    }
    
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadPRD);
    }
    
    /**
     * Handle PRD generation form submission
     */
    async function handleGenerate(event) {
        event.preventDefault();
        
        // Get form data
        const formData = new FormData(generateForm);
        const prdData = {
            title: formData.get('title'),
            input_prompt: formData.get('input_prompt'),
            template_type: formData.get('template_type'),
            format: formData.get('format')
        };
        
        // Validate form data
        if (!prdData.title || !prdData.input_prompt || !prdData.template_type || !prdData.format) {
            showError('Please fill out all fields.');
            return;
        }
        
        try {
            // Show loading state
            setLoadingState(true);
            
            // Get auth headers
            const headers = {
                'Content-Type': 'application/json',
                ...window.AuthModule.getAuthHeaders()
            };
            
            // Send request to API
            const response = await fetch(`${API_URL}/prd/generate`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(prdData)
            });
            
            // Check response status
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate PRD');
            }
            
            // Parse response
            const data = await response.json();
            
            // Display result
            displayPRDResult(data);
            hideError();
            
        } catch (error) {
            console.error('PRD generation error:', error);
            showError('There was an error generating your PRD: ' + error.message);
        } finally {
            // Reset loading state
            setLoadingState(false);
        }
    }
    
    /**
     * Display PRD generation result
     */
    function displayPRDResult(prdData) {
        // Update title
        if (resultTitle) {
            resultTitle.textContent = prdData.title;
        }
        
        // Update content
        if (editor) {
            editor.value(prdData.content);
        }
        
        // Show result section
        if (resultSection) {
            resultSection.classList.remove('d-none');
            
            // Scroll to result section
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Store PRD data for download
        window.currentPRDData = prdData;
    }
    
    /**
     * Copy PRD content to clipboard
     */
    function copyPRDContent() {
        if (editor) {
            const content = editor.value();
            navigator.clipboard.writeText(content)
                .then(() => {
                    // Change button text temporarily
                    const originalText = copyButton.textContent;
                    copyButton.textContent = 'Copied!';
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                });
        }
    }
    
    /**
     * Download PRD content as a file
     */
    function downloadPRD() {
        if (!window.currentPRDData) return;
        
        const prdData = window.currentPRDData;
        let filename, content, fileType;
        
        if (prdData.format === 'markdown') {
            filename = `${prdData.title.replace(/\s+/g, '_')}.md`;
            content = prdData.content;
            fileType = 'text/markdown';
        } else if (prdData.format === 'json') {
            filename = `${prdData.title.replace(/\s+/g, '_')}.json`;
            content = JSON.stringify(JSON.parse(prdData.content), null, 2);
            fileType = 'application/json';
        } else {
            filename = `${prdData.title.replace(/\s+/g, '_')}.txt`;
            content = prdData.content;
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
     * Show error message
     */
    function showError(message) {
        if (errorAlert) {
            errorAlert.textContent = message;
            errorAlert.classList.remove('d-none');
        }
    }
    
    /**
     * Hide error message
     */
    function hideError() {
        if (errorAlert) {
            errorAlert.classList.add('d-none');
        }
    }
    
    /**
     * Set loading state for the generate button
     */
    function setLoadingState(isLoading) {
        if (generateButton && generateSpinner) {
            if (isLoading) {
                generateButton.disabled = true;
                generateSpinner.classList.remove('d-none');
                generateButton.querySelector('span:not(.spinner-border)') 
                    ? generateButton.querySelector('span:not(.spinner-border)').textContent = ' Generating...'
                    : generateButton.insertAdjacentText('beforeend', ' Generating...');
            } else {
                generateButton.disabled = false;
                generateSpinner.classList.add('d-none');
                generateButton.textContent = 'Generate PRD';
            }
        }
    }
});
