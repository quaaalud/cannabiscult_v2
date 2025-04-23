import QuestionBuilder from '../QuestionBuilder.js';

const strain =  strainValue;
const cultivator =  cultivatorValue;
const preRollId = preRollIdValue;
const prerollQuestionsContainer = document.getElementById('cardBody');
const cardTitle = document.getElementById('cardTitle');

const prerollQuestions = [
  QuestionBuilder.createTextInputQuestion(
    "Please enter Batch ID listed on the box COA label.",
    "pack_code",
    "For example, T2, A3 etc"
  ),
  QuestionBuilder.createRatingQuestion(
    strain,
    "ease_to_light_rating",
    "Was the joint easy to light?",
    { startLabel: "Hard to light", endLabel: "Easy to Light" }
  ),
  QuestionBuilder.createRatingQuestion(
    strain,
    "burn_rating",
    "Did the joint burn even?",
    { startLabel: "Burned Uneven", endLabel: "Burned Even" }
  ),
  QuestionBuilder.createRatingQuestion(
    strain,
    "tightness_rating",
    "Was the joint packed too tight?",
    { startLabel: "Too Tight", endLabel: "Just Right" }
  ),
  QuestionBuilder.createRatingQuestion(
    strain,
    "roll_rating",
    "Was the joint packed too loose?",
    { startLabel: "Too Loose", endLabel: "Just Right" }
  ),
  QuestionBuilder.createRatingQuestion(
    strain,
    "overall_score",
    "Overall Experience",
    { startLabel: "Not enjoyable, poor quality", endLabel: "Enjoyable, high quality" }
  ),
  QuestionBuilder.createYesNoQuestion(
    "Would You Purchase this again?", "purchase_bool", "No at $50", "Yes at $50"
  ),
];
let step = 0;
let formState = await loadFormStateforPreRolls();
const int_keys = prerollQuestions
.filter(question => question.key.endsWith('rating') || question.key.endsWith('score'))
.map(question => question.key);

document.addEventListener('keydown', function enterKeyHandler(event) {
  nextBtn = document.getElementById('nextBtn')
  if (event.keyCode === 13) {
    event.preventDefault();
    nextBtn.click();
  }
});
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
async function loadFormStateforPreRolls() {
  // Early check for localStorage availability
  if (typeof localStorage === 'undefined') {
    console.warn('localStorage is not available, defaulting to initial state.');
    return getDefaultFormState();
  }
  try {
    const savedState = localStorage.getItem('formState');
    if (!savedState) {
      return getDefaultFormState();
    }
    const parsedState = JSON.parse(savedState);
    // Ensure the parsedState is for the current pre-roll item
    if (parsedState.pre_roll_id !== preRollId) {
      console.warn('Saved form state is for a different pre-roll item, defaulting to initial state.');
      return getDefaultFormState();
    }
    return parsedState; // Return the saved state if it matches the current pre-roll ID
  } catch (e) {
    console.error('Error reading or parsing saved form state:', e);
    return getDefaultFormState(); // Fallback to default state in case of any error
  }
}

function getDefaultFormState() {
  return {
    "pre_roll_id": preRollId,
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
  for (let i = 1; i <= prerollQuestions.length; i++) {
    let pageTitle;
    if (i === prerollQuestions.length) {
      pageTitle = "Submit Rating";
    } else {
      pageTitle = formatTitle(prerollQuestions[i].key);
    }
    const pageItemClass = i === step ? 'page-item active' : 'page-item';
    pagination.innerHTML += `<li class="${pageItemClass}" title="${pageTitle}"><button class="page-link" onclick="window.jumpToQuestion(${i})">${i}</button></li>`;
  }
  adjustPaginationForScreenSize();
  $('[data-toggle="tooltip"]').tooltip({
    trigger: 'hover focus' // 'focus' for touch devices
  });
}

async function saveCurrentAnswer() {
  if (step < prerollQuestions.length) {
    const question = prerollQuestions[step];
    const input = document.getElementById(question.key);
    if (input) {
      var inputVal = input.value;
      if (question.key === "connoisseur") {
        const lowerCaseVal = inputVal.toLowerCase()
        formState[question.key] = lowerCaseVal
      } else {
        formState[question.key] = inputVal;
      }
    } else {
      const radioCheck = Array.from(document.getElementsByName(question.key)).find(radio => radio.checked);
      const radioVal = radioCheck ? radioCheck.value : "0";
      formState[question.key] = radioVal;
    }
  }
  formState.lastSavedIndex = step; // Save the current index
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
    if (step > prerollQuestions.length) {
      step = 0
    }
    nextBtn = document.getElementById('nextBtn')
    if (step < prerollQuestions.length) {
        nextBtn.textContent = 'Next';
        const question = prerollQuestions[step];
        cardTitle.innerHTML = question.title;
        prerollQuestionsContainer.innerHTML = question.content;
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
      prerollQuestionsContainer.innerHTML = "";
      nextBtn.textContent = 'Submit';
    }
    await createPagination();
}
function convertYesNoToBoolean(yesNoString) {
  return yesNoString.toLowerCase().includes('true');
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
  formState.purchase_bool = convertYesNoToBoolean(formState.purchase_bool);
  const integerKeys = [
    'ease_to_light_rating', 'burn_rating', 'tightness_rating', 'roll_rating', 'overall_score', 'pre_roll_id'
  ];
  convertToIntegers(formState, integerKeys);
  try {
    const response = await fetch('/prerolls/ranking', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formState)
    });
    if (response.ok) {
      const data = await response.json();
      const connoisseurEmail = formState.connoisseur;
      formState = {};
      formState.connoisseur = connoisseurEmail;
      window.location.href = "/success";
    } else {
      console.log("Submission failed:", response.status, response.statusText);
    }
  } catch (error) {
    console.error("Error during submission:", error);
  }
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
  if (step < prerollQuestions.length) {
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
    }
});

window.addEventListener('supabaseClientReady', async function() {
    loadQuestion();
    await loadFormStateforPreRolls();
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
