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
