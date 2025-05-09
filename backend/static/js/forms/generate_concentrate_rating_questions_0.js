import QuestionBuilder from '../QuestionBuilder.js';

const strain =  strainValue;
const cultivator =  cultivatorValue;
const concentrateId = concentrateIdValue;
const concentrateQuestionsContainer = document.getElementById('cardBody');
const cardTitle = document.getElementById('cardTitle');
let step = 0;

const concentrateQuestions = [
    QuestionBuilder.createRatingQuestion(
        strain,
        "color_rating",
        "Color Rating",
        { startLabel: "Not Desirable", endLabel: "Desirable" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Color Rating Explanation`,
        "color_explanation",
        "Explain your color rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "smell_rating",
        "Aroma Rating",
        { startLabel: "Weak or None", endLabel: "Strong and Pungent" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Aroma Rating Explanation`,
        "smell_explanation",
        "Explain your aroma rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "consistency_rating",
        "Consistency Rating",
        { startLabel: "Too Hard or Dry", endLabel: "Soft with Good Moisture" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Consistency Rating Explanation`,
        "consistency_explanation",
        "Explain your consistency rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "flavor_rating",
        "Flavor Rating",
        { startLabel: "Bad or No Flavor", endLabel: "Tasty Flavor" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Flavor Rating Explanation`,
        "flavor_explanation",
        "Explain your flavor rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "harshness_rating",
        "Smoothness on Inhale Rating",
        { startLabel: "Very Harsh", endLabel: "Enjoyable" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Smoothness on Inhale Rating Explanation`,
        "harshness_explanation",
        "Explain your harshness rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "residuals_rating",
        "Residuals Rating",
        { startLabel: "A lot of Residue", endLabel: "Clean Melt" }
    ),
    QuestionBuilder.createTextInputQuestion(
        `${strain} - Residuals Rating Explanation`,
        "residuals_explanation",
        "Explain your residuals rating for this strain"
    ),
    QuestionBuilder.createRatingQuestion(
        strain,
        "effects_rating",
        "Effects Rating",
        { startLabel: "Short-Lived, No Effects", endLabel: "Strong, Lasting Effects" }
    ),
    QuestionBuilder.createEffectsExplanationQuestion(strain),
    QuestionBuilder.createTextInputQuestion(
        "Please enter Batch ID listed on the box COA label.",
        "pack_code",
        "For example, T2, A3 etc"
    ),
];
const int_keys = concentrateQuestions
.filter(question => question.key.endsWith('rating') || question.key.endsWith('score'))
.map(question => question.key);

document.addEventListener('keydown', function enterKeyHandler(event) {
    const nextBtn = document.getElementById('nextBtn');
    if (event.keyCode === 13) {
        event.preventDefault();
        nextBtn.click();
    }
});

let formState = await loadFormStateforConcentrates();

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

async function loadFormStateforConcentrates() {
    if (typeof localStorage === 'undefined') {
        console.warn('localStorage is not available, defaulting to initial state.');
        return getDefaultFormStateForConcentrates();
    }
    try {
        const savedState = localStorage.getItem('formState');
        if (!savedState) {
            return getDefaultFormStateForConcentrates();
        }
        const parsedState = JSON.parse(savedState);
        if (parsedState.concentrate_id !== concentrateId) {
            console.warn('Saved form state is for a different concentrate item, defaulting to initial state.');
            return getDefaultFormStateForConcentrates();
        }
        return parsedState;
    } catch (e) {
        console.error('Error reading or parsing saved form state:', e);
        return getDefaultFormStateForConcentrates();
    }
}

function getDefaultFormStateForConcentrates() {
    return {
        "concentrate_id": concentrateId,
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
    for (let i = 1; i <= concentrateQuestions.length; i++) {
        let pageTitle;
        if (i === concentrateQuestions.length) {
            pageTitle = "Submit Rating";
        } else {
            pageTitle = formatTitle(concentrateQuestions[i].key);
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
    if (step < concentrateQuestions.length) {
        const question = concentrateQuestions[step];
        const input = document.getElementById(question.key);
        if (input) {
          var inputVal = input.value;
          if (question.key == "effects_explanation") {
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
    const nextBtn = document.getElementById('nextBtn')
    if (step < concentrateQuestions.length) {
        nextBtn.textContent = 'Next';
        const question = concentrateQuestions[step];
        cardTitle.innerHTML = question.title;
        concentrateQuestionsContainer.innerHTML = question.content;
        if (int_keys.includes(question.key)) {
            QuestionBuilder.setSelectedRadioValue(question.key, formState[question.key]);
        } else {
            const inputElement = document.getElementById(question.key);
            if (inputElement && formState[question.key]) {
                inputElement.value = formState[question.key];
            }
        }
    } else {
      cardTitle.innerHTML = "All Questions Completed";
      concentrateQuestionsContainer.innerHTML = "";
      nextBtn.textContent = 'Submit';
    }
    await createPagination();
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
    const integerKeys = ['color_rating', 'smell_rating', 'consistency_rating', 'flavor_rating', 'harshness_score', 'residuals_rating', 'effects_rating'];
    convertToIntegers(formState, integerKeys);
    formState.concentrate_id = parseInt(concentrateId);

    try {
      const response = await fetch('/concentrates/ranking', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(formState)
      });
      if (response.ok) {
          const connoisseurEmail = formState.connoisseur;
          formState = {};
          formState.connoisseur = connoisseurEmail;
          window.location.reload();
      };
    } catch (error) {
        console.error("Error during submission:", error);
    }
    step = 0
}
document.getElementById('nextBtn').addEventListener('click', async function() {
    if (step === 0) {
        const userEmail = await window.supabaseClient.getCurrentUserEmail();
        if (userEmail) {
            const voterExists = await checkVoterExists(userEmail);
            if (!voterExists) {
                $('#FlowerVoterInfoCaptureModal').modal('show');
                return;
            }
            formState['connoisseur'] = userEmail;
            document.getElementById('paginationContainer').style.display = 'block';
        }
    }
    if (step < concentrateQuestions.length) {
        saveCurrentAnswer();
        step++;
        loadQuestion();
    } else {
        saveCurrentAnswer();
        const allAnswered = await validateResponses();
        if (!allAnswered) {
          return alert("Please answer every rating before you submit.");
        }
        await submitForm(formState);
    }
});

document.getElementById('backBtn').addEventListener('click', function() {
    if (step > 0) {
        saveCurrentAnswer();
        step--;
        loadQuestion(step);
    } else {
        document.getElementById('backToCardBtn').click();
    }
});

window.addEventListener('supabaseClientReady', async function() {
    loadQuestion();
});
$('#FlowerVoterInfoCaptureModal').on('shown.bs.modal', function () {
    $('#FlowerVoterInfoCaptureModal').attr('aria-modal', 'true');
    $('#FlowerVoterInfoCaptureModal').attr('role', 'dialog');
    $('#FlowerVoterInfoCaptureModal input').first().focus();
});

$('#FlowerVoterInfoCaptureModal').on('hidden.bs.modal', function () {
    $('#FlowerVoterInfoCaptureModal').removeAttr('aria-modal');
    $('#FlowerVoterInfoCaptureModal').removeAttr('role');
    const cookieString = document.cookie.split('; ').find(row => row.startsWith('mystery_voter='));
    const flagValue = cookieString ? cookieString.split('=')[1] : null;
    
    if (flagValue === 'true') {
        saveCurrentAnswer();
        step++;
        loadQuestion();
        document.cookie = "mystery_voter=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;";
    }
});
