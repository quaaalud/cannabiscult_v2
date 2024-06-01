class createLineageChart {
  constructor() {
    this.lineageContainer = document.getElementById('lineageChart');
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
      label: "",
      name: parent
    }));
  
    const chartData = {
      label: cultivator,
      name: strain,
      avatar: urlPath,
      children: parentNodes
    };
    new OrganizationChart(this.lineageContainer, {
      data: chartData
    });
  }
  renderLineageChart(lineage, strain, cultivator, urlPath) {
    const parentStrains = this.parseLineage(lineage);
    this.initLineageChart(cultivator, strain, urlPath, parentStrains);
  }
}

export default createLineageChart;