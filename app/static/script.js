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

    console.log("Loaded elements:", { viewHistoryButton, historyModal, closeModalButton, historyList });

    // Reveal animation initial setup
    resultsCard.classList.add('hidden');

    // --- Open History Modal ---
    viewHistoryButton.addEventListener('click', () => {
        console.log("History button clicked.");
        fetchHistory();
        historyModal.classList.remove('hidden');
    });

    // --- Close Modal ---
    closeModalButton.addEventListener('click', () => {
        historyModal.classList.add('hidden');
    });

    // --- Close if clicking outside modal ---
    window.addEventListener('click', (event) => {
        if (event.target === historyModal) {
            historyModal.classList.add('hidden');
        }
    });

    // --- Fetch History Function ---
    async function fetchHistory() {
        historyList.innerHTML = '<p class="loading-message">Loading history...</p>';

        try {
            const response = await fetch('/history');
            const json = await response.json();

            if (response.ok && json.history && json.history.length > 0) {
                historyList.innerHTML = json.history.map(item => `
                    <div class="history-item">
                        <div class="history-meta">
                            <strong>ID: ${item.id}</strong>
                            <span class="history-date">${item.query_timestamp}</span>
                        </div>
                        <p class="history-input">
                            <span class="label">Input:</span> ${item.symptoms_input}
                        </p>
                        <div class="history-summary">
                            <span class="label">Conditions:</span>
                            ${item.llm_response_json.possible_conditions.join(', ')}
                        </div>
                    </div>
                `).join('');
            } else {
                historyList.innerHTML = '<p class="loading-message">No history recorded yet.</p>';
            }

        } catch (error) {
            console.error("History fetch error:", error);
            historyList.innerHTML = '<p class="error-message">Error loading history.</p>';
        }
    }

    // --- Symptom Check Handler ---
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
                alert(data.detail || "Error processing symptoms.");
            }
        } catch (err) {
            console.error(err);
            alert("Network error.");
        } finally {
            loadingIndicator.classList.add('hidden');
            submitButton.disabled = false;
        }
    });

    function displayResults(data) {
        document.getElementById('possible-conditions').innerHTML =
            data.possible_conditions.map(i => `<li>${i}</li>`).join('');

        document.getElementById('red-flags').innerHTML =
            data.red_flags.map(i => `<li class="red-flag-item">${i}</li>`).join('');

        document.getElementById('next-steps').innerHTML =
            data.recommended_next_steps.map(i => `<li>${i}</li>`).join('');
    }
});
