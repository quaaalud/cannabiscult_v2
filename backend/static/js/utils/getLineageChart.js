class createLineageChart {
    constructor(lineage, strain, cultivator, urlPath) {
        this.lineageContainer = document.getElementById('lineageChart');
        this.lineage = lineage;
        this.strain = strain;
        this.cultivator = cultivator;
        this.urlPath = urlPath;
        this.chartInstance = null;
    }
    parseLineage(lineage) {
        if (!lineage || lineage === "Coming Soon") return ["Coming", "Soon"];
        return lineage.split(' X ').map(part => part.trim());
    }
    clearLineageChart() {
        if (this.lineageContainer) {
            this.lineageContainer.innerHTML = "";
        }
    }
    initLineageChart(cultivator, strain, urlPath, parentStrains) {
        if (!this.lineageContainer) return;
        const parentNodes = parentStrains.map(parent => ({
            label: "_",
            name: parent
        }));
        const chartData = {
            label: cultivator,
            name: strain,
            avatar: urlPath,
            children: parentNodes
        };
        this.clearLineageChart();
        this.chartInstance = new OrganizationChart(this.lineageContainer, {
            data: chartData
        });
    }
    renderLineageChart() {
        if (!this.lineageContainer) return;
        const parentStrains = this.parseLineage(this.lineage);
        this.initLineageChart(this.cultivator, this.strain, this.urlPath, parentStrains);
    }
    updateLineage(newLineage) {
        if (newLineage !== this.lineage) {
            this.lineage = newLineage;
            this.renderLineageChart();
        }
    }
}

export default createLineageChart;
