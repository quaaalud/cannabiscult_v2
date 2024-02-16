import QuestionBuilder from './QuestionBuilder.js';

document.addEventListener("DOMContentLoaded", function() {
  const strain =  strainValue;
  const cultivator =  cultivatorValue;
  const preRollId = preRollIdValue;
  const questionsContainer = document.getElementById('cardBody');
  const cardTitle = document.getElementById('cardTitle');
  let step = 0;
  let formState = loadFormState();
  
  const questions = [
    QuestionBuilder.createEmailQuestion(strain, cultivator),
  
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
          if (parsedState.hasOwnProperty('pre_roll_id') && parsedState.hasOwnProperty('pre_roll_id') == preRollId) {
              return parsedState;
          } else {
          return {
              "pre_roll_id": preRollId,
              "cultivator": "{{ cultivator }}",
              "strain": "{{ strain }}"
          };
        }
      } else {
          return {
              "pre_roll_id": preRollId,
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
  function convertYesNoToBoolean(yesNoString) {
    return yesNoString.toLowerCase().includes('true');
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
    formState.purchase_bool = convertYesNoToBoolean(formState.purchase_bool);
    const integerKeys = ['ease_to_light_rating', 'burn_rating', 'tightness_rating', 'roll_rating', 'overall_score', 'pre_roll_id'];
    convertToIntegers(formState, integerKeys);
    try {
      const response = await fetch('/prerolls/update_or_create_pre_roll_ranking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formState)
      });
      if (response.ok) {
        const data = await response.json();
        if (formState.cultivator === "Connoisseur") {
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
