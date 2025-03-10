// Function to render a pie chart
function renderPieChart(canvasId, data, labels, title) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: title
                }
            }
        }
    });
}

// Function to render a bar chart
function renderBarChart(canvasId, labels, incomeData, expenseData, title) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Expenses',
                    data: expenseData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Example usage
document.addEventListener('DOMContentLoaded', function() {
    // Example data for pie chart
    const expenseData = [300, 50, 100, 40, 120, 60];
    const expenseLabels = ['Rent', 'Groceries', 'Utilities', 'Transport', 'Entertainment', 'Others'];
    renderPieChart('expensePieChart', expenseData, expenseLabels, 'Expenses by Category');

    // Example data for bar chart
    const months = ['January', 'February', 'March', 'April', 'May', 'June'];
    const incomeData = [5000, 6000, 7000, 8000, 7500, 7200];
    const expenseDataBar = [3000, 3500, 4000, 4500, 4200, 4100];
    renderBarChart('incomeExpenseBarChart', months, incomeData, expenseDataBar, 'Monthly Income and Expenses');
});