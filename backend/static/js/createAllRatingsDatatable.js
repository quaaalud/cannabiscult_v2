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
    async fetchImageUrl(productType, strain, cultivator) {
        const cacheKey = `${productType}-${strain}-${cultivator}`;
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
            const { url, timestamp } = JSON.parse(cachedData);
            const age = (Date.now() - timestamp) / 1000 / 60;
            if (age < 30) {
                return url;
            }
        }
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
            const imgUrl = data.img_url;
            localStorage.setItem(cacheKey, JSON.stringify({ url: imgUrl, timestamp: Date.now() }));
            return imgUrl;
        } catch (error) {
            const imgUrl = 'https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/public/cannabiscult/reviews/Connoisseur_Pack/CP_strains.webp';
            localStorage.setItem(cacheKey, JSON.stringify({ url: imgUrl, timestamp: Date.now() }));
            return imgUrl;
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
            }, 5000);
        });
    }
    getReviewLink(productType, strain, cultivator) {
        const formattedType = productType.toLowerCase();
        let formAction;
        switch (formattedType) {
            case 'pre-roll':
                formAction = '/pre-roll-get-review-form';
                break;
            case 'concentrate':
                formAction = '/concentrate-get-review';
                break;
            case 'edible':
                formAction = '/edible-get-review';
                break;
            default:
                formAction = '/get-review';
        }
        return `${formAction}?strain_selected=${encodeURIComponent(strain)}&cultivator_selected=${encodeURIComponent(cultivator)}`;
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
    async addProductTableTab(productType, tabList, tabContent, ratings) {
        const productTableTab = document.createElement('li');
        productTableTab.className = 'nav-item';
        const productTableLink = document.createElement('a');
        productTableLink.className = 'nav-link active text-dark';
        productTableLink.id = `productTable-tab-${productType}`;
        productTableLink.dataset.bsToggle = 'tab';
        productTableLink.href = `#productTable-${productType}`;
        productTableLink.role = 'tab';
        productTableLink.ariaControls = `productTable-${productType}`;
        productTableLink.ariaSelected = 'true';
        productTableLink.innerText = `${productType} Table`;
        productTableTab.appendChild(productTableLink);

        tabList.appendChild(productTableTab);

        const productTableContent = document.createElement('div');
        productTableContent.className = 'tab-pane fade show active';
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

        let columns = [
          { label: 'Strain', width: 150},
          { label: 'Cultivator', width: 150 }
        ];

        Object.keys(ratings[0]).filter(key => key.endsWith('_rating')).forEach(key => {
          const columnValues = ratings.map(rating => parseFloat(rating[key]));
          columns.push({
            label: key.replace(/_/g, ' ').replace('rating', '').trim().toUpperCase(),
            sort: true,
          });
        });
        columns.unshift({
          label: '',
          width: 125,
        });

        let rows = await Promise.all(ratings.map(async rating => {
          return Promise.all(columns.map(async col => {
            let key = col.label.toLowerCase().replace(/ /g, '_') + '_rating';
            if (col.label === '') {
              try {
                const imgUrl = await this.fetchImageUrl(productType, rating.strain, rating.cultivator);
                return `
                  <div id="lightbox${rating.strain}" class="lightbox" data-mdb-zoom-level="0.25" data-mdb-lightbox-init>
                    <img
                      src="${imgUrl}"
                      alt="${rating.strain} by ${rating.cultivator}"
                      style="width: 40px; max-height: 40px"
                      class="rounded-circle"
                      data-mdb-img="${imgUrl}"
                      loading="lazy"
                    />
                  </div>
                `;
              } catch (error) {
                console.error('Failed to load image URL:', error);
                return `
                  <div id="lightbox${rating.strain}" class="lightbox">
                    <img
                      src="https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/public/cannabiscult/reviews/Connoisseur_Pack/CP_strains.webp"
                      alt="Fallback Image"
                      style="width: 40px; max-height: 40px"
                      class="rounded-circle"
                    />
                  </div>
                `;
              }
            } else if (col.label === 'Strain') {
                const reviewUrl = this.getReviewLink(productType, rating.strain, rating.cultivator);
                return `
                    <a href="${reviewUrl}" target="_blank" class="text-decoration-none text-dark">
                        ${rating.strain}
                    </a>
                `;
            } else if (col.label === 'Cultivator') {
                const reviewUrl = this.getReviewLink(productType, rating.strain, rating.cultivator);
                return `
                    <a href="${reviewUrl}" target="_blank" class="text-decoration-none text-dark">
                        ${rating.cultivator}
                    </a>
                `;
            } else {
                return rating[key] || rating[col.label.toLowerCase()] || '-';
            }
          }));
        }));
        const tableContainer = document.createElement('div');
        tableContainer.id = `datatable${productType}`;
        container.appendChild(tableContainer);

        productTableContent.appendChild(container);
        tabContent.appendChild(productTableContent);
        document.getElementById(`body${productType}`).appendChild(tabContent);
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
        document.getElementById(`datatable-search-input-${productType}`).addEventListener('input', function (e) {
            datatableInstance.search(e.target.value);
        });
        this.initializeLightboxes();
    }
    initializeLightboxes() {
        const lightboxes = document.querySelectorAll('[id^="lightbox"]');
        lightboxes.forEach(lightbox => {
            mdb.Lightbox.getOrCreateInstance(lightbox);
        });
    }
    async populateImages(productType, ratings) {
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
    createTableForProductType(productType, ratings) {
        if (ratings.length === 0) return;

        const productTypeContainer = document.createElement('div');
        productTypeContainer.className = 'product-type-container col-12 col-md-9 col-lg-6 mx-auto py-3';

        const tabList = document.createElement('ul');
        tabList.className = 'nav nav-tabs nav-fill px-3';
        tabList.id = `tabList-${productType}`;
        tabList.role = 'tablist';

        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.id = `tabContent-${productType}`;

        productTypeContainer.appendChild(tabList);
        productTypeContainer.appendChild(tabContent);

        document.getElementById(`body${productType}`).appendChild(productTypeContainer);
        this.addProductTableTab(productType, tabList, tabContent, ratings);
        this.createChartTab(productType, tabList, tabContent, ratings);
        this.createOverallScoreTab(productType, tabList, tabContent, ratings);
        if (productType.toLowerCase() == "concentrate" || productType.toLowerCase() == "flower") {
          this.createTerpProfileTab(productType, tabList, tabContent);
        }
        this.initializeLightboxes();
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

        const chartCanvas = document.createElement('canvas');
        chartCanvas.id = `chart-canvas-${productType}`;
        chartContent.appendChild(chartCanvas);

        tabContent.appendChild(chartContent);

        const dropdown = this.createDropdown(productType, ratings, chartCanvas);
        chartContent.insertBefore(dropdown, chartCanvas);
    }

    createDropdown(productType, ratings, chartCanvas) {
        const selectContainer = document.createElement('div');
        selectContainer.className = 'chart-dropdown-container';

        const selectElement = document.createElement('select');
        selectElement.className = 'form-select';
        selectElement.id = `chart-dropdown-${productType}`;

        const defaultOption = document.createElement('option');
        defaultOption.selected = true;
        defaultOption.disabled = true;
        defaultOption.hidden = true;
        defaultOption.textContent = 'Select a Strain';
        selectElement.appendChild(defaultOption);

        ratings.forEach(rating => {
            const option = document.createElement('option');
            option.value = `${rating.cultivator}-${rating.strain}`;
            option.textContent = `${rating.cultivator} - ${rating.strain}`;
            selectElement.appendChild(option);
        });

        selectContainer.appendChild(selectElement);

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

        if (chartCanvas.chartInstance) {
            chartCanvas.chartInstance.dispose();
        }

        const polarAreaChartData = {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [{
                    label: `${selectedCultivator} - ${selectedStrain}`,
                    data: data,
                    backgroundColor: backgroundColors.slice(0, labels.length),
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        };

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

        const overallScoreCanvas = document.createElement('canvas');
        overallScoreCanvas.id = `overall-score-canvas-${productType}`;
        overallScoreContent.appendChild(overallScoreCanvas);

        tabContent.appendChild(overallScoreContent);

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
        ratings.forEach(rating => {
            const scoreValues = Object.keys(rating)
                .filter(key => key.endsWith('_rating'))
                .map(key => parseFloat(rating[key]) || 0);

            const overallScore = scoreValues.reduce((acc, curr) => acc + curr, 0) / scoreValues.length;

            labels.push(`${rating.strain}`);
            data.push(overallScore.toFixed(2));
            tooltips.push(`${rating.cultivator} - ${rating.strain}: ${overallScore.toFixed(2)}`);
        });

        const dataBarCustomTooltip = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: `${productType} Rankings`,
                    data: data,
                    backgroundColor: data.map((_, i) => backgroundColors[i % backgroundColors.length]),
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
        };

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
                indexAxis: 'y',
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                    }
                },
            }
        };

        new mdb.Chart(chartCanvas, dataBarCustomTooltip, optionsBarCustomTooltip);
    }
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

        const dropdown = this.createTerpDropdown(productType);
        const canvasContainer = document.createElement('div');
        canvasContainer.className = "col-12 col-sm-10 col-md-8 col-lg-6 mx-auto"
        const canvas = document.createElement('canvas');
        canvas.id = "";
        canvas.id = `terp-profile-chart-${productType}`;
        terpProfileContent.appendChild(dropdown);
        canvasContainer.appendChild(canvas);
        terpProfileContent.appendChild(canvasContainer);
        tabContent.appendChild(terpProfileContent);
        dropdown.addEventListener('change', async (event) => {
            const productId = event.target.value;
            this.createPolarChart(productType, productId, canvas);
        });
    }

    createTerpDropdown(productType) {
        const dropdown = document.createElement('select');
        dropdown.className = 'form-select';
        dropdown.id = `terp-profile-dropdown-${productType}`;
        this.populateStrainDropdown(productType, dropdown);
        return dropdown;
    }
    populateStrainDropdown(productType, dropdown) {
        const defaultOption = document.createElement('option');
        defaultOption.textContent = "Select a strain to see terps";
        defaultOption.value = "";
        defaultOption.selected = true;
        defaultOption.disabled = true;
        dropdown.appendChild(defaultOption);

        this.fetchStrains(productType)
            .then(strains => {
                strains.forEach(strain => {
                    if (strain.strain.includes("MOLUV") || strain.cultivator === "Connoisseur" || strain.cultivator === "Cultivar") {
                        return;
                    }
                    const option = document.createElement('option');
                    option.value = strain.product_id;
                    option.textContent = `${strain.strain} by ${strain.cultivator}`;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => {
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
            const data = await response.json();
            return data.terp_profile?.terp_values || null;
        } catch (error) {
            console.error('Error fetching terpene profile:', error);
            return null;
        }
    }
    async extractTerpeneData(terpeneProfile) {
        const labels = [];
        const values = [];
        const excludeKeys = new Set(["description_id", "product_id", "product_type"]);
        for (const [key, value] of Object.entries(terpeneProfile)) {
            if (!excludeKeys.has(key) && parseFloat(value) > 0) {
                labels.push(this.formatLabel(key));
                values.push(parseFloat(value));
            }
        }
        return { labels, values };
    }
    async createPolarChart(productType, productId, canvas) {
        if (canvas.chartInstance) {
            canvas.chartInstance.dispose();
        }

        const terpeneData = await this.fetchTerpeneProfile(productType, productId);
        if (!terpeneData) {
            console.error('No data available to create the chart.');
            return;
        }
        const data = await this.extractTerpeneData(terpeneData);
        canvas.chartInstance = new mdb.Chart(canvas, {
            type: 'polarArea',
            data: {
                labels: data.labels,
                datasets: [{
                    label: `${productType} Terpenes`,
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
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

$(document).ready(function() {
  new AllRatingsDatatable();
});
