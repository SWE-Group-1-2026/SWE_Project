const searchInput = document.getElementById("recipeSearch");
const searchForm = document.querySelector(".search-form");
const resultsGrid = document.getElementById("resultsGrid");
const searchStatus = document.getElementById("searchStatus");

let activeController = null;
let debounceTimer = null;

function recipeCardMarkup(recipe) {
  return `
    <article class="recipe-card">
      <h3>${recipe.name}</h3>
      <div class="recipe-meta">
        <span class="recipe-tag">${recipe.cuisine || "Unknown cuisine"}</span>
        <span class="recipe-time">⏱️ ${recipe.time || "N/A"}</span>
      </div>
      <a href="/recipe/${recipe.id}/" class="view-link">View Recipe</a>
    </article>
  `;
}

function renderResults(data) {
  if (data.error_message) {
    searchStatus.textContent = data.error_message;
    searchStatus.hidden = false;
  } else {
    searchStatus.hidden = true;
    searchStatus.textContent = "";
  }

  if (!data.recipes.length) {
    resultsGrid.innerHTML = `<p class="placeholder-text">${
      data.error_message || "No recipes found yet. Try another keyword."
    }</p>`;
    return;
  }

  resultsGrid.innerHTML = data.recipes.map(recipeCardMarkup).join("");
}

async function fetchRecipes(query) {
  if (activeController) {
    activeController.abort();
  }

  activeController = new AbortController();
  const params = new URLSearchParams();

  if (query.trim()) {
    params.set("search", query.trim());
  }

  try {
    const response = await fetch(`/recipes/?${params.toString()}`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      signal: activeController.signal,
    });

    if (!response.ok) {
      throw new Error("Search request failed.");
    }

    const data = await response.json();
    renderResults(data);
  } catch (error) {
    if (error.name === "AbortError") {
      return;
    }

    searchStatus.textContent = "Live search is temporarily unavailable.";
    searchStatus.hidden = false;
  }
}

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  fetchRecipes(searchInput.value);
});

searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchRecipes(searchInput.value);
  }, 250);
});
