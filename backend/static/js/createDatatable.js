import * from '../src/mdb.pro.umd.js';

async function fetchRatings(userEmail) {
    const response = await fetch(`/search/get_my_ratings?user_email=${encodeURIComponent(userEmail)}`);
    if (!response.ok) {
        throw new Error('Failed to fetch ratings');
    }
    return await response.json();
}

function formatRating(value) {
    return value ? parseFloat(value).toFixed(2) : 'N/A';
}

function createTableForProductType(productType, ratings) {

    if (ratings.length === 0) return;

    ratings.sort((a, b) => a.strain.localeCompare(b.strain));
    // Create a container for the table and title
    const tableContainer = document.createElement('div');
    tableContainer.setAttribute('data-mdb-datatable-init', 'true');
    tableContainer.className = 'table-container py-2';
    
    // Create the title element
    const title = document.createElement('h3');
    title.className = 'text-dark pt-5 pb-2 text-center';
    title.textContent = productType;
    tableContainer.appendChild(title);

    // Create the table and its headers
    const table = document.createElement('table');
    table.className = 'table table-responsive align-middle mb-0 bg-white';

    // Determine columns from the first rating entry
    const firstRating = ratings[0];
    const columns = ['strain', 'cultivator'].concat(Object.keys(firstRating).filter(key => key.endsWith('_rating')));

    // Create table headers
    const thead = document.createElement('thead');
    thead.className = 'bg-light';
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.replace(/_/g, ' ')
                             .replace('rating', '') // Remove the word "rating"
                             .trim() // Remove any leading/trailing whitespace
                             .toUpperCase(); // Convert to uppercase
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement('tbody');
    ratings.forEach(rating => {
        const row = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = col.endsWith('_rating') ? formatRating(rating[col]) : rating[col];
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    // Append the table to the container and the container to the ratings container
    tableContainer.appendChild(table);
    document.getElementById('ratings-container').appendChild(tableContainer);
}

async function populateRatingsTables(userEmail) {
    try {
        const ratingsByProductType = await fetchRatings(userEmail);
        
        for (const [productType, ratings] of Object.entries(ratingsByProductType)) {
            createTableForProductType(productType, ratings);
        }
    } catch (error) {
        console.error('Error populating ratings tables:', error);
    }
}

$(document).ready(async function() {
  window.addEventListener('supabaseClientReady', async function() {
    const userEmail = await window.supabaseClient.getCurrentUserEmail();
    if (!userEmail) {
      return;
    } else {
      await populateRatingsTables(userEmail);
    }
  });
});