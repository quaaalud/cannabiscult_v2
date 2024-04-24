class AllRatingsDatatable {
    constructor() {
        this.init();
    }
    async init() {
        try {
            const allRatings = await this.fetchAllRatings();
            const ratingsByProductType = this.groupRatingsByProductType(allRatings);
            this.setupAccordion(ratingsByProductType); 
            this.chartInstances = this.chartInstances || {};
            for (const [productType, ratings] of Object.entries(ratingsByProductType)) {
                ratings.sort((a, b) => a.strain.localeCompare(b.strain));
                this.createTableForProductType(productType, ratings);
            }
        } catch (error) {
            console.error('Error initializing ratings tables:', error);
        }
    }
    async fetchAllRatings() {
        try {
            // Start the aggregation task
            const startResponse = await fetch(`/search/get_aggregated_strain_ratings`);
            if (!startResponse.ok) {
                throw new Error('Failed to start ratings aggregation');
            }
            const startData = await startResponse.json();

            if (startData && startData.task_id) {
                return await this.waitForTaskCompletion(startData.task_id);
            } else {
                throw new Error('No task ID received to track aggregation');
            }
        } catch (error) {
            console.error('Failed to fetch aggregated ratings:', error);
            throw error;
        }
    }
    // Asynchronous function to fetch image URL
    async fetchImageUrl(productType, strain, cultivator) {
        try {
            const response = await fetch('/images/get-image-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_type: productType, strain: strain, cultivator: cultivator })
            });
            if (!response.ok) {
                throw new Error('Failed to fetch image URL');
            }
            const data = await response.json();
            return data.img_url;
        } catch (error) {
            return 'https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/sign/cannabiscult/reviews/Connoisseur_Pack/CP_strains.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjYW5uYWJpc2N1bHQvcmV2aWV3cy9Db25ub2lzc2V1cl9QYWNrL0NQX3N0cmFpbnMucG5nIiwiaWF0IjoxNzEzNzQ0Mzg4LCJleHAiOjE3NDUyODAzODh9.OHV1BzngWYDvhJE6h7ZJ8w2NeP7400g5jB06KoCjcl4&t=2024-04-22T00%3A06%3A28.960Z';
        }
    }
    async waitForTaskCompletion(taskId) {
        return new Promise((resolve, reject) => {
            const intervalId = setInterval(async () => {
                try {
                    const resultResponse = await fetch(`/search/get_task_result/${taskId}`);
                    if (!resultResponse.ok) {
                        throw new Error('Failed to get task result');
                    }
                    const resultData = await resultResponse.json();
                    if (resultData.status === 'completed') {
                        clearInterval(intervalId);
                        resolve(resultData.data);
                    } else if (resultData.status === 'failed') {
                        clearInterval(intervalId);
                        reject(new Error(resultData.error || 'Task failed without error message'));
                    }
                } catch (error) {
                    clearInterval(intervalId);
                    reject(error);
                }
            }, 5000); // Poll every 5 seconds
        });
    }
    groupRatingsByProductType(ratings) {
        return ratings.reduce((acc, rating) => {
            if (!acc[rating.product_type]) {
                acc[rating.product_type] = [];
            }
            acc[rating.product_type].push(rating);
            return acc;
        }, {});
    }
    setupAccordion(ratingsByProductType) {
        const accordionContainer = document.getElementById('ratingsAccordion') || document.createElement('div');
        accordionContainer.id = 'ratingsAccordion';
        accordionContainer.className = 'accordion';
        document.getElementById('ratings-container').appendChild(accordionContainer);
    
        for (const productType of Object.keys(ratingsByProductType)) {
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item';
    
            const header = document.createElement('h2');
            header.className = 'accordion-header';
            header.id = `heading${productType}`;
    
            const button = document.createElement('button');
            button.className = 'accordion-button collapsed';
            button.setAttribute('type', 'button');
            button.setAttribute('data-bs-toggle', 'collapse');
            button.setAttribute('data-bs-target', `#collapse${productType}`);
            button.setAttribute('aria-expanded', 'false');
            button.setAttribute('aria-controls', `collapse${productType}`);
            button.textContent = productType;
            header.appendChild(button);
    
            const collapseDiv = document.createElement('div');
            collapseDiv.id = `collapse${productType}`;
            collapseDiv.className = 'accordion-collapse collapse';
            collapseDiv.setAttribute('aria-labelledby', `heading${productType}`);
            collapseDiv.setAttribute('data-bs-parent', '#ratingsAccordion');
    
            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'accordion-body';
            bodyDiv.id = `body${productType}`;
    
            collapseDiv.appendChild(bodyDiv);
            accordionItem.appendChild(header);
            accordionItem.appendChild(collapseDiv);
            accordionContainer.appendChild(accordionItem);
        }
    }
    // Method to add a tab for each product type's table
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
        container.className = 'container-fluid pt-3';

        const searchContainerHTML = `
            <div class="row">
                <div class="col-12 col-md-9 col-lg-6 mx-auto">
                    <div class="form-outline mb-4" data-mdb-input-init="true">
                        <input type="text" class="form-control" id="datatable-search-input-${productType}">
                        <label class="form-label" for="datatable-search-input-${productType}">Search ${productType}</label>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML = searchContainerHTML;
    
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
        columns.unshift({
          label: '', // No label for image column
          width: 125, // Adjust width to fit the image
        });
    
        // Prepare rows data
        let rows = ratings.map(rating => {
          let row = columns.map(col => {
            let key = col.label.toLowerCase().replace(/ /g, '_') + '_rating';
            if (col.label === '') {
              // Wrap the placeholder image with lightbox attributes
              return `
                <div id="lightbox${rating.strain}" class="lightbox" data-mdb-zoom-level="0.25" data-mdb-lightbox-init>
                  <img 
                    src="https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/sign/cannabiscult/reviews/Connoisseur_Pack/CP_strains.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjYW5uYWJpc2N1bHQvcmV2aWV3cy9Db25ub2lzc2V1cl9QYWNrL0NQX3N0cmFpbnMucG5nIiwiaWF0IjoxNzEzNzQ0Mzg4LCJleHAiOjE3NDUyODAzODh9.OHV1BzngWYDvhJE6h7ZJ8w2NeP7400g5jB06KoCjcl4&t=2024-04-22T00%3A06%3A28.960Z"
                    alt="${rating.strain}"
                    style="width: 40px; max-height: 40px"
                    class="rounded-circle"
                    data-mdb-img="https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/sign/cannabiscult/reviews/Connoisseur_Pack/CP_strains.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjYW5uYWJpc2N1bHQvcmV2aWV3cy9Db25ub2lzc2V1cl9QYWNrL0NQX3N0cmFpbnMucG5nIiwiaWF0IjoxNzEzNzQ0Mzg4LCJleHAiOjE3NDUyODAzODh9.OHV1BzngWYDvhJE6h7ZJ8w2NeP7400g5jB06KoCjcl4&t=2024-04-22T00%3A06%3A28.960Z"
                  />
                </div>
              `;
            } else {
              return rating[key] || rating[col.label.toLowerCase()];
            }
          });
          return row;
        });
    
        // Create a table container
        const tableContainer = document.createElement('div');
        tableContainer.id = `datatable${productType}`;
        container.appendChild(tableContainer);
        
        productTableContent.appendChild(container);
        // Append the ProductTable content to the tab content container
        tabContent.appendChild(productTableContent);
        document.getElementById(`body${productType}`).appendChild(tabContent);
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
        ratings.forEach((rating, index) => {
          this.fetchImageUrl(productType, rating.strain, rating.cultivator).then(imgUrl => {
            const imgElements = document.querySelectorAll(`#datatable${productType} img[data-mdb-img]`);
            if (imgElements[index]) {
              imgElements[index].src = imgUrl;
              imgElements[index].setAttribute('data-mdb-img', imgUrl);
              imgElements[index].alt = `${rating.strain} by ${rating.cultivator} primary image for the Cannabis Cult.`;
            }
          });
          let lightbox = document.getElementById(`lightbox${rating.strain}`);
          let instance = mdb.Lightbox.getOrCreateInstance(lightbox);
        });
    }
    // Method to create data tables for ratings
    createTableForProductType(productType, ratings) {
        if (ratings.length === 0) return;
    
        // Main container for the product type
        const productTypeContainer = document.createElement('div');
        productTypeContainer.className = 'product-type-container col-12 col-md-9 col-lg-6 mx-auto py-3';
    
        // Tab list for the product type
        const tabList = document.createElement('ul');
        tabList.className = 'nav nav-tabs nav-fill px-3';
        tabList.id = `tabList-${productType}`;
        tabList.role = 'tablist';
    
        // Tab content container for the product type
        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.id = `tabContent-${productType}`;
    
        // Append the tab list and tab content container to the main container
        productTypeContainer.appendChild(tabList);
        productTypeContainer.appendChild(tabContent);
    
        // Append the main container to the accordian-container
        document.getElementById(`body${productType}`).appendChild(productTypeContainer);
        // Add the ProductTable tab and content
        this.addProductTableTab(productType, tabList, tabContent, ratings);
        this.createChartTab(productType, tabList, tabContent, ratings);
        this.createOverallScoreTab(productType, tabList, tabContent, ratings);
        this.createTerpProfileTab(productType, tabList, tabContent);
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
                indexAxis: 'y', // This makes the bar chart horizontal
                scales: {
                    x: {
                        stacked: true, // Optional: for stacked bar chart
                        // Configure your x-axis options here
                    },
                    y: {
                        // Configure your y-axis options here
                        stacked: true, // Optional: for stacked bar chart
                    }
                },
            }
        };
    
        // Create the bar chart with custom tooltips
        new mdb.Chart(chartCanvas, dataBarCustomTooltip, optionsBarCustomTooltip);
    }
    // Helper method to format column labels nicely
    formatLabel(key) {
        if (key === 'strain') return 'Strain';
        if (key === 'cultivator') return 'Cultivator';
        return key.split('_').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
    }
    formatRating(value) {
        return value ? parseFloat(value).toFixed(2) : 'N/A';
    }
    createTerpProfileTab(productType, tabList, tabContent) {
        const tab = document.createElement('li');
        tab.className = 'nav-item';
        
        const link = document.createElement('a');
        link.className = 'nav-link text-dark';
        link.id = `terp-profile-tab-${productType}`;
        link.dataset.bsToggle = 'tab';
        link.href = `#terp-profile-${productType}`;
        link.role = 'tab';
        link.ariaControls = `terp-profile-${productType}`;
        link.innerText = 'Terp Profile';
        
        tab.appendChild(link);
        tabList.appendChild(tab);
        
        const terpProfileContent = document.createElement('div');
        terpProfileContent.className = 'tab-pane fade';
        terpProfileContent.id = `terp-profile-${productType}`;
        terpProfileContent.role = 'tabpanel';
        terpProfileContent.ariaLabelledby = `terp-profile-tab-${productType}`;
    
        // Create dropdown and chart canvas
        const dropdown = this.createTerpDropdown(productType);
        const canvas = document.createElement('canvas');
        canvas.id = `terp-profile-chart-${productType}`;
    
        terpProfileContent.appendChild(dropdown);
        terpProfileContent.appendChild(canvas);
        tabContent.appendChild(terpProfileContent);
    
        // Initialize an empty property to store chart instances if not already initialized
        this.chartInstances = this.chartInstances || {};
    
        // Add event listener to dropdown to update chart on change
        dropdown.addEventListener('change', async (event) => {
            const productId = event.target.value;
            this.createPolarChart(productType, productId, canvas);
        });
    } 
    createTerpDropdown(productType) {
        const dropdown = document.createElement('select');
        dropdown.className = 'form-select';
        dropdown.id = `terp-profile-dropdown-${productType}`;
        this.populateStrainDropdown(productType, dropdown); // Assume this function populates the dropdown
        return dropdown;
    }
    
    populateStrainDropdown(productType, dropdown) {
        // Fetch strains and populate dropdown, assume fetchStrains is implemented
        this.fetchStrains(productType).then(strains => {
            strains.forEach(strain => {
                const option = document.createElement('option');
                option.value = strain.product_id;
                option.textContent = strain.strain;
                dropdown.appendChild(option);
            });
        }).catch(error => {
            console.error('Error populating strains:', error);
        });
    }
    
    async fetchStrains(productType) {
        const response = await fetch(`/search/strains/${productType.toLowerCase()}`);
        if (!response.ok) throw new Error('Failed to fetch strains');
        return await response.json();
    }
    async fetchTerpeneProfile(productType, productId) {
        const url = `/search/terps/${productType}/${productId}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching terpene profile:', error);
            return null; // Return null or handle the error as you see fit
        }
    }
    extractTerpeneData(terpeneProfile) {
        const labels = [];
        const values = [];

        // Assuming terpeneProfile has a consistent structure with keys for terpenes
        for (const [key, value] of Object.entries(terpeneProfile)) {
            if (key.startsWith("alpha_") || key.startsWith("beta_") || key.startsWith("delta_") || key.startsWith("gamma_") || key.startsWith("trans_")) {
                labels.push(this.formatLabel(key));
                values.push(parseFloat(value));
            }
        }

        return { labels, values };
    }
    
    createPolarChart(productType, productId, canvas) {
        const terpeneData = this.fetchTerpeneProfile(productType, productId);
        if (!terpeneData) {
            console.error('No data available to create the chart.');
            return;
        }
    
        // Check if there's an existing chart instance and destroy it
        if (this.chartInstances[canvas.id]) {
            this.chartInstances[canvas.id].destroy();
        }
    
        const data = this.extractTerpeneData(terpeneData);
        const ctx = canvas.getContext('2d'); // Get the rendering context
    
        // Create a new chart instance and store it
        this.chartInstances[canvas.id] = new mdb.Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        'rgba(63, 81, 181, 0.5)', 'rgba(77, 182, 172, 0.5)', 'rgba(66, 133, 244, 0.5)',
                        'rgba(156, 39, 176, 0.5)', 'rgba(233, 30, 99, 0.5)', 'rgba(66, 73, 244, 0.4)',
                        'rgba(66, 133, 244, 0.2)'
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }


}

// Wait for the DOM to be fully loaded and for the Supabase client to be ready
$(document).ready(function() {
  new AllRatingsDatatable(); // Create a new instance of the RatingsDatatable class
});
