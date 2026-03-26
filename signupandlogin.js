function createSession(user) {
  const session = {
    name: user.name,
    email: user.email,
    role: user.role,
    loggedInAt: new Date().toISOString(),
  };
  sessionStorage.setItem("souspaw_session", JSON.stringify(session));
}

function requireAuth(redirectTo = "login.html") {
  const session = sessionStorage.getItem("souspaw_session");
  if (!session) window.location.href = redirectTo;
  return session ? JSON.parse(session) : null;
}
 
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
