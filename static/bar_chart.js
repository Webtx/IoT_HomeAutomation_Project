let motionChart = null;
let motionReadings = [];

// Export to window for access from security.html
window.motionReadings = motionReadings;

// Load motion data and create chart
function loadMotionData() {
    fetch('/api/motion-data')
    .then(response => response.json())
    .then(result => {
        if (result.success && result.data.length > 0) {
            motionReadings = result.data;
            window.motionReadings = motionReadings; // Update window reference
            createMotionChart();
            console.log('Loaded', motionReadings.length, 'motion readings');
        } else {
            console.error('No motion data available');
        }
    })
    .catch(error => {
        console.error('Error loading motion data:', error);
    });
}

// Create motion detection bar chart
function createMotionChart() {
    if (motionReadings.length === 0) {
        console.log('No readings to display');
        return;
    }
    
    const ctx = document.getElementById('motionChart');
    if (!ctx) {
        console.error('Canvas element not found');
        return;
    }
    
    const context = ctx.getContext('2d');
    
    // Destroy existing chart if it exists
    if (motionChart) {
        motionChart.destroy();
    }
    
    // Prepare data - reverse to show oldest to newest
    const reversedData = [...motionReadings].reverse();
    const labels = reversedData.map(reading => {
        const timestamp = new Date(reading.timestamp);
        const hours = timestamp.getHours().toString().padStart(2, '0');
        const minutes = timestamp.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    });
    const counts = reversedData.map(reading => reading.count);
    
    // Alternating colors: pink and teal like the environmental chart
    const backgroundColors = counts.map((count, index) => {
        if (index % 2 === 0) {
            return 'rgba(255, 99, 132, 0.6)'; // Pink
        } else {
            return 'rgba(75, 192, 192, 0.6)'; // Teal
        }
    });
    
    const borderColors = counts.map((count, index) => {
        if (index % 2 === 0) {
            return 'rgb(255, 99, 132)'; // Pink
        } else {
            return 'rgb(75, 192, 192)'; // Teal
        }
    });
    
    motionChart = new Chart(context, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Motion Count',
                data: counts,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Motion Detection Over Time',
                    color: '#fff',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        borderColor: 'rgba(255, 255, 255, 0.3)'
                    },
                    title: {
                        display: true,
                        text: 'Motion Count',
                        color: '#fff',
                        font: {
                            size: 14
                        }
                    }
                },
                x: {
                    ticks: {
                        color: '#fff',
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        borderColor: 'rgba(255, 255, 255, 0.3)'
                    },
                    title: {
                        display: true,
                        text: 'Time (HH:MM)',
                        color: '#fff',
                        font: {
                            size: 14
                        }
                    }
                }
            }
        }
    });
    
    console.log('Motion chart created successfully with', motionReadings.length, 'data points');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Bar chart script loaded');
    loadMotionData();
    // Refresh every 30 seconds
    setInterval(loadMotionData, 30000);
});
