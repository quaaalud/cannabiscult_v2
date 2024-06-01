class createLineageChart {
  constructor(lineage, strain, cultivator, urlPath) {
    this.lineageContainer = document.getElementById('lineageChart');
    if (this.lineageContainer) {
      this.lineage = lineage;
      this.strain = strain;
      this.cultivator = cultivator;
      this.urlPath = urlPath;
    }
  }
  parseLineage(lineage) {
    if (!lineage) return [];
    return lineage.split(' X ').map(part => part.trim());
  } 
  initLineageChart(cultivator, strain, urlPath, parentStrains) {
    if (!this.lineageContainer) {
      return;
    }
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
    if (!this.lineageContainer) {
      return;
    }
    new OrganizationChart(this.lineageContainer, {
      data: chartData
    });
  }
  renderLineageChart() {
    const parentStrains = this.parseLineage(this.lineage);
    this.initLineageChart(this.cultivator, this.strain, this.urlPath, parentStrains);
  }
}

export default createLineageChart;