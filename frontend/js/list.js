document.addEventListener('DOMContentLoaded', () => {
    const jugsList = document.getElementById('jugs-list');
    const refreshBtn = document.getElementById('refresh-btn');
    const messageDiv = document.getElementById('message');
    
    // Czech translations
    const translations = {
        loading: 'Načítání kanystů...',
        noJugsFound: 'Žádné naplněné kanystry nenalezeny',
        loaded: 'Načtená data:',
        jugs: 'kanystry',
        markEmpty: 'Vyzvednout',
        markedEmpty: 'Kanystr označen jako prázdný',
        error: 'Chyba',
        networkError: 'Chyba sítě:'
    };
    
    // Load the jugs on page load
    loadFilledJugs();
    
    // Refresh button handler
    refreshBtn.addEventListener('click', loadFilledJugs);
    
    async function loadFilledJugs() {
        try {
            showMessage(translations.loading, 'info');
            
            const response = await fetch('/api/jugs?state=filled');
            const jugs = await response.json();
            
            renderJugsList(jugs);
            
            if (jugs.length === 0) {
                showMessage(translations.noJugsFound, 'info');
            } else {
                showMessage(`${translations.loaded} ${jugs.length} ${translations.jugs}`, 'success');
            }
        } catch (error) {
            showMessage(`${translations.error} ${error.message}`, 'error');
        }
    }
    
    function renderJugsList(jugs) {
        jugsList.innerHTML = '';
        
        jugs.forEach(jug => {
            const row = document.createElement('tr');
            
            // Jug name cell
            const nameCell = document.createElement('td');
            nameCell.textContent = jug.JugName;
            
            // Fill date cell - format to show only date (not time)
            const dateCell = document.createElement('td');
            // Parse datetime string (format: 'HH:MM:SS DD.MM.YYYY')
            try {
                // Extract just the date part (DD.MM.YYYY)
                const datePart = jug.DateTime.split(' ')[1];
                dateCell.textContent = datePart;
            } catch (e) {
                dateCell.textContent = jug.DateTime;
            }
            
            // Action cell with empty button
            const actionCell = document.createElement('td');
            const emptyBtn = document.createElement('button');
            emptyBtn.textContent = translations.markEmpty;
            emptyBtn.addEventListener('click', () => markAsEmpty(jug.JugName));
            actionCell.appendChild(emptyBtn);
            
            row.appendChild(nameCell);
            row.appendChild(dateCell);
            row.appendChild(actionCell);
            
            jugsList.appendChild(row);
        });
    }
    
    async function markAsEmpty(jugName) {
        try {
            const response = await fetch('/api/jugs/empty', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jugName: jugName
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                showMessage(`${translations.markedEmpty}: ${jugName}`, 'success');
                loadFilledJugs();
            } else {
                showMessage(`${translations.error}`, 'error');
            }
        } catch (error) {
            showMessage(`${translations.networkError} ${error.message}`, 'error');
        }
    }
    
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
