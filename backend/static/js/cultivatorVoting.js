class CultivatorVotingAPI {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async createCultivator(cultivator) {
        const response = await fetch(`${this.baseURL}/add_new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cultivator),
        });
        if (!response.ok) {
            throw new Error('Failed to create cultivator');
        }
        return await response.json();
    }

    async listVotes() {
        const response = await fetch(`${this.baseURL}/get_votes`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to get votes');
        }
        return await response.json();
    }

    async voteForCultivator(vote) {
        const response = await fetch(`${this.baseURL}/add_vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(vote),
        });
        if (!response.ok) {
            throw new Error('Failed to add vote');
        }
        return await response.json();
    }

    async deleteVote(encodedEmail, cultivatorId) {
        const response = await fetch(`${this.baseURL}/${encodedEmail}/${cultivatorId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to delete vote');
        }
        return true;
    }

    async listUniqueCultivators() {
        const response = await fetch(`${this.baseURL}/cultivators`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to get unique cultivators');
        }
        return await response.json();
    }
}

export default CultivatorVotingAPI;
