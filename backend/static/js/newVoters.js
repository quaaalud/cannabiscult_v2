document.addEventListener("DOMContentLoaded", function() {
    const termsCheckbox = document.getElementById('register_check');
    const submitButton = document.getElementById('submitNewVoterBtn');
    var checkbox = document.getElementById('cannabisIndustryCheck');
    var employmentDiv = document.getElementById('employmentQuestions');
    
    function toggleSubmitButtonState() {
        submitButton.disabled = !termsCheckbox.checked;
    };
    
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
  
    submitButton.addEventListener("click", async function(event) {
        event.preventDefault();
        const { data: { user }, error } = await window.supabaseClient.supabase.auth.getUser();
        if (error || !user) {
            console.error("Failed to retrieve user data.");
            return;
        }
        
        const parsedMeta = window.supabaseClient.parseUserMetadata(user);
        
        const voterEmail = parsedMeta.email;
        const voterName = parsedMeta.name;
        const voterPhone = parsedMeta.phone;
        const voterZip = parsedMeta.zip_code;
        
        const formData = new URLSearchParams();
        formData.append('voter_email', voterEmail);
        formData.append('voter_name', voterName);
        formData.append('voter_phone', voterPhone);
        formData.append('voter_zip_code', voterZip);
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
              document.cookie = "mystery_voter=true; max-age=300; path=/; SameSite=Lax; Secure";
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
