document.addEventListener('DOMContentLoaded', () => {
    const submitButton = document.getElementById('submit-button');
    const symptomsInput = document.getElementById('symptoms-input');
    const resultsCard = document.getElementById('results-card');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsContent = document.getElementById('results-content');
    
    // Initial state setup
    resultsCard.classList.add('hidden');
    
    submitButton.addEventListener('click', async () => {
        const symptoms = symptomsInput.value.trim();
        if (!symptoms) {
            alert("Please enter symptoms before checking.");
            return;
        }
        
        // 1. Start Loading State and Hide Previous Results
        resultsCard.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        submitButton.disabled = true; // Disable button while loading
        
        try {
            const response = await fetch('/check-symptoms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms: symptoms })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // 2. Display Results
                displayResults(data);
                resultsContent.classList.remove('hidden');
            } else {
                // 3. Handle API Errors (400, 500)
                alert(`Error: ${data.detail || 'An unknown error occurred.'}`);
            }
            
        } catch (error) {
            console.error('Fetch error:', error);
            alert('A network error occurred. Check server connection.');
        } finally {
            // 4. End Loading State
            loadingIndicator.classList.add('hidden');
            submitButton.disabled = false;
        }
    });
    
    function displayResults(data) {
        document.getElementById('possible-conditions').innerHTML = data.possible_conditions.map(item => `<li>${item}</li>`).join('');
        
        // Highlight Red Flags
        document.getElementById('red-flags').innerHTML = data.red_flags.map(item => 
            `<li class="red-flag-item">${item}</li>`
        ).join('');
        
        document.getElementById('next-steps').innerHTML = data.recommended_next_steps.map(item => `<li>${item}</li>`).join('');
    }
});
