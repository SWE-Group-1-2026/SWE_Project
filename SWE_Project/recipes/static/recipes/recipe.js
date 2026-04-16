document.addEventListener("DOMContentLoaded", () => {
  const player = document.querySelector("[data-step-player]");

  if (!player) {
    return;
  }

  const steps = Array.from(document.querySelectorAll("[data-recipe-step]"))
    .map((step) => step.textContent.trim())
    .filter(Boolean);

  if (!steps.length) {
    return;
  }

  const startButton = player.querySelector("[data-start-button]");
  const panel = player.querySelector("[data-step-panel]");
  const progress = player.querySelector("[data-step-progress]");
  const progressFill = player.querySelector("[data-progress-fill]");
  const current = player.querySelector("[data-step-current]");
  const prevButton = player.querySelector("[data-prev-button]");
  const nextButton = player.querySelector("[data-next-button]");
  const restartButton = player.querySelector("[data-restart-button]");

  let currentIndex = 0;

  const renderStep = () => {
    progress.textContent = `Step ${currentIndex + 1} of ${steps.length}`;
    current.textContent = steps[currentIndex];
    prevButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === steps.length - 1;
    progressFill.style.width = `${((currentIndex + 1) / steps.length) * 100}%`;
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
    renderStep();
  });
});
