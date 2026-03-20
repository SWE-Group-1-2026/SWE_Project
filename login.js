
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



//addded a test account so we can use temporarily
const USERS = [
    {
        email: "test@souspaw.com",
        password: "testpassword",
        name: "Dev Tester",
        role: "dev",
    }

    //Add real users here later, or swap this out for an API call
]


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
 

// ─── Event Handlers ───────────────────────────────────────────────────────────
 
function handleSocial(platform) {
  // TODO: Integrate OAuth for Google / Apple
  alert(`Social login with ${platform} coming soon!`);
}

function authenticateUser(email, password) {
  return USERS.find(
    (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
  ) || null;
}
 
function handleLogin() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  setError("");

  if (!email || !password) {
    setError("Please enter your email and password.");
    return;
  }

  const user = authenticateUser(email, password);

  if (user) {
    createSession(user);
    window.location.href = "main.html";
  } else {
    setError("Incorrect email or password. Please try again.");
  }
}

