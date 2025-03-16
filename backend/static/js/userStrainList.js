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
        const response = await fetch('/users/my_strains/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        return response.ok ? await response.json() : [];
    }

    async deleteStrain(strainData) {
        try {
            const deleteData = {
                email: this.email,
                strain: strainData.strain,
                cultivator: strainData.cultivator,
                product_type: strainData.product_type,
                to_review: false
            };
            const response = await fetch('/users/delete_strain_from_list/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deleteData)
            });
            if (response.status !== 204) {
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
            case 'pre-roll': return '/pre-roll-get-review-form';
            case 'concentrate': return '/concentrate-get-review';
            default: return '/get-review';
        }
    }

    renderDataTable() {
        const container = document.getElementById('tableContent');
        container.classList.add("text-start");
        container.innerHTML = '';

        if (!this.userStrainsList.length) {
            container.innerHTML = '<h4 class="text-start mt-4">No strains found in your list. Search and add strains to your list to track products you wish to review.</h4>';
            return;
        }

        const columns = [
            { label: 'Type', field: 'product_type', sort: true },
            { label: 'Strain', field: 'strain', sort: true },
            { label: 'Cultivator', field: 'cultivator', sort: true },
            { label: 'Reviewed', field: 'to_review', sort: true },
            { label: '', field: 'actions', sort: false }
        ];

        const rows = this.userStrainsList.map((item, index) => ({
            actions: `
                <div class="row g-1">
                  <div class="col-6">
                    <a class="btn btn-sm btn-info go-btn w-100" data-index="${index}">Go</a>
                  </div>
                  <div class="col-6">
                    <button class="btn btn-sm btn-dark delete-btn w-100" data-index="${index}">Remove</button>
                  </div>
                </div>`,
            strain: item.strain,
            cultivator: item.cultivator,
            to_review: `<div class="container"><input type="checkbox" class="form-check-input" ${this.parseReviewedValue(item.to_review) ? 'checked' : ''} data-strain-id="${item.id}"></div>`,
            product_type: item.product_type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
        }));

        new mdb.Datatable(container, { columns, rows }, { hover: true, striped: true, borderless: true });

        this.attachEventListeners(container);
    }

    attachEventListeners(container) {
        container.onclick = (e) => {
            const goBtn = e.target.closest('.go-btn');
            const delBtn = e.target.closest('.delete-btn');

            if (goBtn) {
                const idx = goBtn.getAttribute('data-index');
                const row = this.userStrainsList[idx];
                window.location.href = `${this.getFormAction(row.product_type)}?strain_selected=${encodeURIComponent(row.strain)}&cultivator_selected=${encodeURIComponent(row.cultivator)}&product_type=${encodeURIComponent(row.product_type)}`;
            }

            if (delBtn) {
                const idx = delBtn.getAttribute('data-index');
                const row = this.userStrainsList[idx];
                const strainData = { strain: row.strain, cultivator: row.cultivator, product_type: row.product_type, to_review: false };
                this.deleteStrain(strainData).then(() => this.initialize()).catch(err => alert(err.message));
            }
        };

        this.bindCheckboxListeners();
    }

    bindCheckboxListeners() {
        document.querySelectorAll('input[type="checkbox"][data-strain-id]').forEach(checkbox => {
            checkbox.onchange = (event) => {
                const strainId = checkbox.dataset.strainId;
                const toReview = checkbox.checked;
                this.updateStrainReviewStatus(strainId, toReview);
            };
        });
    }

    async updateStrainReviewStatus(strainId, toReview) {
        const response = await fetch(`/users/update_strain_list/${strainId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to_review: this.parseReviewedValue(toReview) })
        });

        if (!response.ok) {
            throw new Error(`Failed to update strain status: ${await response.text()}`);
        }
    }
}

window.addEventListener('supabaseClientReady', async () => {
    const userEmail = await window.supabaseClient.getCurrentUserEmail();
    if (userEmail) new UserStrainList(userEmail).initialize();
});
