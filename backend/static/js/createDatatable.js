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

        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-container py-2';

        const title = document.createElement('h3');
        title.className = 'text-dark pt-5 pb-2 text-center';
        title.textContent = productType;
        tableContainer.appendChild(title);

        const table = document.createElement('table');
        table.className = 'display';
        table.style.width = '100%';

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

        tableContainer.appendChild(table);
        document.getElementById('ratings-container').appendChild(tableContainer);

        // Initialize DataTables on the created table
        var createdTable = $(table).DataTable({
            searching: true // Enable the search functionality
        });
        $('.dataTables_filter').closest('.row').addClass('row');
        $('.dataTables_length').closest('.row').addClass('row');
        var searchInput = $('div.dataTables_filter');
        var lengthSelect = $('div.dataTables_length');
        searchInput.className = "w-100 form-control";
        $('.dataTables_length').closest('.row').addClass('justify-content-start');
        $('.dataTables_filter').closest('.row').addClass('justify-content-start');
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
