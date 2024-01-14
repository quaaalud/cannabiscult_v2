document.addEventListener("DOMContentLoaded", function() {
  const termsCheckbox = document.getElementById('register_check');
  const submitButton = document.getElementById('submitNewVoterBtn');
  var checkbox = document.getElementById('cannabisIndustryCheck');
  var employmentDiv = document.getElementById('employmentQuestions');
  
  function toggleSubmitButtonState() {
      submitButton.disabled = !termsCheckbox.checked;
  }
  
  termsCheckbox.addEventListener('change', toggleSubmitButtonState);
  
  toggleSubmitButtonState();

  checkbox.addEventListener('change', function() {
    if (checkbox.checked) {
      employmentDiv.style.display = 'block';
    } else {
      employmentDiv.style.display = 'none';
    }
  });
  
  const form = document.getElementById("newVoterForm");
      document.getElementById("newUserBackBtn").onclick = function() {
    $('#FlowerVoterInfoCaptureModal').modal('hide');
  };

  submitButton.addEventListener("click", function(event) {
    event.preventDefault();

    const formData = new URLSearchParams();
      const emailInput = document.getElementById("new_connoisseur").value
      const lowerCasedEmail = emailInput.toLowerCase()
      formData.append('voter_name', document.getElementById("connoisseur_name").value);
      formData.append('voter_email', lowerCasedEmail);
      formData.append('voter_phone', document.getElementById("connoisseur_phone").value);
      formData.append('voter_zip_code', document.getElementById("connoisseur_zip_code").value);
      formData.append('voter_industry_employer', document.getElementById("connoisseur_employer").value);
      formData.append('voter_industry_job_title', document.getElementById("connoisseur_job_title").value);

      fetch("/submit-new-voter", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString()
      })
    .then(response => response.json())
    .then(data => {
      if (data.status === true) {
        $('#FlowerVoterInfoCaptureModal').modal('hide');
      } else {
        alert("Please ensure you have provided a valid email and try again.")
        return
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
  });
});
