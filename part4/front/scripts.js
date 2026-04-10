/*
 * HBnB Part 4 - scripts.js
 * Handles: login, places list with filter, place details, add review
 */

const API_URL = 'http://127.0.0.1:5000/api/v1';

/* ─────────────────────────────────────────────
   UTILITY FUNCTIONS
───────────────────────────────────────────── */

/**
 * Get a cookie value by its name
 * @param {string} name - the cookie name
 * @returns {string|null} the cookie value or null
 */
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
    }
    return null;
}

/**
 * Set a cookie
 * @param {string} name - cookie name
 * @param {string} value - cookie value
 */
function setCookie(name, value) {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/`;
}

/**
 * Get a URL query parameter by name
 * @param {string} param - parameter name
 * @returns {string|null}
 */
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

/**
 * Show a status message in the UI
 * @param {string} elementId - ID of the message div
 * @param {string} text - message text
 * @param {string} type - 'success' or 'error'
 */
function showMessage(elementId, text, type) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = text;
    el.className = `message ${type}`;
    el.style.display = 'block';
}

/* ─────────────────────────────────────────────
   TASK 2 — LOGIN
───────────────────────────────────────────── */

/**
 * Setup login form event listener
 * On submit: POST credentials to API, store token in cookie, redirect to index
 */
function setupLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                /* Store the JWT token in a cookie */
                setCookie('token', data.access_token);
                window.location.href = 'index.html';
            } else {
                showMessage('login-message', 'Invalid email or password.', 'error');
            }
        } catch (error) {
            showMessage('login-message', 'Connection error. Please try again.', 'error');
        }
    });
}

/* ─────────────────────────────────────────────
   TASK 3 — INDEX PAGE (list of places)
───────────────────────────────────────────── */

/**
 * Check authentication and control login link visibility on index page
 * If token found: hide login link and fetch places
 * If no token: show login link but still fetch places (public endpoint)
 */
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'none';
    }

    /* Always fetch places — public endpoint */
    fetchPlaces(token);
}

/**
 * Fetch all places from the API
 * @param {string|null} token - JWT token for auth header
 */
async function fetchPlaces(token) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const response = await fetch(`${API_URL}/places/`, { headers });
        if (response.ok) {
            const places = await response.json();
            displayPlaces(places);
        }
    } catch (error) {
        console.error('Error fetching places:', error);
    }
}

/**
 * Dynamically create and display place cards in #places-list
 * @param {Array} places - array of place objects from API
 */
function displayPlaces(places) {
    const list = document.getElementById('places-list');
    if (!list) return;
    list.innerHTML = '';

    if (!places || places.length === 0) {
        list.innerHTML = '<p style="text-align:center;color:#888;">No places available.</p>';
        return;
    }

    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.dataset.price = place.price || 0;

        card.innerHTML = `
            <h2>${place.title || place.name || 'Unnamed Place'}</h2>
            <p>Price per night: $${place.price || 0}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        list.appendChild(card);
    });

    /* Setup price filter after cards are created */
    setupPriceFilter();
}

/**
 * Setup client-side price filter
 * Filters place cards based on selected max price without page reload
 */
function setupPriceFilter() {
    const filter = document.getElementById('price-filter');
    if (!filter) return;

    filter.addEventListener('change', (event) => {
        const selected = event.target.value;
        const cards = document.querySelectorAll('.place-card');

        cards.forEach(card => {
            const price = parseFloat(card.dataset.price);
            if (selected === 'all' || price <= parseFloat(selected)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

/* ─────────────────────────────────────────────
   TASK 4 — PLACE DETAILS PAGE
───────────────────────────────────────────── */

/**
 * Initialize place details page
 * Check auth, get place ID from URL, fetch and display details
 */
function initPlacePage() {
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();
    const loginLink = document.getElementById('login-link');
    const addReviewSection = document.getElementById('add-review');

    /* Redirect if no place ID */
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    /* Show/hide login link and add review section based on auth */
    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
        if (addReviewSection) addReviewSection.style.display = 'none';
    } else {
        if (loginLink) loginLink.style.display = 'none';
        if (addReviewSection) addReviewSection.style.display = 'block';
    }

    fetchPlaceDetails(token, placeId);
}

/**
 * Fetch details for a specific place
 * @param {string|null} token - JWT token
 * @param {string} placeId - place ID from URL
 */
async function fetchPlaceDetails(token, placeId) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const response = await fetch(`${API_URL}/places/${placeId}`, { headers });
        if (response.ok) {
            const place = await response.json();
            displayPlaceDetails(place);
        } else {
            const section = document.getElementById('place-details');
            if (section) section.innerHTML = '<p style="color:#888;">Place not found.</p>';
        }
    } catch (error) {
        console.error('Error fetching place details:', error);
    }
}

/**
 * Display place details in #place-details and reviews in #reviews
 * @param {Object} place - place object from API
 */
function displayPlaceDetails(place) {
    const section = document.getElementById('place-details');
    if (!section) return;

    /* Build amenities string */
    let amenitiesStr = 'None';
    if (place.amenities && place.amenities.length > 0) {
        amenitiesStr = place.amenities.map(a => a.name || a).join(', ');
    }

    /* Owner name */
    const ownerName = place.owner
        ? `${place.owner.first_name || ''} ${place.owner.last_name || ''}`.trim()
        : 'N/A';

    /* Place title shown above details box */
    const titleEl = document.createElement('h1');
    titleEl.className = 'page-title';
    titleEl.textContent = place.title || place.name || 'Place Details';
    section.parentNode.insertBefore(titleEl, section);

    section.innerHTML = `
        <div class="place-details">
            <div class="place-info">
                <p><strong>Host:</strong> ${ownerName}</p>
                <p><strong>Price per night:</strong> $${place.price || 0}</p>
                <p><strong>Description:</strong> ${place.description || 'No description.'}</p>
                <p><strong>Amenities:</strong> ${amenitiesStr}</p>
            </div>
        </div>
    `;

    /* Display reviews */
    const reviewsSection = document.getElementById('reviews');
    if (reviewsSection) {
        let html = '<h2>Reviews</h2>';
        if (place.reviews && place.reviews.length > 0) {
            place.reviews.forEach(review => {
                const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
                const userName = review.user
                    ? `${review.user.first_name || ''} ${review.user.last_name || ''}`.trim()
                    : 'Anonymous';
                html += `
                    <div class="review-card">
                        <p><strong>${userName}:</strong></p>
                        <p>${review.text}</p>
                        <p>Rating: ${stars}</p>
                    </div>
                `;
            });
        } else {
            html += '<p style="color:#888;">No reviews yet.</p>';
        }
        reviewsSection.innerHTML = html;
    }

    /* Setup inline review form */
    setupPlaceReviewForm(place.id);
}

/**
 * Setup inline review form on place.html
 * @param {string} placeId - place ID
 */
function setupPlaceReviewForm(placeId) {
    const form = document.getElementById('review-form');
    if (!form) return;
    const token = getCookie('token');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const text = document.getElementById('review-text').value;
        const rating = parseInt(document.getElementById('rating').value);
        await submitReview(token, placeId, text, rating, 'review-message');
    });
}

/* ─────────────────────────────────────────────
   TASK 5 — ADD REVIEW PAGE
───────────────────────────────────────────── */

/**
 * Initialize add review page
 * Redirect unauthenticated users to index
 * Setup form submission
 */
function initAddReviewPage() {
    const token = getCookie('token');

    /* Unauthenticated users go back to index */
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const placeId = getPlaceIdFromURL();
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    /* Update page title with place name if available */
    fetchPlaceName(token, placeId);

    const form = document.getElementById('review-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const text = document.getElementById('review').value;
        const rating = parseInt(document.getElementById('rating').value);
        await submitReview(token, placeId, text, rating, 'review-message');
    });
}

/**
 * Fetch place name to display in add_review page title
 * @param {string} token - JWT token
 * @param {string} placeId - place ID
 */
async function fetchPlaceName(token, placeId) {
    try {
        const response = await fetch(`${API_URL}/places/${placeId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const place = await response.json();
            const titleEl = document.getElementById('place-title');
            if (titleEl) {
                titleEl.textContent = `Reviewing: ${place.title || place.name || 'Place'}`;
            }
        }
    } catch (error) {
        console.error('Error fetching place name:', error);
    }
}

/**
 * Submit a review to the API
 * @param {string} token - JWT token
 * @param {string} placeId - place ID
 * @param {string} text - review text
 * @param {number} rating - rating 1-5
 * @param {string} messageId - ID of message div to show feedback
 */
async function submitReview(token, placeId, text, rating, messageId) {
    try {
        const response = await fetch(`${API_URL}/reviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                text,
                rating,
                place_id: placeId
            })
        });

        handleResponse(response, messageId);
    } catch (error) {
        showMessage(messageId, 'Connection error. Please try again.', 'error');
    }
}

/**
 * Handle API response after review submission
 * @param {Response} response - fetch response
 * @param {string} messageId - ID of message div
 */
function handleResponse(response, messageId) {
    if (response.ok) {
        showMessage(messageId, 'Review submitted successfully!', 'success');
        const form = document.getElementById('review-form');
        if (form) form.reset();
    } else {
        showMessage(messageId, 'Failed to submit review. Please try again.', 'error');
    }
}

/* ─────────────────────────────────────────────
   ROUTER — detect current page and initialize
───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('login.html')) {
        setupLoginForm();
    } else if (path.includes('add_review.html')) {
        initAddReviewPage();
    } else if (path.includes('place.html')) {
        initPlacePage();
    } else {
        /* index.html or root */
        checkAuthentication();
    }
});