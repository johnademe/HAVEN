// autocomplete.js — Item and category autocomplete

async function loadItems() {
    try {
        AppState.allItems = (await api('/items')) || [];
    } catch {}
}

async function loadCategories() {
    try {
        const cats = await api('/expense-categories');
        AppState.allCategories = cats.map(c => c.category) || [];
    } catch {
        AppState.allCategories = [
            'Office Supplies', 'Utilities', 'Rent', 'Software',
            'Marketing', 'Salaries', 'Travel', 'Other'
        ];
    }
}

function autocompleteItems(input) {
    const val = input.value.toLowerCase();
    const list = document.getElementById('autocompleteList');
    if (!val) { list.classList.remove('open'); return; }
    const matches = AppState.allItems.filter(i => i.item_name.toLowerCase().includes(val)).slice(0, 10);
    if (!matches.length) { list.classList.remove('open'); return; }
    list.innerHTML = matches.map(i =>
        `<div class="ac-item" onclick="selectItem('${i.item_name.replace(/'/g,"\\'")}',${i.default_price})">
            <span>${i.item_name}</span><span class="ac-price">$${i.default_price}</span>
        </div>`
    ).join('');
    list.classList.add('open');
}

function selectItem(name, price) {
    document.getElementById('saleItem').value = name;
    document.getElementById('salePrice').value = price;
    document.getElementById('autocompleteList').classList.remove('open');
}

function autocompleteCategories(input) {
    const val = input.value.toLowerCase();
    const list = document.getElementById('categoryAutocompleteList');
    if (!val) { list.classList.remove('open'); return; }
    const matches = AppState.allCategories.filter(c => c.toLowerCase().includes(val)).slice(0, 10);
    if (!matches.length) {
        list.innerHTML =
            `<div class="ac-item" onclick="selectCategory('${input.value.replace(/'/g,"\\'")}')">
                <span class="ac-create"><i class="fas fa-plus" style="margin-right:8px"></i>Create "${input.value}"</span>
            </div>`;
    } else {
        list.innerHTML = matches.map(c =>
            `<div class="ac-item" onclick="selectCategory('${c.replace(/'/g,"\\'")}')"><span>${c}</span></div>`
        ).join('');
    }
    list.classList.add('open');
}

function selectCategory(name) {
    document.getElementById('expenseCategory').value = name;
    document.getElementById('categoryAutocompleteList').classList.remove('open');
    if (!AppState.allCategories.includes(name)) AppState.allCategories.push(name);
}

// Close autocomplete when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.ac-wrap')) {
        document.querySelectorAll('.ac-list').forEach(l => l.classList.remove('open'));
    }
});
