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
    async deleteStrain(strainData) {
        alert(strainData.product_type);
        try {
            const deleteData = {email: this.email, strain: strainData.strain, cultivator: strainData.cultivator, product_type: strainData.product_type, to_review: false }
            const response = await fetch(`/users/delete_strain_from_list/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deleteData)
            });
            if (response.status === 204) {
                return;
            } else {
                throw new Error('Failed to delete strain');
            }
        } catch (error) {
            console.error(`Error deleting strain ${strainData.strain}:`, error);
            alert(`Error deleting strain: ${error.message}`);
        }
    }
    parseReviewedValue(toReview) {
        return !toReview;
    }
    getFormAction(productType) {
        switch (productType.toLowerCase()) {
            case 'pre-roll':
                return '/pre-roll-get-review-form';
            case 'concentrate':
                return '/concentrate-get-review';
            default:
                return '/get-review';
        }
    }
    renderDataTable() {
        const container = document.getElementById('tableContent');
        container.innerHTML = ''; // Clear previous content

        if (this.userStrainsList.length === 0) {
            const message = document.createElement('h4');
            message.textContent = "No strains found in your list. Search and add strains to your list to track products you wish to review.";
            message.className = 'text-center mt-4';
            container.appendChild(message);
            return;
        }
        let columns = [
            { label: 'Strain', field: 'strain', sort: true, editable: false },
            { label: 'Cultivator', field: 'cultivator', sort: true, editable: false },
            { label: 'Reviewed', field: 'to_review', sort: true , inputType: 'checkbox', editable: false },
            { label: 'Type', field: 'product_type', sort: true, editable: false },
            { label: '', field: 'go_to_strain', sort: false, editable: false }
        ];
        let rows = this.userStrainsList.map(item => ({
            strain: item.strain,
            cultivator: item.cultivator,
            to_review: `<input type="checkbox" class="form-check-input" ${this.parseReviewedValue(item.to_review) ? 'checked' : ''} data-strain-id="${item.id}">`,
            product_type: item.product_type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
            go_to_strain: `<a class="btn btn-sm btn-info" href="${this.getFormAction(item.product_type)}?strain_selected=${encodeURIComponent(item.strain)}&cultivator_selected=${encodeURIComponent(item.cultivator)}&product_type=${encodeURIComponent(item.product_type)}"><span class="text-dark">Go</span></a>`,
        }));
        const tableEditor = new TableEditor(container, {
            columns: columns,
            rows: rows,
            bordered: true,
            layout: {
              striped: true,
              responsive: true,
              pagination: true
            }
          },
          { confirm: true, hover: true }
        );
        this.bindCheckboxListeners();
        container.addEventListener('delete.mdb.tableEditor', (e) => {
            const row = event.row; // Find the closest tr parent
            const strainData = { "strain": row.strain, "cultivator": row.cultivator, "product_type": row.product_type, "to_review": row.to_review };
            this.deleteStrain(strainData);
        })
        
    }
    bindCheckboxListeners() {
        // Ensure the DOM has been updated with the new HTML before attaching listeners
        setTimeout(() => {
            document.querySelectorAll('input[type="checkbox"][data-strain-id]').forEach(checkbox => {
                checkbox.addEventListener('change', event => {
                    const strainId = checkbox.dataset.strainId;
                    const toReview = checkbox.checked;
                    this.updateStrainReviewStatus(strainId, toReview);
                });
            });
        }, 50);
    }
}


window.addEventListener('supabaseClientReady', async function() {
  const userEmail = await window.supabaseClient.getCurrentUserEmail();
  if (userEmail) {
    const userList = new UserStrainList(userEmail);
    await userList.initialize();
  }
});
