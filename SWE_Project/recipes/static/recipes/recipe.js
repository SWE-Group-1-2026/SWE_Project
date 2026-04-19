document.addEventListener("DOMContentLoaded", () => {
  const player = document.querySelector("[data-step-player]");
  const petConfig = document.getElementById("pet-config");
  if (!player || !petConfig) {
    return;
  }

  const GITHUB_BASE = "https://raw.githubusercontent.com/SWE-Group-1-2026/SWE_Project/main/SWE_Project/recipes/static/recipes/images/";
  const genderInit = petConfig.getAttribute("data-gender").charAt(0).toUpperCase();
  const species = petConfig.getAttribute("data-species").toUpperCase();

  const ACTION_MAP = {
        "whisk": "WHISKING",
        "rolling":"ROLLING",
        "mix":"WHISKING",
        "beat eggs":"WHISKING",
        "frost":"FROSTING",
        "mixer": "MIXER",
        "griddle": "GRIDDLE",
        "toast the bread": "TOASTER",
        "blend": "BLENDING",
        "blender": "BLENDING",
        "sauté": "PAN",
        "garnish":"SEASONING",
        "sprinkle":"SEASONING",
        "season":"SEASONING",
        "bake": "OVEN",
        "oven": "OVEN",
        "chop": "CHOPPING",
        "slice": "CHOPPING",
        "cut": "CHOPPING",
        "stir":"POT",
        "boil":"POT",
        "default": "design" 
  };

  const steps = Array.from(document.querySelectorAll("[data-recipe-step]"))
    .map((step) => step.textContent.trim())
    .filter(Boolean);

  if (!steps.length) {
    return;
  }

  const startButton = player.querySelector("[data-start-button]");
  const panel = player.querySelector("[data-step-panel]");
  const progress = player.querySelector("[data-step-progress]");
  const progressPercent = player.querySelector("[data-progress-percent]");
  const progressFill = player.querySelector("[data-progress-fill]");
  const current = player.querySelector("[data-step-current]");
  const prevButton = player.querySelector("[data-prev-button]");
  const nextButton = player.querySelector("[data-next-button]");
  const restartButton = player.querySelector("[data-restart-button]");

  const petImg = document.getElementById('sous-paw-pet');
  let currentIndex = 0;

  const updatePetImage = (text) => {
        const lowerText = text.toLowerCase();

        const match = Object.keys(ACTION_MAP)
            .sort((a, b) => b.length - a.length)
            .find(key => lowerText.includes(key.toLowerCase()));
            
        const actionPart = match ? ACTION_MAP[match] : ACTION_MAP.default;
        
        const fileName = `${genderInit}_${species}_${actionPart}.jpg`;

        petImg.style.opacity = 0.4;
        petImg.src = GITHUB_BASE + fileName;
        
        petImg.onload = () => petImg.style.opacity = 1;
        
        petImg.onerror = () => {
            petImg.src = `${GITHUB_BASE}${genderInit}_${species}_design.png`;
            petImg.style.opacity = 1;
        };
    };

  const renderStep = () => {
    const percentComplete = Math.round(((currentIndex + 1) / steps.length) * 100);
    const stepText = steps[currentIndex];
    progress.textContent = `Step ${currentIndex + 1} of ${steps.length}`;
    progressPercent.textContent = `${percentComplete}% complete`;
    current.textContent = steps[currentIndex];
    prevButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === steps.length - 1;
    progressFill.style.width = `${percentComplete}%`;
    updatePetImage(stepText);
  };

  if (startButton && panel) {
    startButton.addEventListener("click", () => {
      currentIndex = 0;
      panel.hidden = false;
      startButton.hidden = true;
      renderStep();
    });
  } else {
    renderStep();
  }

  prevButton.addEventListener("click", () => {
    if (currentIndex === 0) {
      return;
    }

    currentIndex -= 1;
    renderStep();
  });

  nextButton.addEventListener("click", () => {
    if (currentIndex === steps.length - 1) {
      return;
    }

    currentIndex += 1;
    renderStep();
  });

  restartButton.addEventListener("click", () => {
    currentIndex = 0;
    progressFill.style.width = "0%";
    renderStep();
  });
});
