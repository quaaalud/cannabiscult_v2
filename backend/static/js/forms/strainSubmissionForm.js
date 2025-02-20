let fieldsCompletedWatched = false;
let lineageContainer

function createChip() {
    if (window.lineageList.length === 0) {
      lineageContainer = document.getElementById('lineageChipsContainer');
      lineageContainer.innerHTML = ""
    }
    const input = document.getElementById('lineageInput');
    const value = input.value.trim();
    if (value) {
      const chipContainer = document.createElement('div');
      chipContainer.className = 'col-6';
      const chip = document.createElement('div');
      chip.className = 'chip chip-outline btn-outline-dark';
      chip.setAttribute('data-mdb-chip-init', '');
      chip.setAttribute('data-mdb-ripple-color', 'dark');
      chip.textContent = value;
      chip.id = value;
      chip.value = value;
      const closeIcon = document.createElement('i');
      closeIcon.className = 'close fas fa-times';
      closeIcon.addEventListener('click', function() {
        chipContainer.remove();
        const index = window.lineageList.indexOf(value);
        if (index > -1) {
          window.lineageList.splice(index, 1);
        }
      });
      chip.appendChild(closeIcon);
      chipContainer.appendChild(chip);
      document.getElementById('lineageChipsContainer').appendChild(chipContainer);
      window.lineageList.push(value);
      input.value = '';
    }
}

function getNewlyCreatedStrain(strain, cultivator, cultivar_email) {
    const productTypeElements = document.getElementsByName("inlineRadioOptions");
    for (const ptElement of productTypeElements) {
        if (ptElement.checked) {
            let reviewUrl;
            switch(ptElement.value) {
                case "flowerSubmission":
                    reviewUrl = `/get-review?strain_selected=${strain}&cultivator_selected=${cultivator}&cultivar_email=${cultivar_email}`;
                    break;
                case "concentrateSubmission":
                    reviewUrl = `/concentrate-get-review?strain_selected=${strain}&cultivator_selected=${cultivator}&cultivar_email=${cultivar_email}`;
                    break;
                case "pre_rollSubmission":
                    reviewUrl = `/pre-roll-get-review?strain_selected=${strain}&cultivator_selected=${cultivator}&cultivar_email=${cultivar_email}`;
                    break;
                case "edibleSubmission":
                    reviewUrl = `/edible-get-review?strain_selected=${strain}&cultivator_selected=${cultivator}&cultivar_email=${cultivar_email}`;
                    break;
                default:
                    console.error("Unknown product type:", ptElement.value);
                    return;
            }
            window.location.href = reviewUrl;
            break;
        }
    }
}

function getMissingFieldNames() {
    const missing = [];
    const productTypeElements = document.getElementsByName("inlineRadioOptions");
    let productTypeValid = false;
    for (const elem of productTypeElements) {
        if (elem.checked) {
            productTypeValid = true;
            break;
        }
    }
    if (!productTypeValid) {
        missing.push("Product Type");
    }
    const requiredFields = [
        { id: "strainSubmission", name: "Strain Name" },
        { id: "cultivatorSubmission", name: "Cultivator" },
        { id: "strainCategorySubmission", name: "Strain Category" },
        { id: "emailAddress", name: "Email Address" },
        { id: "strainDescription", name: "Description" },
        { id: "effectsSubmission", name: "Effects" },
        { id: "terpenesSubmission", name: "Terpenes" }
    ];
    requiredFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (!element) {
            missing.push(field.name);
        } else {
            if (field.id === "terpenesSubmission") {
                const selectedOptions = Array.from(element.selectedOptions);
                if (selectedOptions.length === 0) {
                    missing.push(field.name);
                }
            } else {
                if (element.value.trim() === "") {
                    missing.push(field.name);
                }
            }
        }
    });
    if (!window.lineageList || window.lineageList.length === 0) {
        missing.push("Missing Lineage");
    }
    return missing;
}

function updateSubmitButtonState() {
    const form = document.getElementById("strainSubmissionForm");
    const submitButton = form.querySelector('button[type="submit"]');
    const missingFields = getMissingFieldNames();
    submitButton.disabled = missingFields.length > 0;
    return missingFields;
}

function setupSubmitButtonFieldWatcher() {
    if (fieldsCompletedWatched) {
        return;
    }
    const requiredFieldIds = [
        "strainSubmission",
        "cultivatorSubmission",
        "strainCategorySubmission",
        "emailAddress",
        "strainDescription",
        "effectsSubmission",
        "terpenesSubmission"
    ];
    requiredFieldIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.removeEventListener('input', updateSubmitButtonState);
            element.removeEventListener('change', updateSubmitButtonState);
            element.addEventListener('input', updateSubmitButtonState);
            element.addEventListener('change', updateSubmitButtonState);
        }
    });
    const productTypeElements = document.getElementsByName("inlineRadioOptions");
    productTypeElements.forEach(elem => {
        elem.removeEventListener('change', updateSubmitButtonState);
        elem.addEventListener('change', updateSubmitButtonState);
    });
    fieldsCompletedWatched = true;
}

async function submitStrainForm(event) {
  event.preventDefault();
  const form = document.getElementById("strainSubmissionForm");
  const modalBody = document.querySelector('#missingInfoModal .modal-body');
  // 1) Check for missing fields
  const missingFields = getMissingFieldNames();
  if (missingFields.length > 0) {
    modalBody.innerHTML = `<p>Please complete the following fields:</p>
                           <ul>${missingFields.map(field => `<li>${field}</li>`).join('')}</ul>`;
    const missingInfoModal = new bootstrap.Modal(document.getElementById('missingInfoModal'));
    missingInfoModal.show();
    setupSubmitButtonFieldWatcher();
    return;
  }
  const terpenesElement = document.getElementById("terpenesSubmission");
  const selectedTerpenes = Array.from(terpenesElement.selectedOptions).map(opt => opt.value);
  if (selectedTerpenes.length > 0) {
    showTerpenePercentageModal(selectedTerpenes);
    return;
  }
  await finalizeStrainSubmission();
}


function showTerpenePercentageModal(selectedTerpenes) {
  const terpeneInputsContainer = document.getElementById('terpeneInputsContainer');
  terpeneInputsContainer.innerHTML = '';
  selectedTerpenes.forEach(terp => {
    const terpeneInputCol = document.createElement('div');
    terpeneInputCol.className = 'col-sm-6 col-md-4 mb-3';
    terpeneInputCol.innerHTML = `
      <label class="form-label" for="terpInput_${terp}">${terp}</label>
      <input
        type="number"
        step="0.01"
        min="0.01"
        max="99.99"
        class="form-control terp-percent-input"
        id="terpInput_${terp}"
        data-terpene="${terp}"
        placeholder="Enter %"
        required
      />
    `;
    terpeneInputsContainer.appendChild(terpeneInputCol);
  });
  const terpenePercentModal = new bootstrap.Modal(document.getElementById('terpenePercentModal'));
  terpenePercentModal.show();
}

async function finalizeStrainSubmission() {
  const strainValue = document.getElementById("strainSubmission").value.trim();
  const cultivatorValue = document.getElementById("cultivatorSubmission").value.trim();
  const strainCategoryValue = document.getElementById("strainCategorySubmission").value.trim();
  const emailAddressValue = document.getElementById("emailAddress").value.trim();
  const descriptionValue = document.getElementById("strainDescription").value.trim();
  const effectsValue = document.getElementById("effectsSubmission").value.trim();
  const lineageValues = window.lineageList || [];
  const terpenesElement = document.getElementById("terpenesSubmission");
  const selectedTerpenes = Array.from(terpenesElement.selectedOptions).map(option => option.value);
  const productTypeElements = document.getElementsByName("inlineRadioOptions");
  let productTypeValue = '';
  for (const ptElement of productTypeElements) {
    if (ptElement.checked) {
      productTypeValue = ptElement.value;
      break;
    }
  }
  const cleanCultivatorString = window.supabaseClient.sanitizeInputString(cultivatorValue);
  const cleanStrainString = window.supabaseClient.sanitizeInputString(strainValue);
  let lineageFormSubmission = lineageValues.join(' X ');
  const formData = new FormData();
  formData.append('strain', cleanStrainString);
  formData.append('cultivator', cleanCultivatorString);
  formData.append('cultivar_email', emailAddressValue);
  formData.append('description', descriptionValue || 'Coming Soon');
  formData.append('effects', effectsValue || 'Coming Soon');
  formData.append('product_type', productTypeValue);
  formData.append('lineage', lineageFormSubmission);
  formData.append('terpenes_list', selectedTerpenes);
  formData.append('strain_category', strainCategoryValue);
  const terpeneMap = window.selectedTerpenePercentages || {};
  formData.append('terpenes_map', JSON.stringify(terpeneMap));
  try {
    const root = window.location.origin;
    const url = new URL('/submit/submit_strain/', root);
    const authToken = await window.supabaseClient.getAccessToken();
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${authToken}`
      }
    });
    if (!response.ok) {
      console.error("Form submission failed:", response.status, response.statusText);
      alert('The submission failed, check your inputs and try again.');
      return;
    }
    const responseData = await response.json();
    getNewlyCreatedStrain(
      responseData.submission_strain,
      responseData.submission_cultivator,
      responseData.cultivar_email
    );
  } catch (error) {
    console.error("Submission error:", error);
    alert('An error occurred while submitting the form. Please try again.');
  }
}

document.getElementById('saveTerpenePercentagesBtn').addEventListener('click', async function() {
  const inputElements = document.querySelectorAll('.terp-percent-input');
  const terpeneMap = {};
  inputElements.forEach(input => {
    const terpName = input.getAttribute('data-terpene');
    const val = parseFloat(input.value);
    terpeneMap[terpName] = val;
  });
  window.selectedTerpenePercentages = terpeneMap;
  const terpenePercentModal = bootstrap.Modal.getInstance(document.getElementById('terpenePercentModal'));
  terpenePercentModal.hide();
  await finalizeStrainSubmission();
});


window.addEventListener('supabaseClientReady', async (event) => {
    const maxChars = 1500;
    const toggleButton = document.getElementById('toggleFormButton');
    const formContainer = document.getElementById('strainSubmissionContainerRow');
    const form = document.getElementById("strainSubmissionForm");
    const lineageList = [];
    window.lineageList = lineageList;
    const longInputFields = [
        { textarea: document.getElementById('strainDescription'), counter: document.getElementById('descriptionCounter') },
        { textarea: document.getElementById('effectsSubmission'), counter: document.getElementById('effectsCounter') }
    ];
    toggleButton.addEventListener('click', function() {
      if (formContainer.style.display === "none") {
        formContainer.style.display = "block";
        toggleButton.textContent = "Hide 'Add a Strain' Form";
      } else {
        formContainer.style.display = "none";
        toggleButton.textContent = "Show 'Add a Strain' Form";
      }
    });
    document.getElementById('addLineage').addEventListener('click', function() {
        createChip();
    });
    document.getElementById('lineageInput').addEventListener('keypress', function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            createChip();
        }
    });
    form.addEventListener('submit', async function(event) {
      submitStrainForm(event);
    });
    function updateCounter(event) {
        const field = longInputFields.find(f => f.textarea === event.target);
        if (field) {
            field.counter.textContent = event.target.value.length;
        }
    }
    longInputFields.forEach(({ textarea, counter }) => {
        if (textarea && counter) {
            counter.textContent = textarea.value.length;
            textarea.removeEventListener('input', updateCounter);
            textarea.addEventListener('input', updateCounter);
        }
    });
});
