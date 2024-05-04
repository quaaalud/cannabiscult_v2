// generate_rating_questions.js

/**
 * A utility class for creating various types of question components.
 */
class QuestionBuilder {

  /**
   * Creates a rating question component.
   * @param {string} strain - The strain name.
   * @param {string} key - The unique key for the question.
   * @param {string} description - The description of the rating.
   * @param {object} scaleDescription - Object containing labels for the start and end of the scale.
   * @returns {object} An object containing the title and HTML content for the rating question.
   */
  static createRatingQuestion(strain, key, description, scaleDescription) {
    const options = Array.from({ length: 10 }, (_, i) => `
      <input type="radio" class="btn-check" name="${key}" id="${key}${i + 1}" value="${i + 1}" autocomplete="off">
      <label class="btn btn-light" for="${key}${i + 1}">${i + 1}</label>
    `).join('');

    return {
      title: `${strain}<br/>${description}`,
      content: `
        <div class="container-fluid align-items-center text-center btn-group-container py-3">
          <div class="row pt-1 mx-auto">
            <div class="col-9 text-center mx-auto">
              <label class="modal-info-shadow long-voting-label" for="${key}_1_point">${scaleDescription.startLabel}</label>
            </div>
          </div>
          <div class="col-10 btn-group btn-group-sm btn-group-container" role="group" aria-label="${strain} ${description}">
            <div class="row btn-group-container">
              ${options}
            </div>
          </div>
          <div class="row pt-1 mx-auto">
            <div class="col-9 text-center mx-auto">
              <label class="modal-info-shadow long-voting-label" for="${key}_10_point">${scaleDescription.endLabel}</label>
            </div>
          </div>
        </div>
      `,
      key: key
    };
  }

  /**
   * Creates an HTML structure for an explanation question.
   * @param {string} strain - The name of the strain.
   * @param {string} key - The unique key for the question.
   * @param {string} description - The description or title of the question.
   * @returns {object} An object containing the title and HTML content for the explanation question.
   */
  static createExplanationQuestion(strain, key, description) {
    // Validate input parameters
    if (!strain || !key || !description) {
      console.error('Invalid parameters passed to createExplanationQuestion.');
      return { title: '', content: '', key: '' };
    }
    // Build and return the question object
    return {
      title: `${strain}<br/>${description}`,
      content: `
        <div class="container px-4">
          <div class="row px-4 py-3">
            <div class="form-outline" data-mdb-input-init>
              <textarea class="form-control shadow-2-strong" id="${key}" name="${key}" rows="4" placeholder="Start typing here..."></textarea>
            </div>
            <label class="form-label pt-4" for="${key}" name="${key}_label" id="${key}_label">Explain your rating in the space above.</label>
          </div>
        </div>
      `,
      key: key
    };
  }
  
  /**
   * Creates a Yes/No question with Bootstrap-styled radio buttons.
   * @param {string} question - The question to be asked.
   * @param {string} key - The unique key for the question.
   * @param {string} noLabel - The label for the 'No' option.
   * @param {string} yesLabel - The label for the 'Yes' option.
   * @returns {object} An object containing the title and HTML content for the Yes/No question.
   */
  static createYesNoQuestion(question, key, noLabel, yesLabel) {
    const title = `${question}`;
    const content = `
      <div class="yes-no-question-container py-3">
        <div class="row g-1 text-center justify-content-center mx-0 mx-lg-3">
          <div class="col-5 mx-auto">
            <div class="form-check">
              <input class="form-check-input" type="radio" id="${key}_no" name="${key}" value="false">
              <label class="form-check-label" for="${key}_no"><strong>${noLabel}</strong></label>
            </div>
          </div>
          <div class="col-5 mx-auto">
            <div class="form-check">
              <input class="form-check-input" type="radio" id="${key}_yes" name="${key}" value="true">
              <label class="form-check-label" for="${key}_yes"><strong>${yesLabel}</strong></label>
            </div>
          </div>
        </div>
      </div>
    `;
  
    return { title, content, key };
  }

  /**
   * Creates an object representing a question about the method of consumption.
   * @param {string} strain - The name of the strain.
   * @param {string} cultivator - The name of the cultivator.
   * @returns {object} An object containing the title, HTML content, and key for the consumption method question.
   */
  static createConsumptionMethodQuestion(strain, cultivator) {
    return {
      title: `${strain} by ${cultivator}`,
      content: `
        <div class="container ps-lg-3 py-3">
          <div class="row align-items-center justify-content-center text-start g-3 mx-2">
            <div class="col-md-6 px-3">
              <label class="consume-label" for="method_of_consumption" style="display: block; font-weight: bold; margin-bottom: 0.25rem;">How did you consume ${strain}:</label>
            </div>
            <div class="col-md-6 px-3"> 
              <select class="form-select" id="method_of_consumption" name="method_of_consumption" aria-label="Method of Consumption Dropdown Field" style="width: 100%; padding: 0.5rem; border-radius: 0.25rem; border: 1px solid #ced4da;">
                <option value="blunt">Blunt</option>
                <option value="bong">Bong</option>
                <option value="joint">Joint</option>
                <option value="one_hitter">One-Hitter</option>
                <option value="pipe">Pipe</option>
                <option value="steamroller">Steamroller</option>
                <option value="vaporizer">Vaporizer</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
        </div>`,
      key: "method_of_consumption"
    };
  }


  /**
   * Creates an object representing a question for obtaining a user's email.
   * @param {string} strain - The name of the strain.
   * @param {string} cultivator - The name of the cultivator.
   * @returns {object} An object containing the title, HTML content, and key for the email question.
   */
  static createEmailQuestion(strain, cultivator) {
    return {
      title: `${strain} by ${cultivator}`,
      content: `
        <div class="container px-4 py-3">
          <div class="row px-4 py-2 py-lg-3">
            <input class="form-control text-center email-input-field" id="connoisseur" name="connoisseur" placeholder="Your email is required to rate strains" />
          </div>
        </div>`,
      key: "connoisseur"
    };
  }


  /**
   * Creates an object representing a question for explaining the effects rating.
   * @param {string} strain - The name of the strain.
   * @returns {object} An object containing the title, HTML content, and key for the effects explanation question.
   */
  static createEffectsExplanationQuestion(strain) {
    return {
      title: `${strain}<br/>Effects Rating Explanation`,
      content: `
        <div class="container align-content-center align-items-center justify-content-center text-center py-3">
          <div class="row align-items-center">
            <div class="col-7">
              <label class="pb-3 ps-2 fs-5 text-start" for="effects_explanation">Please pick a minimum of two (2) to explain how ${strain} made you feel:</label>
            </div>
            <div class="col-5 align-content-center align-items-center justify-content-center ">
              <select class="form-select px-3 px-lg-4" id="effects_explanation" name="effects_explanation" aria-label="Effects Rating Explanation Field" multiple>
                <option value="sedative">Sedative</option>
                <option value="anxious">Anxious</option>
                <option value="relaxing">Relaxing</option>
                <option value="sleepy">Sleepy</option>
                <option value="tingly">Tingly</option>
                <option value="calming">Calming</option>
                <option value="hungry">Hungry</option>
                <option value="happy">Happy</option>
                <option value="giggly">Giggly</option>
                <option value="energizing">Energizing</option>
                <option value="euphoric">Euphoric</option>
                <option value="focused">Focused</option>
                <option value="uplifting">Uplifting</option>
                <option value="alert">Alert</option>
                <option value="creative">Creative</option>
                <option value="talkative">Talkative</option>
                <option value="aroused">Aroused</option>
                <option value="none">None / Short Lived</option>
              </select>
            </div>
          </div>
        </div>`,
      key: "effects_explanation"
    };
  }


  /**
   * Creates a text input question component.
   * @param {string} prompt - The prompt or question to be displayed.
   * @param {string} key - The unique key for the input field.
   * @param {string} example - An example value to guide the user.
   * @returns {object} An object containing the title and HTML content for the text input question.
   */
  static createTextInputQuestion(prompt, key, example) {
    return {
      title: prompt,
      content: `
        <div class="container px-4 py-3">
          <div class="row px-4 py-2 py-lg-3">
            <input type="text" class="form-control" id="${key}" name="${key}" placeholder="${example}">
          </div>
        </div>`,
      key: key
    };
  }
  static setSelectedRadioValue(name, value) {
    if (value) {
      const radioToCheck = document.querySelector(`input[name="${name}"][value="${value}"]`);
      if (radioToCheck) {
        radioToCheck.checked = true;
      }
    }
  }
  static setSelectedMultiSelectValues(id, value) {
    if (value) {
      const selectElement = document.getElementById(id);
      const values = value.split(' ');
      Array.from(selectElement.options).forEach(option => {
        if (values.includes(option.value)) {
          option.selected = true;
        }
      });
    }
  }
}


export default QuestionBuilder;
