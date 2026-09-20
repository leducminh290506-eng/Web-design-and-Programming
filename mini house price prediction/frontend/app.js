document.addEventListener('DOMContentLoaded', () => {
    fetchData();

    const form = document.getElementById('item-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

function showAlert(message, type = 'error') {
    const alertBox = document.getElementById('alert-box');
    if (!alertBox) {
        alert(`${type.toUpperCase()}: ${message}`);
        return;
    }
    
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    alertBox.style.display = 'block';

    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 4000);
}

function resetForm() {
    const form = document.getElementById('item-form');
    if (form) form.reset();

    const itemId = document.getElementById('item-id');
    if (itemId) itemId.value = '';

    const formTitle = document.getElementById('form-title');
    if (formTitle) formTitle.textContent = 'Add New Item';

    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.textContent = 'Add Item';

    const cancelBtn = document.getElementById('cancel-btn');
    if (cancelBtn) cancelBtn.style.display = 'none';
}

async function fetchData() {
    const tbody = document.getElementById('items-tbody') || document.querySelector('tbody');
    if (!tbody) return;

    try {
        const response = await fetch('/items');
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `HTTP Error ${response.status}`);
        }

        const rawData = await response.json();
        const data = Array.isArray(rawData) ? rawData : (rawData.items || []);
        tbody.innerHTML = '';

        if (data && data.length > 0) {
            for (const item of data) {
                const row = document.createElement('tr');
                const stockBadge = item.in_stock
                    ? '<span class="badge badge-success">In Stock</span>'
                    : '<span class="badge badge-danger">Out of Stock</span>';

                row.innerHTML = `
                    <td><strong>#${item.id}</strong></td>
                    <td>${escapeHtml(item.name)}</td>
                    <td>$${Number(item.price).toFixed(2)}</td>
                    <td>${stockBadge}</td>
                    <td>
                        <div class="action-btns">
                            <button class="btn btn-edit" onclick="handleEdit(${item.id})">Edit</button>
                            <button class="btn btn-danger" onclick="handleDelete(${item.id})">Delete</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            }
        } else {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #64748b;">No items found.</td></tr>`;
        }
    } catch (error) {
        console.error('Fetch data failed:', error);
        showAlert(`Failed to load items: ${error.message}`, 'error');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const itemId = document.getElementById('item-id').value;
    const name = document.getElementById('item-name').value.trim();
    const price = parseFloat(document.getElementById('item-price').value);
    const in_stock = document.getElementById('item-stock').checked;

    if (!name || isNaN(price)) {
        showAlert('Please fill in valid name and price.', 'error');
        return;
    }

    const payload = { name, price, in_stock };
    const isEdit = Boolean(itemId);
    const url = isEdit ? `/items/${itemId}` : '/items';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            let msg = 'Request failed';
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    msg = errorData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ');
                } else {
                    msg = errorData.detail;
                }
            }
            throw new Error(msg);
        }

        resetForm();
        fetchData();
    } catch (error) {
        console.error('Save item error:', error);
        showAlert(`Error saving item: ${error.message}`, 'error');
    }
}

async function handleEdit(id) {
    try {
        const response = await fetch(`/items/${id}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch item details');
        }

        const item = await response.json();
        const itemId = document.getElementById('item-id');
        if (itemId) itemId.value = item.id;

        const itemName = document.getElementById('item-name');
        if (itemName) itemName.value = item.name;

        const itemPrice = document.getElementById('item-price');
        if (itemPrice) itemPrice.value = item.price;

        const itemStock = document.getElementById('item-stock');
        if (itemStock) itemStock.checked = Boolean(item.in_stock);

        const formTitle = document.getElementById('form-title');
        if (formTitle) formTitle.textContent = `Edit Item #${item.id}`;

        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) submitBtn.textContent = 'Update Item';

        const cancelBtn = document.getElementById('cancel-btn');
        if (cancelBtn) cancelBtn.style.display = 'inline-flex';

        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error('Fetch item detail error:', error);
        showAlert(error.message, 'error');
    }
}

async function handleDelete(id) {
    try {
        const response = await fetch(`/items/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok && response.status !== 204) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to delete item #${id}`);
        }

        showAlert(`Item #${id} deleted successfully.`, 'success');
        fetchData();
    } catch (error) {
        console.error('Delete item error:', error);
        showAlert(`Delete failed: ${error.message}`, 'error');
    }
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
