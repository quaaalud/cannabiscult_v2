import QuestionBuilder from './QuestionBuilder.js';

document.addEventListener("DOMContentLoaded", function() {
  const strain =  strainValue;
  const cultivator =  cultivatorValue;
  const concentrateId = concentrateIdValue;
  const questionsContainer = document.getElementById('cardBody');
  const cardTitle = document.getElementById('cardTitle');
  let step = 0;
  let formState = loadFormState();
  
  const questions = [
    QuestionBuilder.createEmailQuestion(strain, cultivator),
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
  ];
  const int_keys = questions
  .filter(question => question.key.endsWith('rating') || question.key.endsWith('score'))
  .map(question => question.key);
  
  document.addEventListener('keydown', function enterKeyHandler(event) {
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
  function loadFormState() {
      const savedState = localStorage.getItem('formState');
      if (savedState) {
          const parsedState = JSON.parse(savedState);
          if (parsedState.hasOwnProperty('concentrate_id') && parsedState.hasOwnProperty('concentrate_id') == concentrateId) {
              return parsedState;
          } else {
          return {
              "concentrate_id": concentrateId,
              "cultivator": cultivator,
              "strain": strain,
          };
        }
      } else {
          return {
              "concentrate_id": concentrateId,
              "cultivator": cultivator,
              "strain": strain,
          };
      }
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
    for (let i = 1; i <= questions.length; i++) {
      let pageTitle;
      if (i === questions.length) {
        pageTitle = "Submit Rating";
      } else {
        pageTitle = formatTitle(questions[i].key);
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
    if (step < questions.length) {
      const question = questions[step];
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
      if (step < questions.length) {
          nextBtn.textContent = 'Next';
          const question = questions[step];
          cardTitle.innerHTML = question.title;
          questionsContainer.innerHTML = question.content;
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
        questionsContainer.innerHTML = "";
        nextBtn.textContent = 'Submit';
      }
      await createPagination();
  }
  function convertToIntegers(formState, integerKeys) {
      integerKeys.forEach(key => {
          if (formState.hasOwnProperty(key) && formState[key] !== null && formState[key] !== '') {
              formState[key] = parseInt(formState[key], 10); // 10 is the radix parameter for base-10 (decimal) numbers
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
      const response = await fetch('/concentrate_ranking/submit-concentrate-ranking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formState)
      });
      if (response.ok) {
        const data = await response.json();
        if (formState.cultivator === "Connoisseur" || formState.cultivator === "Cultivar") {
          const connoisseurEmail = formState.connoisseur; // Save the email value
          formState = {};
          formState.connoisseur = connoisseurEmail;
          window.location.href = "/success/connoisseur_citrus_one";
          
        } else {
          const connoisseurEmail = formState.connoisseur; // Save the email value
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
  }
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
    if (step < questions.length) {
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
  loadQuestion();
});
$(document).ready(function() {
  window.addEventListener('supabaseClientReady', async function() {
    const userEmail = await window.supabaseClient.getCurrentUserEmail();
    if (userEmail) {
      const emailInput = document.getElementById('connoisseur');
      emailInput.value = userEmail;
    }
  });
});
