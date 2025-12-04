document.addEventListener('DOMContentLoaded', () => {
    const submitButton = document.getElementById('submit-button');
    const symptomsInput = document.getElementById('symptoms-input');
    const resultsCard = document.getElementById('results-card');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsContent = document.getElementById('results-content');

    // --- History Elements ---
    const viewHistoryButton = document.getElementById('view-history-button');
    const historyModal = document.getElementById('history-modal');
    const closeModalButton = document.getElementById('close-modal-button');
    const historyList = document.getElementById('history-list');

    // Reveal animation initial setup
    resultsCard.classList.add('hidden');

    /* ---------------------------------------------------------
       VIEW HISTORY MODAL HANDLING
    --------------------------------------------------------- */

    viewHistoryButton.addEventListener('click', () => {
        console.log("History button clicked. Attempting to fetch history..."); // DEBUG
        fetchHistory();
        historyModal.classList.remove('hidden');
    });

    closeModalButton.addEventListener('click', () => {
        historyModal.classList.add('hidden');
    });

    window.addEventListener('click', (event) => {
        if (event.target === historyModal) {
            historyModal.classList.add('hidden');
        }
    });

    /* ---------------------------------------------------------
       FETCH HISTORY (FINAL CORRECTED VERSION)
    --------------------------------------------------------- */

    async function fetchHistory() {
        historyList.innerHTML = '<p class="loading-message">Loading history...</p>';

        try {
            const response = await fetch('/history');
            console.log("History fetch response status:", response.status); // DEBUG
            const json = await response.json();

            if (response.ok && json.history && json.history.length > 0) {
                console.log("Successfully fetched history data:", json.history); // DEBUG

                historyList.innerHTML = json.history
                    .map(item => {
                        let llmResponse = item.llm_response_json;
                        
                        // FIX: Check if the response is a JSON string and parse it if necessary
                        if (typeof llmResponse === 'string') {
                            try {
                                llmResponse = JSON.parse(llmResponse);
                            } catch (e) {
                                // This internal error should not stop the loop
                                console.error("Failed to parse history JSON string for item:", item.id, e); 
                                llmResponse = null; 
                            }
                        }
                        
                        // Robustly check for and join conditions
                        const conditions =
                            llmResponse &&
                            Array.isArray(llmResponse.possible_conditions)
                                ? llmResponse.possible_conditions.join(', ')
                                : 'Conditions not available';

                        // Ensure timestamp is a string (it should be after the Python fix)
                        const timestamp = item.query_timestamp || 'Time unavailable';

                        return `
                            <div class="history-item">
                                <div class="history-meta">
                                    <strong>ID: ${item.id}</strong>
                                    <span class="history-date">${timestamp}</span>
                                </div>

                                <p class="history-input">
                                    <span class="label">Input:</span> ${item.symptoms_input}
                                </p>

                                <div class="history-summary">
                                    <span class="label">Conditions:</span> 
                                    ${conditions}
                                </div>
                            </div>
                        `;
                    })
                    .join('');
            } else {
                console.log("History array is empty or response not OK.", json); // DEBUG
                historyList.innerHTML = '<p class="loading-message">No history recorded yet.</p>';
            }

        } catch (error) {
            // This is the network/fatal parsing error catch
            console.error('CRITICAL Error fetching history:', error); 
            historyList.innerHTML =
                '<p class="error-message">Failed to load history. Please check server logs.</p>';
        }
    }

    /* ---------------------------------------------------------
       SUBMIT SYMPTOM CHECK REQUEST
    --------------------------------------------------------- */
    submitButton.addEventListener('click', async () => {
        const symptoms = symptomsInput.value.trim();
        if (!symptoms) {
            alert("Please enter symptoms before checking.");
            return;
        }

        resultsCard.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        submitButton.disabled = true;

        resultsCard.style.opacity = '0';
        resultsCard.style.transform = 'translateY(10px)';

        try {
            const response = await fetch('/check-symptoms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms })
            });

            const data = await response.json();

            if (response.ok) {
                displayResults(data);
                resultsContent.classList.remove('hidden');

                resultsCard.style.opacity = '1';
                resultsCard.style.transform = 'translateY(0)';
            } else {
                alert(`Error: ${data.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error("Fetch error:", error);
            alert("Network error. Check server connection.");
        } finally {
            loadingIndicator.classList.add('hidden');
            submitButton.disabled = false;
        }
    });

    /* ---------------------------------------------------------
       DISPLAY RESULTS
    --------------------------------------------------------- */
    function displayResults(data) {
        document.getElementById('possible-conditions').innerHTML =
            data.possible_conditions.map(item => `<li>${item}</li>`).join('');

        document.getElementById('red-flags').innerHTML =
            data.red_flags.map(item => `<li class="red-flag-item">${item}</li>`).join('');

        document.getElementById('next-steps').innerHTML =
            data.recommended_next_steps.map(item => `<li>${item}</li>`).join('');
    }
});