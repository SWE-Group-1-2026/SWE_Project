// function handleSocial(platform) {
//     console.log("Signing in with:", platform);
//     alert("This would typically redirect to " + platform + " authentication.");
// }

// function handleLogin() {
//     const email = document.getElementById('email').value;
//     const password = document.getElementById('password').value;

//     if (email && password) {
//         alert("Welcome to SousPaw!");
//     } else {
//         alert("Please fill in all fields.");
//     }
// }

//added a test account so we can use temporarily
const USERS = [
    {
        email: "test@souspaw.com",
        password: "testpassword",
        name: "Dev Tester",
        role: "dev",
    }

    //Add real users here later, or swap this out for an API call
]

function getSavedUsers(){
  const stored = localStorage.getItem("souspaw_users");
  const localUsers = stored ? JSON.parse(stored) : [];
  return [...USERS, ...localUsers];
}

/**
 * Stores a lightweight session so other pages can check if the user is logged in.
 * Replace sessionStorage with a real token/cookie flow in production.
 */
function createSession(user) {
  const session = {
    name: user.name,
    email: user.email,
    role: user.role,
    loggedInAt: new Date().toISOString(),
  };
  sessionStorage.setItem("souspaw_session", JSON.stringify(session));
}

/** Call this on protected pages to redirect guests away. */
function requireAuth(redirectTo = "login.html") {
  const session = sessionStorage.getItem("souspaw_session");
  if (!session) window.location.href = redirectTo;
  return session ? JSON.parse(session) : null;
}
 
/** Logs the user out and clears the session. */
function logout(redirectTo = "login.html") {
  sessionStorage.removeItem("souspaw_session");
  window.location.href = redirectTo;
}

function setError(msg) {
  let el = document.getElementById("auth-error");
  if (!el) return;
  el.textContent = msg;
  el.style.display = msg ? "block" : "none";
}

function togglePassword(inputId = "password", toggleId = "togglePassword") {
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
function toggleConfirmPassword() {
  const passwordInput = document.getElementById("confirm-password");
  const toggleText = document.getElementById("toggleConfirm");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleText.textContent = "Hide";
  } else {
    passwordInput.type = "password";
    toggleText.textContent = "Show";
  }
}

// ─── Event Handlers ───────────────────────────────────────────────────────────
 
function handleSocial(platform) {
  // TODO: Integrate OAuth for Google
  alert(`Social login with ${platform} coming soon!`);
}

function authenticateUser(email, password) {
  const allUsers = getSavedUsers();
  return allUsers.find(
    (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
  ) || null;
}

function registerUser(name, email, password) {
  const users = getSavedUsers();

   const exists = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (exists) {
    setError("An account with that email already exists.");
    return false;
  }

  const newUser = {
    name,
    email,
    password,
    role: "user",
    createdAt: new Date().toISOString(),
  };

  // Only save the locally-registered users (not the hardcoded USERS array)
  const stored = localStorage.getItem("souspaw_users");
  const localUsers = stored ? JSON.parse(stored) : [];
  localUsers.push(newUser);
  localStorage.setItem("souspaw_users", JSON.stringify(localUsers));

  return newUser;
}
