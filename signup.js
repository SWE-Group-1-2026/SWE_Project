const USERS = [
  {
    email: "test@souspaw.com",
    password: "testpassword",
    name: "Dev Tester",
    role: "dev",
  }
];

function getSavedUsers() {
  const stored = localStorage.getItem("souspaw_users");
  const localUsers = stored ? JSON.parse(stored) : [];
  return [...USERS, ...localUsers];
}

function registerUser(email, password) {
  const users = getSavedUsers();

  const exists = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (exists) return { error: "An account with that email already exists." };

  const newUser = {
    email,
    password,
    name: email.split("@")[0],
    role: "user",
    createdAt: new Date().toISOString(),
  };

  const stored = localStorage.getItem("souspaw_users");
  const localUsers = stored ? JSON.parse(stored) : [];
  localUsers.push(newUser);
  localStorage.setItem("souspaw_users", JSON.stringify(localUsers));

  return { user: newUser };
}



function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function togglePassword(inputId, toggleId) {
  const passwordInput = document.getElementById(inputId);
  const toggleText = document.getElementById(toggleId);

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleText.textContent = "Hide";
  } else {
    passwordInput.type = "password";
    toggleText.textContent = "Show";
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
    const result = registerUser(email, password);

    if (result.error) {
      showBox(errorDiv, result.error);
      return;
    }

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
