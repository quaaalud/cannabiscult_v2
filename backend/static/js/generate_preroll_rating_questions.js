import QuestionBuilder from './QuestionBuilder.js';

document.addEventListener("DOMContentLoaded", function() {
  const questionsContainer = document.getElementById('cardBody');
  const cardTitle = document.getElementById('cardTitle');
  
  document.addEventListener('keydown', function enterKeyHandler(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      nextBtn.click();
    }
  });

  const strain =  strainValue;
  const cultivator =  cultivatorValue;

  // Generate questions
  const questions = [
    QuestionBuilder.createEmailQuestion(strain, cultivator), // Email collection for connoisseur
  
    QuestionBuilder.createTextInputQuestion(
      "Please enter Batch ID listed on the box COA label.",
      "batch_id",
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
      { startLabel: "Burned uneven", endLabel: "Burned even" }
    ),
  ];


  function loadQuestion(index) {
    if (index >= 0 && index < questions.length) {
      const question = questions[index];
      cardTitle.innerHTML = question.title;
      questionsContainer.innerHTML = question.content;
    }
  }

  loadQuestion(0);

  let currentQuestionIndex = 0;
  document.getElementById('nextBtn').addEventListener('click', function() {
    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex++;
      loadQuestion(currentQuestionIndex);
    }
  });

  document.getElementById('backBtn').addEventListener('click', function() {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
      loadQuestion(currentQuestionIndex);
    }
  });
});
