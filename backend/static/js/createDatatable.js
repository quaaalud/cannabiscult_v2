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

        const searchContainer = document.createElement('div');
        searchContainer.setAttribute('data-mdb-input-init', 'true');
        searchContainer.className = 'form-outline mb-4';
        // Create the search input element
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control';
        searchInput.id = `datatable-search-input-${productType}`; // Unique ID for each product type

        // Create the search input label
        const searchLabel = document.createElement('label');
        searchLabel.className = 'form-label';
        searchLabel.setAttribute('for', searchInput.id);
        searchLabel.textContent = 'Search';

        // Append input and label to the search container
        searchContainer.appendChild(searchInput);
        searchContainer.appendChild(searchLabel);

        const title = document.createElement('h3');
        title.className = 'text-dark pt-3 pb-2 text-center';
        title.textContent = productType;
        

        const table = document.createElement('table');
        table.className = 'table table-striped py-3'; // Add Bootstrap table classes
        table.setAttribute('data-mdb-datatable', 'true');
        table.setAttribute('data-mdb-width', '100')
        table.setAttribute('data-mdb-pagination', 'false')
        const columns = ['strain', 'cultivator'].concat(Object.keys(ratings[0]).filter(key => key.endsWith('_rating')));
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.replace(/_/g, ' ').replace('rating', '').trim().toUpperCase();
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        ratings.forEach(rating => {
            const row = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                td.textContent = col.endsWith('_rating') ? this.formatRating(rating[col]) : rating[col];
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        document.getElementById('ratings-container').appendChild(title);
        document.getElementById('ratings-container').appendChild(searchContainer);
        document.getElementById('ratings-container').appendChild(table);
        
        const mdbTable = new mdb.Datatable(table, {
            responsive: true,
            layout: {
              topStart: null
          }
        });
        searchInput.addEventListener('input', (e) => {
          mdbTable.search(e.target.value);
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
