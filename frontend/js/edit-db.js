document.addEventListener('DOMContentLoaded', () => {
    const csvEditor = document.getElementById('csv-editor');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const loadBtn = document.getElementById('load-btn');
    const linesCount = document.getElementById('lines-count');
    const messageDiv = document.getElementById('message');
    
    // Default number of lines to load
    const DEFAULT_LINES = 20;
    
    // Store metadata about loaded data
    let currentData = {
        totalRows: 0,
        retrievedRows: 0
    };
    
    // Czech translations
    const translations = {
        loading: 'Načítání dat...',
        noData: 'Žádná data nenalezena',
        saved: 'Data úspěšně uložena',
        error: 'Chyba:',
        networkError: 'Chyba sítě:',
        confirmSave: 'Opravdu chcete uložit změny? Tato akce nelze vrátit.',
        canceled: 'Změny zrušeny',
        lineFormat: '[Název kanystru],[Stav (Filled/Emptied)],[Datum a čas (HH:MM:SS DD.MM.YYYY)]',
        databaseChanged: 'Databáze byla změněna někým jiným od načtení. Obnovte data a zkuste znovu.'
    };
    
    // Load data on page load
    loadLastNLines(DEFAULT_LINES);
    
    // Load button handler
    loadBtn.addEventListener('click', () => {
        const n = parseInt(linesCount.value) || DEFAULT_LINES;
        loadLastNLines(n);
    });
    
    // Save button handler
    saveBtn.addEventListener('click', saveChanges);
    
    // Cancel button handler
    cancelBtn.addEventListener('click', () => {
        const n = parseInt(linesCount.value) || DEFAULT_LINES;
        loadLastNLines(n);
        showMessage(translations.canceled, 'info');
    });
    
    // Function to load last N lines
    async function loadLastNLines(n) {
        try {
            showMessage(translations.loading, 'info');
            
            const response = await fetch(`/api/data-csv/last-n?n=${n}`);
            const data = await response.json();
            
            if (data.error) {
                showMessage(`${translations.error} ${data.error}`, 'error');
                return;
            }
            
            if (!data.lines || data.lines.length === 0) {
                csvEditor.value = translations.noData;
                showMessage(translations.noData, 'info');
                return;
            }
            
            // Store metadata for later use when saving
            currentData.totalRows = data.totalRows;
            currentData.retrievedRows = data.retrievedRows;
            
            // Format the lines for display
            const formattedLines = data.lines.map(line => 
                `${line.JugName},${line.State},${line.DateTime}`
            );
            
            // Display the lines
            csvEditor.value = formattedLines.join('\n');
            
            showMessage(`Načteno ${data.lines.length} řádků z celkových ${data.totalRows}`, 'success');
        } catch (error) {
            showMessage(`${translations.networkError} ${error.message}`, 'error');
        }
    }
    
    // Function to save changes
    async function saveChanges() {
        try {
            // Confirm before saving
            if (!confirm(translations.confirmSave)) {
                return;
            }
            
            const lines = csvEditor.value.split('\n')
                .filter(line => line.trim() !== '')
                .map(line => {
                    const parts = line.split(',');
                    if (parts.length >= 3) {
                        return {
                            JugName: parts[0].trim(),
                            State: parts[1].trim(),
                            DateTime: parts.slice(2).join(',').trim() // Handle cases where DateTime might contain commas
                        };
                    }
                    return null;
                })
                .filter(line => line !== null);
            
            if (lines.length === 0) {
                showMessage('Žádná platná data k uložení', 'error');
                return;
            }
            
            showMessage('Ukládání...', 'info');
            
            const response = await fetch('/api/data-csv/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    lines: lines,
                    totalRows: currentData.totalRows,
                    editedCount: currentData.retrievedRows
                })
            });
            
            const result = await response.json();
            
            if (response.status === 409) {
                // Conflict error - database changed
                showMessage(translations.databaseChanged, 'error');
                return;
            }
            
            if (result.error) {
                showMessage(`${translations.error} ${result.error}`, 'error');
            } else {
                showMessage(translations.saved, 'success');
                
                // Update stored metadata with new values
                if (result.newTotal) {
                    currentData.totalRows = result.newTotal;
                }
                
                // Reload to show the updated data
                const n = parseInt(linesCount.value) || DEFAULT_LINES;
                loadLastNLines(n);
            }
        } catch (error) {
            showMessage(`${translations.networkError} ${error.message}`, 'error');
        }
    }
    
    // Function to show messages
    function showMessage(text, type = 'info') {
        messageDiv.textContent = text;
        messageDiv.className = type;
        
        // Auto-hide success messages after 3 seconds
        if (type === 'success') {
            setTimeout(() => {
                messageDiv.textContent = '';
                messageDiv.className = '';
            }, 3000);
        }
    }
});
