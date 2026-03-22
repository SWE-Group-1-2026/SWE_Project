async function handleSignup() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  const errorDiv = document.getElementById('auth-error');
  const successDiv = document.getElementById('auth-success');

  errorDiv.style.display = 'none';
  successDiv.style.display = 'none';

  if (!email || !password || !confirmPassword) {
    showBox(errorDiv, "Please fill in all fields.");
    return;
  }

  if (password.length < 8) {
    showBox(errorDiv, "Password must be at least 8 characters long.");
    return;
  }

  if (password !== confirmPassword) {
    showBox(errorDiv, "Passwords do not match.");
    return;
  }

  try {
    console.log("Registering user:", email);

    showBox(successDiv, "Account created successfully! Redirecting...");

    setTimeout(() => {
      window.location.href = "main.html"; 
    }, 2000);

  } catch (err) {
    showBox(errorDiv, "An error occurred. Please try again later.");
  }
}

function showBox(element, message) {
  element.innerText = message;
  element.style.display = 'block';
}

function handleSocial(provider) {
  console.log(`Starting OAuth flow with ${provider}...`);
}
