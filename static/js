let selectedFile = null;
let categoryChart = null;
let budgetChart = null;
let currentAnalysis = null;

// Smooth scroll function
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
}

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadBox = document.getElementById('uploadBox');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const sampleDataBtn = document.getElementById('sampleDataBtn');

// NEW: Feature elements
const actionButtons = document.getElementById('actionButtons');
const exportPdfBtn = document.getElementById('exportPdfBtn');
const openChatBtn = document.getElementById('openChatBtn');
const chatModal = document.getElementById('chatModal');
const closeChatBtn = document.getElementById('closeChatBtn');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const chatMessages = document.getElementById('chatMessages');

// File input change handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileName.textContent = selectedFile.name;
        fileInfo.style.display = 'block';
        uploadBox.style.display = 'none';
    }
});

// Drag and drop handlers
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        fileName.textContent = selectedFile.name;
        fileInfo.style.display = 'block';
        uploadBox.style.display = 'none';
    }
});

// Analyze button handler
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    loading.style.display = 'block';
    results.style.display = 'none';
    actionButtons.style.display = 'none';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentAnalysis = data;
            displayResults(data);
            actionButtons.style.display = 'flex';
        } else {
            alert('Error: ' + (data.error || 'Failed to analyze file'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
});

// Sample data button handler
sampleDataBtn.addEventListener('click', async () => {
    const sampleTransactions = [
        { date: '2024-01-05', description: 'Whole Foods Market', amount: -85.43 },
        { date: '2024-01-06', description: 'Shell Gas Station', amount: -45.20 },
        { date: '2024-01-07', description: 'Netflix Subscription', amount: -15.99 },
        { date: '2024-01-08', description: 'Starbucks Coffee', amount: -6.75 },
        { date: '2024-01-09', description: 'Amazon Purchase', amount: -127.89 },
        { date: '2024-01-10', description: 'Uber Ride', amount: -18.50 },
        { date: '2024-01-11', description: 'Restaurant Dinner', amount: -67.32 },
        { date: '2024-01-12', description: 'Electric Bill', amount: -145.00 },
        { date: '2024-01-13', description: 'Gym Membership', amount: -49.99 },
        { date: '2024-01-14', description: 'Target Shopping', amount: -89.23 },
        { date: '2024-01-15', description: 'Movie Tickets', amount: -34.00 },
        { date: '2024-01-16', description: 'CVS Pharmacy', amount: -23.45 },
        { date: '2024-01-17', description: 'Internet Bill Comcast', amount: -79.99 },
        { date: '2024-01-18', description: 'Starbucks Coffee', amount: -5.50 },
        { date: '2024-01-19', description: 'Whole Foods Market', amount: -112.67 },
        { date: '2024-01-20', description: 'Spotify Subscription', amount: -9.99 },
        { date: '2024-01-21', description: 'Netflix Subscription', amount: -15.99 },
        { date: '2024-01-22', description: 'Salary Deposit', amount: 3500.00 }
    ];
    
    loading.style.display = 'block';
    results.style.display = 'none';
    actionButtons.style.display = 'none';
    
    try {
        const response = await fetch('/analyze-manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transactions: sampleTransactions })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentAnalysis = data;
            displayResults(data);
            actionButtons.style.display = 'flex';
        } else {
            alert('Error: ' + (data.error || 'Failed to analyze data'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
});

// Display results
function displayResults(data) {
    results.style.display = 'block';

    /* =========================
       1️⃣ SUMMARY (FIRST)
       ========================= */
    document.getElementById('totalSpending').textContent =
        '$' + Math.abs(data.total_spending || 0).toFixed(2);

    const expenseCategories = Object.keys(data.category_totals || {})
        .filter(cat => cat !== 'Income');

    document.getElementById('categoryCount').textContent =
        expenseCategories.length;

    document.getElementById('transactionCount').textContent =
        (data.categorized_transactions || []).length;

    /* =========================
       2️⃣ CHARTS (SECOND)
       ========================= */
    createCategoryChart(data.category_totals || {});
    createBudgetChart(
        data.category_totals || {},
        data.suggested_budget || {}
    );

    /* =========================
       3️⃣ INSIGHTS (THIRD)
       ========================= */
    displayInsights(data.insights || []);

    /* =========================
       4️⃣ RISK & OPPORTUNITY
       (Subscriptions, Anomalies, Goals)
       ========================= */
    displaySubscriptions(data.subscriptions || {});
    displayAnomalies(data.anomalies || {});
    displaySavingsGoals(data.savings_goals || {});

    /* =========================
       5️⃣ RAW DATA (LAST)
       ========================= */
    displayTransactions(data.categorized_transactions || []);
}

// Create category pie chart
function createCategoryChart(categoryTotals) {
    const ctx = document.getElementById('categoryChart');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const labels = Object.keys(categoryTotals).filter(cat => cat !== 'Income');
    const values = labels.map(cat => Math.abs(categoryTotals[cat]));

    
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Create budget comparison chart
function createBudgetChart(actual, budget) {
    const ctx = document.getElementById('budgetChart');
    
    if (budgetChart) {
        budgetChart.destroy();
    }
    
    const categories = Object.keys(budget).length
        ? Object.keys(budget)
        : Object.keys(actual).filter(cat => cat !== 'Income');
    const actualValues = categories.map(cat => Math.abs(actual[cat] || 0));
    const budgetValues = categories.map(cat => Math.abs(budget[cat] || 0));
    
    budgetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Actual Spending',
                    data: actualValues,
                    backgroundColor: '#667eea'
                },
                {
                    label: 'Suggested Budget',
                    data: budgetValues,
                    backgroundColor: '#43e97b'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Display insights
function displayInsights(insights) {
    const container = document.getElementById('insightsList');
    container.innerHTML = '';
    
    insights.forEach(insight => {
        const div = document.createElement('div');
        div.className = 'insight-item';
        div.textContent = insight;
        container.appendChild(div);
    });
}

// Display transactions table
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactionsBody');
    tbody.innerHTML = '';
    
    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${transaction.date || 'N/A'}</td>
            <td>${transaction.description || 'N/A'}</td>
            <td><span class="category-badge">${transaction.category || 'Other'}</span></td>
            <td>$${Math.abs(transaction.amount || 0).toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

// NEW: Display subscriptions
function displaySubscriptions(subscriptions) {
    const section = document.getElementById('subscriptionsSection');
    const list = document.getElementById('subscriptionsList');
    const total = document.getElementById('subscriptionTotal');
    const count = document.getElementById('subscriptionCount');
    
    if (subscriptions.count > 0) {
        section.style.display = 'block';
        total.textContent = '$' + subscriptions.total_monthly.toFixed(2);
        count.textContent = subscriptions.count;
        
        list.innerHTML = '';
        subscriptions.subscriptions.forEach(sub => {
            const div = document.createElement('div');
            div.className = 'subscription-item';
            div.innerHTML = `
                <div class="subscription-info">
                    <div class="subscription-merchant">${sub.merchant}</div>
                    <div class="subscription-frequency">Recurring ${sub.frequency}x</div>
                </div>
                <div class="subscription-amount">$${sub.amount.toFixed(2)}/mo</div>
            `;
            list.appendChild(div);
        });
    } else {
        section.style.display = 'none';
    }
}

// NEW: Display anomalies
function displayAnomalies(anomalies) {
    const section = document.getElementById('anomaliesSection');
    const list = document.getElementById('anomaliesList');
    
    if (anomalies.count > 0) {
        section.style.display = 'block';
        list.innerHTML = '';
        
        anomalies.anomalies.forEach(anomaly => {
            const div = document.createElement('div');
            div.className = 'anomaly-item';
            div.innerHTML = `
                <div class="anomaly-header">
                    <div class="anomaly-description">${anomaly.description}</div>
                    <div class="anomaly-amount">$${anomaly.amount.toFixed(2)}</div>
                </div>
                <div class="anomaly-alert">
                    ⚠️ ${anomaly.times_higher}x higher than your average spending of $${anomalies.average_spending}
                </div>
            `;
            list.appendChild(div);
        });
    } else {
        section.style.display = 'none';
    }
}

// NEW: Display savings goals
function displaySavingsGoals(savingsGoals) {
    const section = document.getElementById('savingsGoalsSection');
    const list = document.getElementById('savingsGoalsList');
    const tips = document.getElementById('savingsTips');
    
    if (savingsGoals.goals && savingsGoals.goals.length > 0) {
        section.style.display = 'block';
        list.innerHTML = '';
        
        savingsGoals.goals.forEach(goal => {
            const div = document.createElement('div');
            div.className = 'savings-goal-card';
            div.innerHTML = `
                <div class="goal-header">
                    <div class="goal-name">${goal.name}</div>
                    <div class="goal-priority ${goal.priority}">${goal.priority}</div>
                </div>
                <div class="goal-description">${goal.description}</div>
                <div class="goal-details">
                    <div class="goal-detail">
                        <div class="goal-detail-label">Target</div>
                        <div class="goal-detail-value">$${goal.target_amount}</div>
                    </div>
                    <div class="goal-detail">
                        <div class="goal-detail-label">Monthly</div>
                        <div class="goal-detail-value">$${goal.monthly_contribution}</div>
                    </div>
                    <div class="goal-detail">
                        <div class="goal-detail-label">Timeline</div>
                        <div class="goal-detail-value">${goal.months_to_complete} mo</div>
                    </div>
                </div>
            `;
            list.appendChild(div);
        });
        
        // Display tips
        tips.innerHTML = '<h4>💡 Savings Tips</h4>';
        savingsGoals.recommendations.forEach(tip => {
            const tipDiv = document.createElement('div');
            tipDiv.className = 'savings-tip';
            tipDiv.textContent = tip;
            tips.appendChild(tipDiv);
        });
    } else {
        section.style.display = 'none';
    }
}

function resetAnalysisState() {
    selectedFile = null;
    currentAnalysis = null;

    fileInput.value = '';

    results.style.display = 'none';
    actionButtons.style.display = 'none';
    fileInfo.style.display = 'none';
    uploadBox.style.display = 'block';

    if (categoryChart) {
        categoryChart.destroy();
        categoryChart = null;
    }

    if (budgetChart) {
        budgetChart.destroy();
        budgetChart = null;
    }

    chatMessages.innerHTML = '';
    chatModal.classList.remove('active');

    document.getElementById('insightsList').innerHTML = '';
    document.getElementById('transactionsBody').innerHTML = '';
    document.getElementById('subscriptionsSection').style.display = 'none';
    document.getElementById('anomaliesSection').style.display = 'none';
    document.getElementById('savingsGoalsSection').style.display = 'none';


    uploadBox.scrollIntoView({ behavior: 'smooth' });
}

// NEW: Export PDF functionality
/* ===============================
   EXPORT PDF (SAFE)
   =============================== */

if (exportPdfBtn) {
    exportPdfBtn.addEventListener('click', async () => {
        if (!currentAnalysis) {
            alert('No analysis available to export.');
            return;
        }

        try {
            const response = await fetch('/export-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ analysis: currentAnalysis })
            });

            if (!response.ok) {
                throw new Error('PDF generation failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `FinSight_Report_${new Date().toISOString().split('T')[0]}.pdf`;

            document.body.appendChild(a);
            a.click();

            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('PDF Export Error:', error);
            alert('Failed to export PDF');
        }
    });
}


// NEW: Chat functionality
openChatBtn.addEventListener('click', () => {
    chatModal.classList.add('active');
    chatInput.focus();
});

closeChatBtn.addEventListener('click', () => {
    chatModal.classList.remove('active');
});

// Close modal on outside click
chatModal.addEventListener('click', (e) => {
    if (e.target === chatModal) {
        chatModal.classList.remove('active');
    }
});

// Send chat message
async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentAnalysis) return;
    
    // Add user message
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message bot';
    typingIndicator.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                analysis: currentAnalysis
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        typingIndicator.remove();
        
        if (response.ok) {
            addChatMessage(data.reply, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        typingIndicator.remove();
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addChatMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendChatBtn.addEventListener('click', sendChatMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

// NEW: Reset / New Analysis button
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

if (newAnalysisBtn) {
    newAnalysisBtn.addEventListener('click', () => {
        resetAnalysisState();
    });
}
