import initTerpeneChart from "./generateTerpeneChart.js";
import createLineageChart from "./getLineageChart.js";

function updateDisplayedDescription(description, strain, cultivator, urlPath) {
    document.getElementById("description_text").textContent = description.description_text || "Coming Soon";
    document.getElementById("effects_text").textContent = description.effects || "Coming Soon";
    document.getElementById("lineage_text").textContent = description.lineage || "Coming Soon";

    const terpeneDiv = document.getElementById("terpene_text");
    terpeneDiv.innerHTML = ""; 

    if (description.terpenes_list && description.terpenes_list.length) {
        const dataValues = description.terpenes_list.map(() => 1);
        initTerpeneChart(description.terpenes_list, dataValues);
    } else {
        terpeneDiv.innerHTML = "<p>Coming Soon</p>";
    }
    populateLineageChartIfExists(description.lineage, strain, cultivator, urlPath)
}
function populateLineageChartIfExists(lineageStr, strain, cultivator, urlPath) {
    const lineage = lineageStr.trim();
    if (!lineage || lineage.toLowerCase() === 'none' || lineage.toLowerCase() === 'null') {
        return;
    }
    if (cultivator && strain && urlPath) {
        const lineageChart = new createLineageChart(lineage, strain, cultivator, urlPath);
        lineageChart.renderLineageChart();
    }
}
export default function populateDescriptionSelect(descriptions, strain, cultivator, urlPath) {
    const selectElement = document.getElementById("descriptionSelect");
    selectElement.innerHTML = "";
    descriptions.forEach((desc) => {
        const option = document.createElement("option");
        option.value = desc.description_id;
        option.textContent = `${desc.username}`;
        selectElement.appendChild(option);
    });
    const selectInstance = mdb.Select.getInstance(selectElement);
    selectElement.addEventListener("change", function () {
        const selectedDescription = descriptions.find(d => d.description_id == this.value);
        if (selectedDescription) {
            updateDisplayedDescription(selectedDescription, strain, cultivator, urlPath);
        }
    });
    if (descriptions.length > 0) {
        selectElement.value = descriptions[0].description_id;
        updateDisplayedDescription(descriptions[0], strain, cultivator, urlPath);
    }
}
