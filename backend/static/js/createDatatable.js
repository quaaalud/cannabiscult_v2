class RatingsDatatable {
    constructor(userEmail) {
        this.userEmail = userEmail;
        this.init();
    }

    async init() {
        try {
            const ratingsByProductType = await this.fetchRatings(this.userEmail);
            this.chartInstances = this.chartInstances || {};
            for (const [productType, ratings] of Object.entries(ratingsByProductType)) {
                ratings.sort((a, b) => a.strain.localeCompare(b.strain));
                this.createTableForProductType(productType, ratings);
            }
        } catch (error) {
            console.error('Error initializing ratings tables:', error);
        }
    }

    async fetchRatings(userEmail) {
        const response = await fetch(`/search/get_my_ratings?user_email=${encodeURIComponent(userEmail)}`);
        if (!response.ok) {
            throw new Error('Failed to fetch ratings');
        }
        return await response.json();
    }

    formatRating(value) {
        return value ? parseFloat(value).toFixed(2) : 'N/A';
    }
    
    addProductTableTab(productType, tabList, tabContent, ratings) {
        // Create the ProductTable tab
        const productTableTab = document.createElement('li');
        productTableTab.className = 'nav-item';
        const productTableLink = document.createElement('a');
        productTableLink.className = 'nav-link active text-dark'; // Active by default
        productTableLink.id = `productTable-tab-${productType}`;
        productTableLink.dataset.bsToggle = 'tab';
        productTableLink.href = `#productTable-${productType}`;
        productTableLink.role = 'tab';
        productTableLink.ariaControls = `productTable-${productType}`;
        productTableLink.ariaSelected = 'true';
        productTableLink.innerText = `${productType} Table`;
        productTableTab.appendChild(productTableLink);
      
        // Append the ProductTable tab to the tab list
        tabList.appendChild(productTableTab);
    
        // Create the content for the ProductTable tab
        const productTableContent = document.createElement('div');
        productTableContent.className = 'tab-pane fade show active'; // Active by default
        productTableContent.id = `productTable-${productType}`;
        productTableContent.role = 'tabpanel';
        productTableContent.ariaLabelledby = `productTable-tab-${productType}`;
    
        const container = document.createElement('div');
        container.id = `container${productType}`;
        container.className = 'container-fluid py-3';
    
        const titleHTML = `<h3 class="text-dark pt-3 pb-2 text-center">${productType}</h3>`;
        container.innerHTML = titleHTML;
    
        const searchContainerHTML = `
            <div class="row">
                <div class="col-12 col-md-9 col-lg-6 mx-auto">
                    <div class="form-outline mb-4" data-mdb-input-init="true">
                        <input type="text" class="form-control" id="datatable-search-input-${productType}">
                        <label class="form-label" for="datatable-search-input-${productType}">Search</label>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += searchContainerHTML;
    
        // Define columns based on ratings keys
        let columns = [
          { label: 'Strain', width: 150},
          { label: 'Cultivator', width: 150 }
        ];

        // Add rating columns dynamically
        Object.keys(ratings[0]).filter(key => key.endsWith('_rating')).forEach(key => {
          const columnValues = ratings.map(rating => parseFloat(rating[key]));
          columns.push({
            label: key.replace(/_/g, ' ').replace('rating', '').trim().toUpperCase(),
            sort: true,
          });
        });
    
        // Prepare rows data
        let rows = ratings.map(rating => {
            return columns.map(col => {
                let key = col.label.toLowerCase().replace(/ /g, '_') + '_rating';
                return rating[key] || rating[col.label.toLowerCase()];
            });
        });
    
        // Create a table container
        const tableContainer = document.createElement('div');
        tableContainer.id = `datatable${productType}`;
        container.appendChild(tableContainer);
        
        productTableContent.appendChild(container);
        // Append the ProductTable content to the tab content container
        tabContent.appendChild(productTableContent);
        
        document.getElementById('ratings-container').appendChild(tabContent);
    
        // Initialize MDB DataTable with dynamic columns and rows
        var datatableInstance = new mdb.Datatable(document.getElementById(`datatable${productType}`), {
            columns: columns,
            rows: rows,
            bordered: true,
            layout: {
              striped: true,
              responsive: true,
              pagination: true,
            }
        });
        // Attach search functionality
        document.getElementById(`datatable-search-input-${productType}`).addEventListener('input', function (e) {
            datatableInstance.search(e.target.value);
        });
    }

    createTableForProductType(productType, ratings) {
        if (ratings.length === 0) return;
    
        // Main container for the product type
        const productTypeContainer = document.createElement('div');
        productTypeContainer.className = 'product-type-container col-12 col-md-9 col-lg-6 mx-auto py-3';
    
        // Tab list for the product type
        const tabList = document.createElement('ul');
        tabList.className = 'nav nav-tabs nav-fill';
        tabList.id = `tabList-${productType}`;
        tabList.role = 'tablist';
    
        // Tab content container for the product type
        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.id = `tabContent-${productType}`;
    
        // Append the tab list and tab content container to the main container
        productTypeContainer.appendChild(tabList);
        productTypeContainer.appendChild(tabContent);
    
        // Append the main container to the ratings-container
        document.getElementById('ratings-container').appendChild(productTypeContainer);
    
        // Add the ProductTable tab and content
        this.addProductTableTab(productType, tabList, tabContent, ratings);
        this.createChartTab(productType, tabList, tabContent, ratings);
        this.createOverallScoreTab(productType, tabList, tabContent, ratings);
        // Optionally, add more tabs for charts related to the DataTable here
        // For example, addChartTab(productType, tabList, tabContent, 'Chart1', createChart1);
    }

    createChartTab(productType, tabList, tabContent, ratings) {
        const chartTab = document.createElement('li');
        chartTab.className = 'nav-item';
        const chartLink = document.createElement('a');
        chartLink.className = 'nav-link text-dark';
        chartLink.id = `chart-tab-${productType}`;
        chartLink.dataset.bsToggle = 'tab';
        chartLink.href = `#chart-${productType}`;
        chartLink.role = 'tab';
        chartLink.ariaControls = `chart-${productType}`;
        chartLink.ariaSelected = 'false';
        chartLink.innerText = `${productType} Charts`;
        chartTab.appendChild(chartLink);
    
        tabList.appendChild(chartTab);
    
        const chartContent = document.createElement('div');
        chartContent.className = 'tab-pane fade col-12 col-md-9 col-lg-6 mx-auto py-3';
        chartContent.id = `chart-${productType}`;
        chartContent.role = 'tabpanel';
        chartContent.ariaLabelledby = `chart-tab-${productType}`;
    
        // Create the canvas element for the chart
        const chartCanvas = document.createElement('canvas');
        chartCanvas.id = `chart-canvas-${productType}`;
        chartContent.appendChild(chartCanvas);
    
        tabContent.appendChild(chartContent);
    
        // Initialize the dropdown for strain-cultivator combinations
        const dropdown = this.createDropdown(productType, ratings, chartCanvas);
        chartContent.insertBefore(dropdown, chartCanvas);
    }

    createDropdown(productType, ratings, chartCanvas) {
        const selectContainer = document.createElement('div');
        selectContainer.className = 'chart-dropdown-container';
    
        const selectElement = document.createElement('select');
        selectElement.className = 'form-select';
        selectElement.id = `chart-dropdown-${productType}`;
    
        // Default dropdown option
        const defaultOption = document.createElement('option');
        defaultOption.selected = true;
        defaultOption.disabled = true;
        defaultOption.hidden = true;
        defaultOption.textContent = 'Select a Strain';
        selectElement.appendChild(defaultOption);
    
        // Populate dropdown options
        ratings.forEach(rating => {
            const option = document.createElement('option');
            option.value = `${rating.cultivator}-${rating.strain}`;
            option.textContent = `${rating.cultivator} - ${rating.strain}`;
            selectElement.appendChild(option);
        });
    
        selectContainer.appendChild(selectElement);
    
        // Event listener for dropdown selection
        selectElement.addEventListener('change', (event) => {
            const selectedCombination = event.target.value;
            this.updateChartForCombination(productType, selectedCombination, ratings, chartCanvas);
        });
    
        return selectContainer;
    }

    updateChartForCombination(productType, combination, ratings, chartCanvas) {
        const [selectedCultivator, selectedStrain] = combination.split('-');
        const ratingData = ratings.find(rating => rating.cultivator === selectedCultivator && rating.strain === selectedStrain);
    
        if (!ratingData) {
            console.error('No data found for selected combination');
            return;
        }
    
        // Prepare chart labels and data
        const labels = [];
        const data = [];
        const backgroundColors = [
            'rgba(63, 81, 181, 0.5)', 'rgba(77, 182, 172, 0.5)', 'rgba(66, 133, 244, 0.5)',
            'rgba(156, 39, 176, 0.5)', 'rgba(233, 30, 99, 0.5)', 'rgba(66, 73, 244, 0.4)',
            'rgba(66, 133, 244, 0.2)'
        ];
    
        Object.keys(ratingData).forEach((key, index) => {
            if (key.endsWith('_rating')) {
                const label = key.replace(/_/g, ' ').replace('rating', '').toUpperCase();
                labels.push(label);
                data.push(parseFloat(ratingData[key]));
            }
        });
    
        // Clear previous chart if it exists
        if (chartCanvas.chartInstance) {
            chartCanvas.chartInstance.dispose();
        }
    
        // Chart.js polar area chart configuration
        const polarAreaChartData = {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [{
                    label: `${selectedCultivator} - ${selectedStrain}`,
                    data: data,
                    backgroundColor: backgroundColors.slice(0, labels.length), // Match color count to label count
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0 // No decimal places
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        };
    
        // Instantiate the polar area chart
        chartCanvas.chartInstance = new mdb.Chart(chartCanvas, polarAreaChartData);
    }

    createOverallScoreTab(productType, tabList, tabContent, ratings) {
        const overallScoreTab = document.createElement('li');
        overallScoreTab.className = 'nav-item';
        const overallScoreLink = document.createElement('a');
        overallScoreLink.className = 'nav-link text-dark';
        overallScoreLink.id = `overall-score-tab-${productType}`;
        overallScoreLink.dataset.bsToggle = 'tab';
        overallScoreLink.href = `#overall-score-${productType}`;
        overallScoreLink.role = 'tab';
        overallScoreLink.ariaControls = `overall-score-${productType}`;
        overallScoreLink.ariaSelected = 'false';
        overallScoreLink.innerText = `${productType} Rankings`;
        overallScoreTab.appendChild(overallScoreLink);
    
        tabList.appendChild(overallScoreTab);
    
        const overallScoreContent = document.createElement('div');
        overallScoreContent.className = 'tab-pane fade col-12 col-md-9 col-lg-6 mx-auto py-3';
        overallScoreContent.id = `overall-score-${productType}`;
        overallScoreContent.role = 'tabpanel';
        overallScoreContent.ariaLabelledby = `overall-score-tab-${productType}`;
    
        // Create the canvas element for the overall score chart
        const overallScoreCanvas = document.createElement('canvas');
        overallScoreCanvas.id = `overall-score-canvas-${productType}`;
        overallScoreContent.appendChild(overallScoreCanvas);
    
        tabContent.appendChild(overallScoreContent);
    
        // After creating the tab and canvas, calculate scores and create the chart
        this.createOverallScoreChart(productType, ratings, overallScoreCanvas);
    }

    createOverallScoreChart(productType, ratings, chartCanvas) {
        const labels = [];
        const data = [];
        const tooltips = [];
        const backgroundColors = [
            'rgba(63, 81, 181, 0.5)', 'rgba(77, 182, 172, 0.5)', 'rgba(66, 133, 244, 0.5)',
            'rgba(156, 39, 176, 0.5)', 'rgba(233, 30, 99, 0.5)', 'rgba(66, 73, 244, 0.4)',
            'rgba(66, 133, 244, 0.2)'
        ];
        // Calculate overall scores for each strain
        ratings.forEach(rating => {
            const scoreValues = Object.keys(rating)
                .filter(key => key.endsWith('_rating'))
                .map(key => parseFloat(rating[key]) || 0);
            
            const overallScore = scoreValues.reduce((acc, curr) => acc + curr, 0) / scoreValues.length;
            
            labels.push(`${rating.strain}`);
            data.push(overallScore.toFixed(2));
            tooltips.push(`${rating.cultivator} - ${rating.strain}: ${overallScore.toFixed(2)}`);
        });
    
        // Bar chart configuration
        const dataBarCustomTooltip = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: `${productType} Rankings`,
                    data: data,
                    backgroundColor: data.map((_, i) => backgroundColors[i % backgroundColors.length]), // Cycle through the color array
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
        };
    
        // Options with custom tooltip
        const optionsBarCustomTooltip = {
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return tooltips[context.dataIndex];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };
    
        // Create the bar chart with custom tooltips
        new mdb.Chart(chartCanvas, dataBarCustomTooltip, optionsBarCustomTooltip);
    }

}

// Wait for the DOM to be fully loaded and for the Supabase client to be ready
$(document).ready(function() {
  window.addEventListener('supabaseClientReady', async function() {
    const userEmail = await window.supabaseClient.getCurrentUserEmail();
    if (userEmail) {
      new RatingsDatatable(userEmail); // Create a new instance of the RatingsDatatable class
    }
  });
});
