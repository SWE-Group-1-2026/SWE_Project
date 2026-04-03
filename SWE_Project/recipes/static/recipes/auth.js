function logout(redirectTo = "/login/") {
  sessionStorage.removeItem("souspaw_session");
  window.location.href = redirectTo;
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
