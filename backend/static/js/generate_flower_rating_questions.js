import QuestionBuilder from './QuestionBuilder.js';

const strain =  strainValue;
const cultivator =  cultivatorValue;
const flowerId = flowerIdValue;
const flowerQuestionsContainer = document.getElementById('cardBody');
const cardTitle = document.getElementById('cardTitle');
let step = 0;

let packQuestion

if (cultivator === "Connoisseur" || cultivator === "Cultivar") {
  packQuestion = QuestionBuilder.createTextInputQuestion("Enter the Cult Pack ID", "pack_code", "For example, C1965, B4741 etc");
} else {
  packQuestion = QuestionBuilder.createTextInputQuestion("Please enter Pack Code listed on the product label.", "pack_code", "For example, P1, B4 etc");
}
const flowerQuestions = [
  QuestionBuilder.createEmailQuestion(strain, cultivator),
  QuestionBuilder.createConsumptionMethodQuestion(strain, cultivator),
  QuestionBuilder.createRatingQuestion(strain, "appearance_rating", "Appearance Rating", { startLabel: "Not Desirable", endLabel: "Desirable" }),
  QuestionBuilder.createTextInputQuestion(`${strain} - Appearance Rating Explanation`, "appearance_explanation", "Explain your appearance rating for this strain"),
  QuestionBuilder.createRatingQuestion(strain, "smell_rating", "Aroma Rating", { startLabel: "Weak or None", endLabel: "Strong and Pungent" }),
  QuestionBuilder.createTextInputQuestion(`${strain} - Aroma Rating Explanation`, "smell_explanation", "Explain your aroma rating for this strain"),
  QuestionBuilder.createRatingQuestion(strain, "freshness_rating", "Freshness Rating", { startLabel: "Too Old or Dry", endLabel: "Dank with Good Moisture" }),
  QuestionBuilder.createTextInputQuestion(`${strain} - Freshness Rating Explanation`, "freshness_explanation", "Explain your freshness rating for this strain"),
  QuestionBuilder.createRatingQuestion(strain, "flavor_rating", "Flavor Rating", { startLabel: "Bad or No Flavor", endLabel: "Tasty Flavor" }),
  QuestionBuilder.createTextInputQuestion(`${strain} - Flavor Rating Explanation`, "flavor_explanation", "Explain your flavor rating for this strain"),
  QuestionBuilder.createRatingQuestion(strain, "harshness_rating", "Smoothness Rating", { startLabel: "Very Harsh", endLabel: "Enjoyable" }),
  QuestionBuilder.createTextInputQuestion(`${strain} - Smoothness Rating Explanation`, "harshness_explanation", "Explain your smoothness rating for this strain"),
  QuestionBuilder.createRatingQuestion(strain, "effects_rating", "Effects Rating", { startLabel: "Short-Lived, No Effects", endLabel: "Strong, Lasting Effects" }),
  QuestionBuilder.createEffectsExplanationQuestion(strain),
  packQuestion

];
const int_keys = flowerQuestions
.filter(question => question.key.endsWith('rating') || question.key.endsWith('score'))
.map(question => question.key);

let formState = await loadFormStateforFlowers();

async function jumpToQuestion(questionIndex) {
  await saveCurrentAnswer();
  step = questionIndex;
  await loadQuestion();
}
window.jumpToQuestion = async function jumpToQuestion(questionIndex) {
  await saveCurrentAnswer();
  step = questionIndex;
  await loadQuestion();
}

async function loadFormStateforFlowers() {
  if (typeof localStorage === 'undefined') {
    console.warn('localStorage is not available, defaulting to initial state.');
    return getDefaultFormStateForFlowers();
  }

  try {
    const savedState = localStorage.getItem('formState');
    if (!savedState) {
      return getDefaultFormStateForFlowers();
    }
    const parsedState = JSON.parse(savedState);
    if (parsedState.flower_id !== flowerId) {
      console.warn('Saved form state is for a different flower item, defaulting to initial state.');
      return getDefaultFormStateForFlowers();
    }

    return parsedState;
  } catch (e) {
    console.error('Error reading or parsing saved form state:', e);
    return getDefaultFormStateForFlowers();
  }
}

function getDefaultFormStateForFlowers() {
  return {
    "flower_id": flowerId,
    "cultivator": cultivator,
    "strain": strain
  };
}

document.getElementById('pagination').addEventListener('click', function(event) {
  if (event.target.tagName === 'BUTTON') {
    const questionIndex = parseInt(event.target.textContent);
    if (!isNaN(questionIndex)) {
      saveCurrentAnswer();
      jumpToQuestion(questionIndex);
    }
  }
});

function adjustPaginationForScreenSize() {
  const pagination = document.getElementById('pagination');
  if (window.innerWidth < 768) {
    pagination.classList.add('pagination-sm');
  } else {
    pagination.classList.remove('pagination-sm');
  }
}
function formatTitle(str) {
  return str.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
async function createPagination() {
  const pagination = document.getElementById('pagination');
  pagination.className = 'pagination pagination-sm justify-content-center';
  pagination.innerHTML = '';
  for (let i = 1; i <= flowerQuestions.length; i++) {
    let pageTitle;
    if (i === flowerQuestions.length) {
      pageTitle = "Submit Rating";
    } else {
      pageTitle = formatTitle(flowerQuestions[i].key);
    }
    const pageItemClass = i === step ? 'page-item active' : 'page-item';
    pagination.innerHTML += `<li class="${pageItemClass}" title="${pageTitle}"><button class="page-link" onclick="window.jumpToQuestion(${i})">${i}</button></li>`;
  }
  adjustPaginationForScreenSize();
  $('[data-toggle="tooltip"]').tooltip({
    trigger: 'hover focus'
  });
}

async function saveCurrentAnswer() {
  if (step < flowerQuestions.length) {
    const question = flowerQuestions[step];
    const input = document.getElementById(question.key);
    if (input) {
      var inputVal = input.value;
      if (question.key === "connoisseur") {
        const lowerCaseVal = inputVal.toLowerCase()
        formState[question.key] = lowerCaseVal
      } else if (question.key == "effects_explanation") {
        const selectedOptions = Array.from(document.getElementById('effects_explanation').selectedOptions).map(option => option.value);
        const combinedString = selectedOptions.join(' ');
        formState.effects_explanation = combinedString;
      } else {
        formState[question.key] = inputVal;
      }
    } else {
      const radioCheck = Array.from(document.getElementsByName(question.key)).find(radio => radio.checked);
      const radioVal = radioCheck ? radioCheck.value : "0";
      formState[question.key] = radioVal;
    }
  }
  formState.lastSavedIndex = step;
  localStorage.setItem('formState', JSON.stringify(formState));
}
async function validateResponses() {
  for (const question of int_keys) {
    if (!formState.hasOwnProperty(question) || formState[question] === "0") {
      return false;
    }
  }
  return true;
}

async function checkVoterExists(email) {
  const lowerCaseEmail = email.toLowerCase();
  const root = window.location.origin;
  const url = new URL('/check-mystery-voter', root);
  url.searchParams.append('voter_email', lowerCaseEmail);

  const response = await fetch(url, {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json'
      }
  });

  if (response.ok) {
    const data = await response.json();
    if (!data.exists) {
      $('#FlowerVoterInfoCaptureModal').modal('show');
      return false;
    }
    return true;
  } else {
    console.log("Request failed:", response.status, response.statusText);
    return false;
  }
}

async function loadQuestion() {

    if (step < flowerQuestions.length) {
        nextBtn.textContent = 'Next';
        const question = flowerQuestions[step];
        cardTitle.innerHTML = question.title;
        flowerQuestionsContainer.innerHTML = question.content;
        const inputElement = document.querySelector('#cardBody input, #cardBody select, #cardBody textarea');
        if (inputElement) {
            inputElement.focus();
        }
        if (int_keys.includes(question.key)) {
            QuestionBuilder.setSelectedRadioValue(question.key, formState[question.key]);
        } else {
            if (inputElement && formState[question.key]) {
                inputElement.value = formState[question.key];
            }
        }
    } else {
      cardTitle.innerHTML = "All Questions Completed";
      flowerQuestionsContainer.innerHTML = "";
      nextBtn.textContent = 'Submit';
    }
    await createPagination();
    document.querySelectorAll('button, input, select, textarea').forEach(element => {
        element.setAttribute('tabindex', '0');
    });
}
function convertToIntegers(formState, integerKeys) {
    integerKeys.forEach(key => {
        if (formState.hasOwnProperty(key) && formState[key] !== null && formState[key] !== '') {
            formState[key] = parseInt(formState[key], 10);
        }
    });
}
async function submitForm(formState) {
  formState.connoisseur = formState.connoisseur.toLowerCase();
  delete formState.lastSavedIndex;
  const integerKeys = ['appearance_rating', 'smell_rating', 'flavor_rating', 'freshness_score', 'harshness_rating', 'effects_rating'];
  convertToIntegers(formState, integerKeys);
  formState.flower_id = parseInt(flowerId);

  try {
    const response = await fetch('/flower_ranking/submit-flower-ranking', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formState)
    });
    if (response.ok) {
      const data = await response.json();
      if (formState.cultivator === "Connoisseur" || formState.cultivator === "Cultivar") {
        const connoisseurEmail = formState.connoisseur;
        formState = {};
        formState.connoisseur = connoisseurEmail;
        window.location.href = "/success/connoisseur_flower_pack_november";

      } else {
        const connoisseurEmail = formState.connoisseur;
        formState = {};
        formState.connoisseur = connoisseurEmail;
        window.location.href = "/success";
      }
    } else {
      console.log("Submission failed:", response.status, response.statusText);
    }
  } catch (error) {
    console.error("Error during submission:", error);
  }
  step = 0
}
document.addEventListener('keydown', function(event) {
    const activeElement = document.activeElement;
    const formElements = ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'];
    const nonFormElements = ['startReviewBtn', 'closeBtn'];
    const startReviewButton = document.getElementById('startReviewBtn')
    if (event.key === 'Enter') {
        if (activeElement.type === 'radio') {
            activeElement.checked = true;
        } else if (activeElement === nextBtn) {
            event.preventDefault();
            nextBtn.click();
        } else if (activeElement === nextBtn || activeElement === startReviewButton) {
            event.preventDefault();
            activeElement.click();
        } else if (!formElements.includes(activeElement.tagName)) {
            event.preventDefault();
        }
    } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        document.getElementById('backBtn').click();
    } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        document.getElementById('nextBtn').click();
    }
});

document.getElementById('nextBtn').addEventListener('click', async function() {
  if (step === 0) {
    const emailInput = document.getElementById('connoisseur');
    if (emailInput) {
      const lowerCaseEmail = emailInput.value.toLowerCase();
      const voterExists = await checkVoterExists(lowerCaseEmail);
      if (!voterExists) {
        $('#FlowerVoterInfoCaptureModal').modal('show');
        return;
      }
      formState['connoisseur'] = lowerCaseEmail;
      document.getElementById('paginationContainer').style.display = 'block';
    }
  }
  if (step < flowerQuestions.length) {
    saveCurrentAnswer();
    step++;
    loadQuestion();
  } else {
    saveCurrentAnswer();
    await submitForm(formState);
  }
});

document.getElementById('backBtn').addEventListener('click', function() {
  if (step > 0) {
    saveCurrentAnswer();
    step--;
    loadQuestion(step);
  }
});

window.addEventListener('supabaseClientReady', async function() {
  loadQuestion();
  document.addEventListener("DOMContentLoaded", async function() {
    try {
      const userEmail = await window.supabaseClient.getCurrentUserEmail();
      if (!userEmail) {
        return;
      }
      const emailInput = document.getElementById('connoisseur');
      if (emailInput) {
          emailInput.value = userEmail.toLowerCase();
      }
    } catch {
      return;
    }
    return;
  });
});
$('#FlowerVoterInfoCaptureModal').on('shown.bs.modal', function () {
    $('#FlowerVoterInfoCaptureModal').attr('aria-modal', 'true');
    $('#FlowerVoterInfoCaptureModal').attr('role', 'dialog');
    $('#FlowerVoterInfoCaptureModal input').first().focus();
});

$('#FlowerVoterInfoCaptureModal').on('hidden.bs.modal', function () {
    $('#FlowerVoterInfoCaptureModal').removeAttr('aria-modal');
    $('#FlowerVoterInfoCaptureModal').removeAttr('role');
    nextBtn.focus();
});
