let lineChart;
let allTimestamps = [];
let currentTimestampIndex = 0;
let currentDayData = null;
let holdInterval = null;
let holdTimeout = null;
let availableDates = [];
let currentSelectedDate = null;

// Load all available dates
function loadAvailableDates() {
    fetch('/api/available-dates')
    .then(response => response.json())
    .then(result => {
        if (result.success && result.dates.length > 0) {
            availableDates = result.dates;
            populateDateDropdown();
            // Load most recent date by default
            currentSelectedDate = availableDates[0];
            loadTimestampsForDate(currentSelectedDate);
        }
    })
    .catch(error => {
        console.error('Error loading dates:', error);
    });
}

// Populate date dropdown
function populateDateDropdown() {
    const select = document.getElementById('dateFilter');
    select.innerHTML = '<option value="">-- Select a Date --</option>';
    
    availableDates.forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        option.textContent = date;
        select.appendChild(option);
    });
    
    // Select the most recent date
    if (availableDates.length > 0) {
        select.value = availableDates[0];
    }
}

// Load data for selected date
function loadDataForSelectedDate() {
    const select = document.getElementById('dateFilter');
    const selectedDate = select.value;
    
    if (selectedDate) {
        currentSelectedDate = selectedDate;
        loadTimestampsForDate(selectedDate);
    }
}

// Load all data (no date filter)
function loadAllData() {
    document.getElementById('dateFilter').value = '';
    currentSelectedDate = null;
    loadTimestampsForDate(null);
}

// Load all timestamps for a specific date
function loadTimestampsForDate(date) {
    const url = date ? `/api/line-data?date=${encodeURIComponent(date)}&sensor=all` : '/api/line-data?sensor=all';
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            // Store all timestamps
            allTimestamps = data.labels;
            currentDayData = data;
            currentTimestampIndex = 0;
            
            // Load first reading
            loadReadingAtIndex(0);
        } else {
            document.getElementById('lineChartContainer').innerHTML = 
                '<div style="text-align: center; color: #ccc; padding: 2rem;">No data available for this selection.</div>';
        }
    })
    .catch(error => {
        console.error('Error loading timestamps:', error);
    });
}

// Load reading at specific index
function loadReadingAtIndex(index) {
    if (!currentDayData || !allTimestamps.length) return;
    
    currentTimestampIndex = index;
    
    // Update display
    document.getElementById('currentTimestamp').textContent = allTimestamps[index];
    document.getElementById('readingPosition').textContent = `${index + 1} of ${allTimestamps.length}`;
    
    // Update current values from datasets
    const tempDataset = currentDayData.datasets.find(d => d.label.includes('Temperature'));
    const humidityDataset = currentDayData.datasets.find(d => d.label.includes('Humidity'));
    const pressureDataset = currentDayData.datasets.find(d => d.label.includes('Pressure'));
    
    if (tempDataset) {
        document.getElementById('currentTemp').textContent = `${tempDataset.data[index]}°C`;
    }
    if (humidityDataset) {
        document.getElementById('currentHumidity').textContent = `${humidityDataset.data[index]}%`;
    }
    if (pressureDataset) {
        document.getElementById('currentPressure').textContent = `${pressureDataset.data[index]} hPa`;
    }
    
    // Update chart with full day data
    updateChart(currentDayData);
    updateStats(currentDayData);
}

// Previous button
function loadPrevious() {
    if (currentTimestampIndex > 0) {
        loadReadingAtIndex(currentTimestampIndex - 1);
    }
}

// Next button
function loadNext() {
    if (currentTimestampIndex < allTimestamps.length - 1) {
        loadReadingAtIndex(currentTimestampIndex + 1);
    }
}

// Start holding previous
function startHoldingPrevious() {
    loadPrevious();
    holdTimeout = setTimeout(() => {
        holdInterval = setInterval(() => {
            loadPrevious();
        }, 100); // Navigate every 100ms when held
    }, 300); // Wait 300ms before starting rapid navigation
}

// Start holding next
function startHoldingNext() {
    loadNext();
    holdTimeout = setTimeout(() => {
        holdInterval = setInterval(() => {
            loadNext();
        }, 100); // Navigate every 100ms when held
    }, 300); // Wait 300ms before starting rapid navigation
}

// Stop holding
function stopHolding() {
    if (holdTimeout) {
        clearTimeout(holdTimeout);
        holdTimeout = null;
    }
    if (holdInterval) {
        clearInterval(holdInterval);
        holdInterval = null;
    }
}

// Update chart display
function updateChart(data) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    
    if (lineChart) {
        lineChart.destroy();
    }
    
    if (!data.datasets || data.datasets.length === 0) {
        document.getElementById('lineChartContainer').innerHTML = 
            '<div style="text-align: center; color: #ccc; padding: 2rem;">No data available.</div>';
        return;
    }
    
    // Apply CTRLHOUSE styling
    data.datasets.forEach(dataset => {
        dataset.borderWidth = 3;
        dataset.pointBorderColor = 'rgba(255, 255, 255, 1)';
        dataset.pointBorderWidth = 2;
        dataset.pointRadius = 4;
        dataset.pointHoverRadius = 6;
        dataset.fill = false;
    });
    
    lineChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff',
                        font: { size: 14 }
                    }
                },
                title: {
                    display: true,
                    text: 'Environmental Monitoring - Lab 08 Data',
                    color: '#fff',
                    font: { size: 16, weight: 'bold' }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 10
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#ccc' },
                    title: {
                        display: true,
                        text: 'Temperature (°C) / Humidity (%)',
                        color: '#fff'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: false,
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#ccc' },
                    title: {
                        display: true,
                        text: 'Pressure (hPa)',
                        color: '#fff'
                    }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: {
                        color: '#ccc',
                        maxTicksLimit: 12
                    },
                    title: {
                        display: true,
                        text: 'Time',
                        color: '#fff'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Update statistics display
function updateStats(data) {
    if (!data || !data.datasets || data.datasets.length === 0) return;
    
    const dataCount = data.labels.length;
    document.getElementById('dataPointsCount').textContent = dataCount;
    
    // Find temperature dataset
    const tempDataset = data.datasets.find(d => d.label.includes('Temperature'));
    
    if (tempDataset) {
        const temperatures = tempDataset.data;
        const avgTemp = (temperatures.reduce((sum, temp) => sum + temp, 0) / dataCount).toFixed(1);
        const minTemp = Math.min(...temperatures).toFixed(1);
        const maxTemp = Math.max(...temperatures).toFixed(1);
        
        // Update detailed statistics
        const statsContainer = document.getElementById('temperatureStats');
        statsContainer.innerHTML = 
            '<div class="glass" style="padding: 1rem; border-radius: 10px; text-align: center;">' +
            '<h4 style="color: #fff; margin-bottom: 0.5rem;">Avg Temp</h4>' +
            '<p style="color: #fff; font-size: 1.5rem; font-weight: bold;">' + avgTemp + '°C</p>' +
            '</div>' +
            '<div class="glass" style="padding: 1rem; border-radius: 10px; text-align: center;">' +
            '<h4 style="color: #fff; margin-bottom: 0.5rem;">Min Temp</h4>' +
            '<p style="color: #fff; font-size: 1.5rem; font-weight: bold;">' + minTemp + '°C</p>' +
            '</div>' +
            '<div class="glass" style="padding: 1rem; border-radius: 10px; text-align: center;">' +
            '<h4 style="color: #fff; margin-bottom: 0.5rem;">Max Temp</h4>' +
            '<p style="color: #fff; font-size: 1.5rem; font-weight: bold;">' + maxTemp + '°C</p>' +
            '</div>' +
            '<div class="glass" style="padding: 1rem; border-radius: 10px; text-align: center;">' +
            '<h4 style="color: #fff; margin-bottom: 0.5rem;">Range</h4>' +
            '<p style="color: #fff; font-size: 1.5rem; font-weight: bold;">' + minTemp + '°C - ' + maxTemp + '°C</p>' +
            '</div>';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('lineChartContainer').style.height = '400px';
    loadAvailableDates();
});
