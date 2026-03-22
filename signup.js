function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (input.type === "password") {
    input.type = "text";
  } else {
    input.type = "password";
  }
}

function showBox(element, message) {
  element.innerText = message;
  element.style.display = 'block';
}

async function handleSignup() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  
  const errorDiv = document.getElementById('auth-error');
  const successDiv = document.getElementById('auth-success');

  errorDiv.style.display = 'none';
  successDiv.style.display = 'none';

  if (!isValidEmail(email)) {
    showBox(errorDiv, "Please enter a valid email address (e.g., name@example.com).");
    return;
  }

  if (password.length < 8) {
    showBox(errorDiv, "Password must be at least 8 characters long.");
    return;
  }

  if (password !== confirmPassword) {
    showBox(errorDiv, "Passwords do not match. Please check again.");
    return;
  }

  try {
    console.log("Creating SousPaw account for:", email);
    
    showBox(successDiv, "Welcome to the pack! Redirecting...");

    setTimeout(() => {
      window.location.href = "main.html"; 
    }, 2000);

  } catch (err) {
    showBox(errorDiv, "Something went wrong on our end. Please try again.");
  }
}

function handleSocial(provider) {
  console.log(`Starting ${provider} authentication...`);
}
