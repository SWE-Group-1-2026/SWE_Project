import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
  getAuth, 
  createUserWithEmailAndPassword, 
  GoogleAuthProvider, 
  signInWithPopup 
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDWMOhkUJFkzd3DG0WFN-o9fsC-L7sILcU",
  authDomain: "souspaws-9db65.firebaseapp.com",
  projectId: "souspaws-9db65",
  storageBucket: "souspaws-9db65.firebasestorage.app",
  messagingSenderId: "438669824701",
  appId: "1:438669824701:web:886f8d9f42a0caaf875dd4"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

function showBox(element, message) {
  element.innerText = message;
  element.style.display = 'block';
}

function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

window.togglePassword = function(inputId, toggleId) {
  const passwordInput = document.getElementById(inputId);
  const toggleText = document.getElementById(toggleId);

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleText.textContent = "Hide";
  } else {
    passwordInput.type = "password";
    toggleText.textContent = "Show";
  }
};

window.handleSignup = async function() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  
  const errorDiv = document.getElementById('auth-error');
  const successDiv = document.getElementById('auth-success');

  errorDiv.style.display = 'none';
  successDiv.style.display = 'none';

  if (!isValidEmail(email)) {
    showBox(errorDiv, "Please enter a valid email address.");
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
    await createUserWithEmailAndPassword(auth, email, password);
    
    showBox(successDiv, "Welcome to the pack! Redirecting...");
    setTimeout(() => {
      window.location.href = "main.html";
    }, 2000);
  } catch (err) {
    let message = "An error occurred during signup.";
    if (err.code === 'auth/email-already-in-use') message = "That email is already registered.";
    showBox(errorDiv, message);
    console.error(err);
  }
};

window.handleSocial = async function(provider) {
  if (provider === 'Google') {
    try {
      await signInWithPopup(auth, googleProvider);
      window.location.href = "main.html";
    } catch (err) {
      console.error("Social login failed:", err);
    }
  }
};
