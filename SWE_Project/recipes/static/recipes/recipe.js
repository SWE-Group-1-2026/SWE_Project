document.addEventListener("DOMContentLoaded", () => {
  const player = document.querySelector("[data-step-player]");
  const petConfig = document.getElementById("pet-config");
  if (!player || !petConfig) {
    return;
  }
  const genderInit = petConfig.getAttribute("data-gender").charAt(0).toUpperCase();
  const species = petConfig.getAttribute("data-species").toUpperCase();

  const ACTION_MAP = {
        "shredded":"SHREDDING",
        "a pot":"POT",
        "mash":"WHISKING",
        "combine":"COMBINE",
        "season":"SEASONING",
        "serve": "SERVE",
        "whisk": "WHISKING",
        "rolling":"ROLLING",
        "roll":"ROLLING",
        "mix":"WHISKING",
        "beat eggs":"WHISKING",
        "beat butter":"WHISKING",
        "frost":"FROSTING",
        "frosting the cake":"FROSTING",
        "mixer": "MIXER",
        "mixing":"MIXER",
        "griddle": "GRIDDLE",
        "toast the bread": "TOASTER",
        "toast pecans":"OVEN",
        "blend": "BLENDING",
        "blend the soup": "POT",
        "blender": "BLENDING",
        "a pan":"PAN",
        "garnish":"SEASONING",
        "sprinkle":"SEASONING",
        "bake": "OVEN",
        "oven": "OVEN",
        "chop": "CHOPPING",
        "slice": "CHOPPING",
        "cut": "CHOPPING",
        "stir":"POT",
        "boil":"POT",
        "boiling":"POT",
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
  let timerInterval = null;
  let timerRemaining = 0;
  let timerTotal = 0;
  let timerRunning = false;

  const timerBlock = player.querySelector("[data-step-timer]");
  const timerDisplay = player.querySelector("[data-timer-display]");
  const timerLabel = player.querySelector("[data-timer-label]");
  const timerToggle = player.querySelector("[data-timer-toggle]");
  const timerReset = player.querySelector("[data-timer-reset]");

  const parseTimeFromStep = (text) => {
    const patterns = [
        { regex: /(\d+)\s*hour[s]?\s*(?:and\s*)?(\d+)\s*min(?:ute)?s?/i, fn: (m) => parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 },
        { regex: /(\d+)\s*hour[s]?/i, fn: (m) => parseInt(m[1]) * 3600 },
        { regex: /(\d+)\s*min(?:ute)?s?/i, fn: (m) => parseInt(m[1]) * 60 },
        { regex: /(\d+)\s*sec(?:ond)?s?/i, fn: (m) => parseInt(m[1]) },
    ];
    for (const { regex, fn } of patterns) {
        const match = text.match(regex);
        if (match) return fn(match);
    }
    return null;
  };

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  };

  const stopTimer = () => {
    clearInterval(timerInterval);
    timerInterval = null;
    timerRunning = false;
    if (timerToggle) timerToggle.textContent = "Start Timer";
  };

  const resetTimer = () => {
    stopTimer();
    timerRemaining = timerTotal;
    if (timerDisplay) timerDisplay.textContent = formatTime(timerRemaining);
  };

  const setupTimer = (stepText) => {
    stopTimer();
    const seconds = parseTimeFromStep(stepText);
    if (!seconds || !timerBlock) return;
    timerTotal = seconds;
    timerRemaining = seconds;
    timerBlock.style.display = "block";
    timerLabel.textContent = `Detected: ${formatTime(seconds)}`;
    timerDisplay.textContent = formatTime(timerRemaining);
    timerToggle.textContent = "Start Timer";
  };

  timerToggle && timerToggle.addEventListener("click", () => {
    if (timerRunning) {
        stopTimer();
    } else {
        if (timerRemaining <= 0) timerRemaining = timerTotal;
        timerRunning = true;
        timerToggle.textContent = "Pause";
        timerInterval = setInterval(() => {
            timerRemaining -= 1;
            timerDisplay.textContent = formatTime(timerRemaining);
            if (timerRemaining <= 0) {
                stopTimer();
                timerToggle.textContent = "Done!";
                timerToggle.disabled = true;
            }
        }, 1000);
    }
  });

  timerReset && timerReset.addEventListener("click", () => {
    timerToggle.disabled = false;
    resetTimer();
  });

  const updatePetImage = (text) => {
        const lowerText = text.toLowerCase();

        const match = Object.keys(ACTION_MAP)
            .sort((a, b) => b.length - a.length)
            .find(key => {
              const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
              const regex = new RegExp(`\\b${escaped}\\b`, 'i');
              return regex.test(lowerText);
            });
            
        const actionPart = match ? ACTION_MAP[match] : ACTION_MAP.default;
        
        const fileName = `${genderInit}_${species}_${actionPart}.jpg`;
        const localPath = `/static/recipes/images/${fileName}`;

        if (petImg) {
            petImg.style.opacity = 0.4;
            petImg.src = localPath;
            petImg.onload = () => petImg.style.opacity = 1;

            petImg.onerror = () => {
                petImg.onerror = null;
                petImg.src = `/static/recipes/images/${genderInit}_${species}_design.jpg`;
                petImg.style.opacity = 1;
            };
        }
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
    if (currentIndex === steps.length - 1) {
        const fileName = `${genderInit}_${species}_SERVE.jpg`;
        if (petImg) {
            petImg.style.opacity = 0.4;
            petImg.src = `/static/recipes/images/${fileName}`;
            petImg.onload = () => petImg.style.opacity = 1;
            petImg.onerror = () => {
                petImg.onerror = null;
                petImg.src = `/static/recipes/images/${genderInit}_${species}_design.jpg`;
                petImg.style.opacity = 1;
            };
        }
        if (timerBlock) timerBlock.style.display = "none";
    } else {
        if (timerBlock) timerBlock.style.display = "none";
        setupTimer(stepText);
        updatePetImage(stepText);
    }
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
