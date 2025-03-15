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
        const updatedData = { to_review: this.parseReviewedValue(toReview) };
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
            return;
        } catch (error) {
            console.error(`Error updating strain ${strainId}:`, error);
        }
    }
    async updateStrainReviewNotes(strainNotes) {
        const updatedData = { 
            "strain": strainNotes.strain,
            "cultivator": strainNotes.cultivator,
            "email": this.email,
            "to_review": strainNotes.to_review,
            "product_type": strainNotes.product_type,
            "strain_notes": strainNotes.strain_notes
        }    
        try {
            const response = await fetch(`/users/update_strain_notes/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedData)
            });
            if (!response.ok) {
                throw new Error(`Failed to update strain notes for ${strainNotes.strain}`);
            }
            return;
        } catch (error) {
            console.error(`Error updating notes for ${strainNotes.strain}:`, error);
        }
    }
    async deleteStrain(strainData) {
        try {
            const deleteData = {
                email: this.email,
                strain: strainData.strain,
                cultivator: strainData.cultivator,
                product_type: strainData.product_type,
                to_review: false
            }
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
        container.className = "text-start align-items-center";
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
            { label: 'Reviewed', field: 'to_review', sort: true , editable: false },
            { label: 'Type', field: 'product_type', sort: true, editable: false },
            { label: '', field: 'go_to_strain', sort: false, editable: false, width: 1 }
        ];
        let rows = this.userStrainsList.map((item, index) => ({
            strain: item.strain,
            cultivator: item.cultivator,
            to_review: `<input type="checkbox" class="form-check-input" ${this.parseReviewedValue(item.to_review) ? 'checked' : ''} data-strain-id="${item.id}">`,
            product_type: item.product_type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
            go_to_strain: `<td class="text-center" data-mdb-index="${index}">
                              <a id="goToStrain-${index}" data-mdb-index="${index}" class="btn btn-sm btn-info" 
                                 href="${this.getFormAction(item.product_type)}?strain_selected=${encodeURIComponent(item.strain)}&cultivator_selected=${encodeURIComponent(item.cultivator)}&product_type=${encodeURIComponent(item.product_type)}">
                                 <span class="text-dark">Go</span>
                              </a>
                           </td>`,
        }));
        const tableEditor = new TableEditor(container, {
            columns: columns,
            rows: rows,
          },
          { confirm: true, hover: true , striped: true, borderless: true, actionHeader: "Review/Remove", color: "bg-gray", actionPosition: "start" }
        );
        this.bindCheckboxListeners();
        container.addEventListener('delete.mdb.tableEditor', (event) => {
            const row = event.row;
            const strainData = { "strain": row.strain, "cultivator": row.cultivator, "product_type": row.product_type, "to_review": false };
            this.deleteStrain(strainData);
                })
        container.addEventListener('editorOpen.mdb.tableEditor', (event) => {
            event.preventDefault();
        });
    }
    bindCheckboxListeners() {
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
