const petImages = {
  dog: {
    Male: "/static/recipes/images/male_dog_design.png",
    Female: "/static/recipes/images/female_dog_design.png",
  },
  cat: {
    Male: "/static/recipes/images/male_cat_design.png",
    Female: "/static/recipes/images/female_cat_design.png",
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
