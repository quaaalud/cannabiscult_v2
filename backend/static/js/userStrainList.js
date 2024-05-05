export class UserStrainList {
    constructor(email) {
        this.email = email;
        this.userStrainsList = [];
    }

    async initialize() {
        try {
            this.userStrainsList = await this.fetchUserStrains(this.email);
            this.renderDataTable();
        } catch (error) {
            console.error("Failed to load user list:", error);
            throw error;
        }
    }

    async fetchUserStrains(email) {
        try {
            const response = await fetch('/users/my_strains/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({email: email})
            });
            if (!response.ok) {
                throw new Error('Failed to fetch strains');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching strains:', error);
            return [];
        }
    }
    async updateStrainReviewStatus(strainId, toReview) {
        const updatedData = { to_review: this.parseReviewedValue(toReview) }; // Invert the value for server side logic
        try {
            const response = await fetch(`/users/update_strain_list/${strainId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedData)
            });
            if (!response.ok) {
                throw new Error(`Failed to update strain with ID ${strainId}`);
            }
            console.log(`Strain ${strainId} review status updated to ${!toReview}`);
        } catch (error) {
            console.error(`Error updating strain ${strainId}:`, error);
        }
    }
    parseReviewedValue(toReview) {
        return !toReview;
    }
    renderDataTable() {
        if (this.userStrainsList.length === 0) {
            console.log("No strains to display.");
            return;
        }

        let columns = [
            { label: 'Type', key: 'product_type' },
            { label: 'Strain', key: 'strain' },
            { label: 'Cultivator', key: 'cultivator' },
            { label: 'Reviewed', key: 'to_review' }
        ];

        let table = document.createElement('table');
        table.className = 'table table-striped';

        // Create header row
        let thead = table.createTHead();
        let headerRow = thead.insertRow();
        columns.forEach(col => {
            let th = document.createElement('th');
            th.textContent = col.label.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            headerRow.appendChild(th);
        });

        // Create body rows
        let tbody = table.createTBody();
        this.userStrainsList.forEach(item => {
            let row = tbody.insertRow();
            columns.forEach(col => {
                let cell = row.insertCell();
                if (col.key === 'to_review') {
                    let checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.checked = this.parseReviewedValue(item[col.key]);
                    checkbox.dataset.strainId = item.id;
                    checkbox.addEventListener('change', (event) => {
                        this.updateStrainReviewStatus(item.id, event.target.checked);
                    });
                    cell.appendChild(checkbox);
                } else {
                    if (col.key === 'product_type') {
                        cell.textContent = item[col.key].split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                    } else {
                        cell.textContent = item[col.key];
                    }
                }
            });
        });

        // Append the table to a container in the DOM
        document.getElementById('data-table-container').appendChild(table);
    }
}


window.addEventListener('supabaseClientReady', async function() {
  const userEmail = await window.supabaseClient.getCurrentUserEmail();
  if (userEmail) {
    const userList = new UserStrainList(userEmail);
    await userList.initialize();
  }
});
