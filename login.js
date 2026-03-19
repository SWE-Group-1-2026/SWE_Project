
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


function handleSocial(platform) {
    console.log("Signing in with:", platform);
    alert("This would typically redirect to " + platform + " authentication.");
}

function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (email && password) {
        alert("Welcome to SousPaw!");
    } else {
        alert("Please fill in all fields.");
    }
}



