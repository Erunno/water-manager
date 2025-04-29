document.addEventListener('DOMContentLoaded', () => {
    const scannedList = document.getElementById('scanned-list');
    const clearBtn = document.getElementById('clear-btn');
    const submitBtn = document.getElementById('submit-btn');
    const messageDiv = document.getElementById('message');
    const readerDiv = document.getElementById('reader');

    // Czech translations
    const translations = {
        added: 'Přidáno',
        noJugs: 'Žádné kanystry nebyly naskenovány',
        cleared: 'Seznam naskenovaných vymazán',
        success: 'Úspěch',
        error: 'Chyba',
        networkError: 'Chyba sítě:',
        cameraIssue: 'Nelze přistoupit ke kameře. Ujistěte se, že jsou udělena oprávnění kamery a zkuste to znovu.',
        cameraRequired: 'Pro skenování QR kódů je nutný přístup ke kameře.',
        commonIssues: 'Časté problémy:',
        permissionDenied: 'Oprávnění kamery odepřeno',
        insecureConnection: 'Používání nezabezpečeného připojení (bez HTTPS)',
        cameraInUse: 'Kamera používána jinou aplikací',
        noCamera: 'Zařízení bez kamery',
        tryAgain: 'Zkusit znovu',
        invalidQR: 'Neplatný obsah QR kódu'
    };
    
    // Store scanned jugs in a Set to avoid duplicates
    const scannedJugs = new Set();
    
    // Initialize QR scanner
    const html5QrCode = new Html5Qrcode("reader");
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };
    
    // Start camera scanning with proper error handling
    html5QrCode.start(
        { facingMode: "environment" }, 
        config, 
        onScanSuccess,
        onScanError
    ).catch(error => {
        console.error("QR scanner failed to start:", error);
        showMessage(translations.cameraIssue, "error");
        
        const instructions = document.createElement('div');
        instructions.className = 'camera-instructions';
        instructions.innerHTML = `
            <p>${translations.cameraRequired}</p>
            <p>${translations.commonIssues}</p>
            <ul>
                <li>${translations.permissionDenied}</li>
                <li>${translations.insecureConnection}</li>
                <li>${translations.cameraInUse}</li>
                <li>${translations.noCamera}</li>
            </ul>
            <button id="retry-camera">${translations.tryAgain}</button>
        `;
        readerDiv.appendChild(instructions);
        
        document.getElementById('retry-camera').addEventListener('click', () => {
            location.reload();
        });
    });
    
    function onScanSuccess(decodedText) {
        try {
            // Properly decode the QR content and remove any BOM characters or extra whitespace
            let jugName = decodeURIComponent(decodedText).trim();
            
            // Remove BOM if present (appears as \uFEFF)
            jugName = jugName.replace(/^\uFEFF/, '');
            
            // Play the beep sound
            const beep = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU...');
            beep.volume = 0.2;
            beep.play();
            
            // Add to set if not already there
            if (!scannedJugs.has(jugName)) {
                scannedJugs.add(jugName);
                updateScannedList();
                
                showMessage(`${translations.added}: ${jugName}`, 'success');
            }
        } catch (error) {
            console.error("Error processing QR code:", error);
            showMessage(translations.invalidQR, "error");
        }
    }
    
    function onScanError(error) {
        console.warn("QR scan error:", error);
    }
    
    function updateScannedList() {
        scannedList.innerHTML = '';
        scannedJugs.forEach(jug => {
            const li = document.createElement('li');
            li.textContent = jug;
            scannedList.appendChild(li);
        });
    }
    
    function showMessage(text, type = 'info') {
        messageDiv.textContent = text;
        messageDiv.className = type;
        
        setTimeout(() => {
            messageDiv.textContent = '';
            messageDiv.className = '';
        }, 3000);
    }
    
    clearBtn.addEventListener('click', () => {
        scannedJugs.clear();
        updateScannedList();
        showMessage(translations.cleared);
    });
    
    submitBtn.addEventListener('click', async () => {
        if (scannedJugs.size === 0) {
            showMessage(translations.noJugs, 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/jugs/fill', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jugs: Array.from(scannedJugs)
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                showMessage(`${translations.success}! ${data.message}`, 'success');
                scannedJugs.clear();
                updateScannedList();
            } else {
                showMessage(`${translations.error}`, 'error');
            }
        } catch (error) {
            showMessage(`${translations.networkError} ${error.message}`, 'error');
        }
    });
});
