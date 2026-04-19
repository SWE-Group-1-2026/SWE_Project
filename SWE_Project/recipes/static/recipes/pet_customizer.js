const petImages = {
  dog: {
    Male: "/static/recipes/images/M_DOG_design.jpg",
    Female: "/static/recipes/images/F_DOG_design.jpg",
  },
  cat: {
    Male: "/static/recipes/images/M_CAT_design.jpg",
    Female: "/static/recipes/images/F_CAT_design.jpg",
  },
};

function updateAvatar() {
  const species = document.getElementById("speciesInput").value;
  const gender = document.getElementById("genderInput").value;
  const petDisplay = document.querySelector(".animated-pet");
  const imageUrl = petImages[species]?.[gender];

  if (imageUrl) {
    petDisplay.innerHTML = `<img src="${imageUrl}" alt="Pet avatar">`;
  } else {
    petDisplay.textContent = "🐾";
  }
}

function updateName() {
  const val = document.getElementById("nameInput").value;
  document.getElementById("displayName").textContent = val || "Lucky";
}

function updateGenderLabel() {
  const val = document.getElementById("genderInput").value;
  document.getElementById("displayGender").textContent = `Gender: ${val}`;
  updateAvatar();
}

document.addEventListener("DOMContentLoaded", () => {
  updateName();
  updateGenderLabel();
});
