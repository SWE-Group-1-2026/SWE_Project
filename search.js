//placeholder test values before database implementation with mongodb
const recipes = [
    { name: "Classic Tonkotsu Ramen", cuisine: "Japanese", time: "45 min" },
    { name: "Spicy Street Tacos", cuisine: "Mexican", time: "20 min" },
    { name: "Creamy Pesto Pasta", cuisine: "Italian", time: "15 min" },
    { name: "Butter Chicken", cuisine: "Indian", time: "40 min" },
    { name: "Avocado Toast Deluxe", cuisine: "Breakfast", time: "10 min" }
];

function filterRecipes() {
    const query = document.getElementById('recipeSearch').value.toLowerCase();
    const resultsGrid = document.getElementById('resultsGrid');
    
    resultsGrid.innerHTML = '';

    const filtered = recipes.filter(r => 
        r.name.toLowerCase().includes(query) || 
        r.cuisine.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        resultsGrid.innerHTML = '<p class="placeholder-text">No recipes found. Try another keyword!</p>';
        return;
    }

    filtered.forEach(recipe => {
        const card = document.createElement('div');
        card.style.cssText = "background: white; padding: 20px; border-radius: 12px; text-align: left; box-shadow: 0 4px 6px rgba(0,0,0,0.05);";
        card.innerHTML = `
            <h3 style="margin: 0 0 10px 0;">${recipe.name}</h3>
            <span style="background: #DDE5B6; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">${recipe.cuisine}</span>
            <span style="margin-left: 10px; font-size: 0.8rem; color: #888;">⏱️ ${recipe.time}</span>
        `;
        resultsGrid.appendChild(card);
    });
}
