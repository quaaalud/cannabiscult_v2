import initTerpeneChart from "./generateTerpeneChart.js";
import createLineageChart from "./getLineageChart.js";

const formatRating = (rating) => {
    return rating !== null ? parseFloat(rating).toFixed(2) : '?';
};

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
export function populateDescriptionSelect(descriptions, strain, cultivator, urlPath) {
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

async function fetchFlowerDescriptions(flowerId, strain, cultivator, urlPath) {
    if (!flowerId) {
        console.error("Flower ID not found!");
        return;
    }
    try {
        const response = await fetch(`/flowers/all_descriptions?flower_id=${flowerId}`);
        if (!response.ok) throw new Error("Failed to fetch descriptions");
        const descriptions = await response.json();
        populateDescriptionSelect(descriptions, strain, cultivator, urlPath);
    } catch (error) {
        console.error("Error fetching flower descriptions:", error);
    }
}

function fetchAndUpdateFlowerRankings(flowerId) {
    let endpoint = `/flowers/get_strain_ratings_by_id/${flowerId}/`;
    fetch(endpoint)
    .then(response => response.json())
    .then(data => {
        if (!data.message) {
            const formatRating = (rating) => {
                return rating !== null ? parseFloat(rating).toFixed(2) : '?';
            };
            document.getElementById('flavor_rating_value').innerText = formatRating(data.flavor_rating);
            document.getElementById('overall_rating_value').innerText = formatRating(data.overall_score);
            document.getElementById('effects_rating_value').innerText = formatRating(data.effects_rating);
            document.getElementById('appearance_rating_value').innerText = formatRating(data.appearance_rating);
            document.getElementById('smell_rating_value').innerText = formatRating(data.smell_rating);
            document.getElementById('harshess_rating_value').innerText = formatRating(data.harshness_rating);
            document.getElementById('freshness_rating_value').innerText = formatRating(data.freshness_rating);
        } else {
            console.error('Error fetching data:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

export async function fetchConcentrateDescriptions(concentrateId, strain, cultivator, urlPath) {
    if (!concentrateId) {
        console.error("Concentrate ID not found!");
        return;
    }
    try {
        const response = await fetch(`/concentrates/all_descriptions?concentrate_id=${concentrateId}`);
        if (!response.ok) throw new Error("Failed to fetch descriptions");
        const descriptions = await response.json();
        populateDescriptionSelect(descriptions, strain, cultivator, urlPath);
    } catch (error) {
        console.error("Error fetching concentrate descriptions:", error);
    }
}

export async function fetchAndUpdateConcentrateRankings(concentrateId) {
  const endpoint = `/concentrates/get_concentrate_ratings_by_id/${concentrateId}`;
  try {
      const response = await fetch(endpoint);
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const ratingsData = await response.json();
      if (ratingsData.message) { return; };
      document.getElementById('flavor_rating_value').textContent = formatRating(ratingsData.flavor_rating);
      document.getElementById('overall_rating_value').textContent = formatRating(ratingsData.overall_score);
      document.getElementById('effects_rating_value').textContent = formatRating(ratingsData.effects_rating);
      document.getElementById('harshness_rating_value').textContent = formatRating(ratingsData.harshness_rating);
      document.getElementById('color_rating_value').textContent = formatRating(ratingsData.color_rating);
      document.getElementById('smell_rating_value').textContent = formatRating(ratingsData.smell_rating);
      document.getElementById('consistency_rating_value').textContent = formatRating(ratingsData.consistency_rating);
    } catch (error) {
      console.error('Error:', error);
    }
}


export async function fetchPreRollDescriptions(preRollId, strain, cultivator, urlPath) {
    if (!preRollId) {
        console.error("Pre-Roll ID not found!");
        return;
    }
    try {
        const response = await fetch(`/prerolls/all_descriptions?preroll_id=${preRollId}`);
        if (!response.ok) throw new Error("Failed to fetch descriptions");
        const descriptions = await response.json();
        populateDescriptionSelect(descriptions, strain, cultivator, urlPath);
    } catch (error) {
        console.error("Error fetching pre-roll descriptions:", error);
    }
}


export async function fetchAndUpdatePreRollStrainRankings(pre_rollId) {
  var endpoint = `/prerolls/get_pre_roll_rating_by_id/${parseInt(pre_rollId)}`;
  fetch(endpoint)
  .then(response => response.json())
  .then(data => {
      if (!data.message) {
          document.getElementById('flavor_rating_value').innerText = formatRating(data.flavor_rating);
          document.getElementById('overall_rating_value').innerText = formatRating(data.overall_score);
          document.getElementById('effects_rating_value').innerText = formatRating(data.effects_rating);
          document.getElementById('roll_rating_value').innerText = formatRating(data.roll_rating);
          document.getElementById('airflow_rating_value').innerText = formatRating(data.airflow_rating);
          document.getElementById('burn_rating_value').innerText = formatRating(data.burn_rating);
          document.getElementById('ease_to_light_rating_value').innerText = formatRating(data.ease_to_light_rating);
      } else {
          console.error('Error fetching data:', data.error);
      }
  })
  .catch(error => console.error('Error:', error));
}
