document.addEventListener('DOMContentLoaded', () => {
    const submitButton = document.getElementById('submit-button');
    const symptomsInput = document.getElementById('symptoms-input');
    const resultsCard = document.getElementById('results-card');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsContent = document.getElementById('results-content');
    
    // Add class to results card to trigger the animation styles
    resultsCard.classList.add('hidden');
    
    submitButton.addEventListener('click', async () => {
        const symptoms = symptomsInput.value.trim();
        if (!symptoms) {
            alert("Please enter symptoms before checking.");
            return;
        }
        
        // 1. Start Loading State
        resultsCard.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        submitButton.disabled = true;
        
        // Reset card opacity/transform if it was previously shown/hidden
        resultsCard.style.opacity = '0';
        resultsCard.style.transform = 'translateY(10px)';
        
        try {
            const response = await fetch('/check-symptoms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms: symptoms })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                console.log("API Success! Data received:", data); // DEBUGGING: Confirm data structure
                
                // 2. Display Results Content
                displayResults(data);
                resultsContent.classList.remove('hidden');
                
                // --- FIX: Trigger the Final Reveal Animation ---
                // This removes the CSS-based hiding styles (opacity/transform)
                // The CSS transition properties will handle the smooth fade-in/slide-up effect
                resultsCard.style.opacity = '1';
                resultsCard.style.transform = 'translateY(0)';
                // ------------------------------------------------
                
            } else {
                alert(`Error: ${data.detail || 'An unknown error occurred.'}`);
            }
            
        } catch (error) {
            console.error('Fetch error:', error);
            alert('A network error occurred. Check server connection.');
        } finally {
            // 3. End Loading State
            loadingIndicator.classList.add('hidden');
            submitButton.disabled = false;
        }
    });
    
    function displayResults(data) {
        document.getElementById('possible-conditions').innerHTML = data.possible_conditions.map(item => `<li>${item}</li>`).join('');
        
        document.getElementById('red-flags').innerHTML = data.red_flags.map(item => 
            `<li class="red-flag-item">${item}</li>`
        ).join('');
        
        document.getElementById('next-steps').innerHTML = data.recommended_next_steps.map(item => `<li>${item}</li>`).join('');
    }
});
