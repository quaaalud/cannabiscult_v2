class RatingsDatatable {
    constructor(userEmail) {
        this.userEmail = userEmail;
        this.init();
    }

    async init() {
        try {
            const ratingsByProductType = await this.fetchRatings(this.userEmail);
            for (const [productType, ratings] of Object.entries(ratingsByProductType)) {
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

    createTableForProductType(productType, ratings) {
        if (ratings.length === 0) return;
    
        const container = document.createElement('div');
        container.id = `container${productType}`;
        container.className = 'container-fluid py-3';
    
        const titleHTML = `<h3 class="text-dark pt-3 pb-2 text-center">${productType}</h3>`;
        container.innerHTML = titleHTML;
    
        const searchContainerHTML = `
            <div class="row">
                <div class="col-12 col-md-9 mx-auto">
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
    
        document.getElementById('ratings-container').appendChild(container);
    
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
