/**
 * Clinic Locator JavaScript Module
 * Handles map initialization, geolocation, search, and result display
 */

class ClinicLocator {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentLocation = null;
        this.infoWindows = [];
        this.init();
    }

    init() {
        // Initialize map
        this.initMap();
        
        // Bind event listeners
        this.bindEvents();
        
        // Request geolocation
        this.requestGeolocation();
    }

    initMap() {
        const defaultCenter = { lat: 40.7128, lng: -74.0060 }; // New York
        
        this.map = new google.maps.Map(document.getElementById('map'), {
            zoom: 15,
            center: defaultCenter,
            styles: this.getMapStyles(),
        });
    }

    getMapStyles() {
        return [
            {
                featureType: 'water',
                stylers: [{ color: '#e8f4f8' }],
            },
            {
                featureType: 'road',
                stylers: [{ color: '#ffffff' }],
            },
            {
                featureType: 'landscape',
                stylers: [{ color: '#f3f3f3' }],
            },
        ];
    }

    bindEvents() {
        document.getElementById('searchBtn').addEventListener('click', () => this.search());
        document.getElementById('searchQuery').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
        
        document.getElementById('currentLocationBtn').addEventListener('click', () => {
            this.requestGeolocation();
        });

        document.getElementById('savedClinicsBtn').addEventListener('click', () => {
            window.location.href = '/locator/saved/';
        });

        document.getElementById('radiusSelect').addEventListener('change', () => {
            if (this.currentLocation) {
                this.search();
            }
        });
    }

    requestGeolocation() {
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by your browser');
            return;
        }

        this.showLoading(true);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                this.map.setCenter(this.currentLocation);
                this.addMarker(this.currentLocation, 'Your Location', 'blue');
                this.search();
                this.showLoading(false);
            },
            (error) => {
                this.handleGeolocationError(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0,
            }
        );
    }

    handleGeolocationError(error) {
        this.showLoading(false);
        let message = '';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                document.getElementById('geoErrorMessage').style.display = 'block';
                message = 'Geolocation permission denied. Please enable location services.';
                break;
            case error.POSITION_UNAVAILABLE:
                message = 'Location information unavailable.';
                break;
            case error.TIMEOUT:
                message = 'Geolocation request timed out.';
                break;
            default:
                message = 'Error requesting geolocation.';
        }
        
        console.warn(message);
    }

    search() {
        if (!this.currentLocation) {
            this.showError('Please enable geolocation or search from your current location');
            return;
        }

        this.showLoading(true);

        const query = document.getElementById('searchQuery').value;
        const radius = parseInt(document.getElementById('radiusSelect').value);

        const params = new URLSearchParams({
            latitude: this.currentLocation.lat,
            longitude: this.currentLocation.lng,
            radius: radius,
            query: query,
        });

        fetch(`/locator/api/nearby/?${params}`)
            .then((response) => response.json())
            .then((data) => this.handleSearchResults(data))
            .catch((error) => {
                console.error('Search error:', error);
                this.showError('Error searching for nearby clinics');
                this.showLoading(false);
            });
    }

    handleSearchResults(data) {
        this.showLoading(false);

        if (!data.success) {
            this.showError(data.error || 'Error searching for clinics');
            return;
        }

        this.clearMarkers();
        this.displayResults(data.results);

        if (data.results.length === 0) {
            this.showError('No clinics found in this area');
        } else {
            this.showSuccess(`Found ${data.count} clinic${data.count !== 1 ? 's' : ''}`);
        }
    }

    displayResults(results) {
        const resultsList = document.getElementById('resultsList');
        resultsList.innerHTML = '';

        const resultCount = document.getElementById('resultCount');
        resultCount.textContent = `${results.length} clinic${results.length !== 1 ? 's' : ''} found`;

        results.forEach((location) => {
            // Add marker to map
            this.addMarker(
                { lat: location.latitude, lng: location.longitude },
                location.name,
                'red',
                location
            );

            // Create result card
            const card = this.createResultCard(location);
            resultsList.appendChild(card);
        });

        // Fit map bounds to all markers
        if (results.length > 0) {
            this.fitMapBounds();
        }
    }

    createResultCard(location) {
        const template = document.getElementById('resultCardTemplate');
        const card = template.content.cloneNode(true);

        const cardElement = card.querySelector('.result-card');
        cardElement.dataset.placeId = location.place_id;
        cardElement.dataset.locationData = JSON.stringify(location);

        card.querySelector('.result-card h3').textContent = location.name;
        card.querySelector('.result-address').textContent = location.address;

        const distanceKm = (location.distance_meters / 1000).toFixed(1);
        card.querySelector('.result-distance').textContent = `${distanceKm} km away`;

        if (location.rating) {
            card.querySelector('.result-rating').textContent = `★ ${location.rating.toFixed(1)}`;
        } else {
            card.querySelector('.result-rating').style.display = 'none';
        }

        if (location.phone) {
            card.querySelector('.result-phone span').textContent = location.phone;
        } else {
            card.querySelector('.result-phone').style.display = 'none';
        }

        if (location.website) {
            const link = card.querySelector('.result-website a');
            link.href = location.website;
            link.textContent = location.website;
        } else {
            card.querySelector('.result-website').style.display = 'none';
        }

        const directionsLink = card.querySelector('.result-directions');
        directionsLink.href = `https://www.google.com/maps/dir/?api=1&destination=${location.latitude},${location.longitude}`;

        // Save button
        const saveBtn = card.querySelector('.save-clinic-btn');
        if (location.is_saved) {
            saveBtn.textContent = '★';
            saveBtn.classList.add('saved');
        }

        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSaveClinic(location, saveBtn);
        });

        // Center map on click
        cardElement.addEventListener('click', () => {
            this.map.setCenter({ lat: location.latitude, lng: location.longitude });
            this.map.setZoom(17);
        });

        return card;
    }

    toggleSaveClinic(location, btn) {
        if (!this.isUserAuthenticated()) {
            window.location.href = '/accounts/login/?next=/locator/';
            return;
        }

        const isSaved = btn.classList.contains('saved');
        const endpoint = isSaved ? '/locator/api/remove/' : '/locator/api/save/';

        const payload = isSaved
            ? { clinic_id: this.getClinicIdFromPlaceId(location.place_id) }
            : {
                  place_id: location.place_id,
                  name: location.name,
                  address: location.address,
                  latitude: location.latitude,
                  longitude: location.longitude,
                  phone: location.phone || '',
                  website: location.website || '',
              };

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    if (isSaved) {
                        btn.textContent = '☆';
                        btn.classList.remove('saved');
                        location.is_saved = false;
                    } else {
                        btn.textContent = '★';
                        btn.classList.add('saved');
                        location.is_saved = true;
                    }
                    this.showSuccess(data.message);
                } else {
                    this.showError(data.error || 'Error saving clinic');
                }
            })
            .catch((error) => {
                console.error('Save clinic error:', error);
                this.showError('Error saving clinic');
            });
    }

    getClinicIdFromPlaceId(placeId) {
        // In a real implementation, you'd need to fetch this from your backend
        // For now, return a dummy value
        return null;
    }

    isUserAuthenticated() {
        // Check if user is authenticated (this would need to be exposed in template)
        return document.documentElement.classList.contains('authenticated') ||
               document.body.classList.contains('authenticated') ||
               !!document.querySelector('[data-authenticated]');
    }

    addMarker(position, title, color = 'red', location = null) {
        const marker = new google.maps.Marker({
            position: position,
            map: this.map,
            title: title,
            icon: this.getMarkerIcon(color),
        });

        if (location) {
            const infoWindow = new google.maps.InfoWindow({
                content: this.createInfoWindowContent(location),
            });

            marker.addListener('click', () => {
                // Close all other info windows
                this.infoWindows.forEach((iw) => iw.close());
                infoWindow.open(this.map, marker);
                this.infoWindows = [infoWindow];
            });
        }

        this.markers.push(marker);
    }

    createInfoWindowContent(location) {
        return `
            <div style="max-width: 250px;">
                <h4 style="margin: 0 0 8px 0;">${location.name}</h4>
                <p style="margin: 0 0 4px 0; font-size: 0.9em;">${location.address}</p>
                ${location.distance_meters ? `<p style="margin: 0 0 4px 0; font-size: 0.9em; color: #667eea;">📍 ${(location.distance_meters / 1000).toFixed(1)} km away</p>` : ''}
                ${location.phone ? `<p style="margin: 0; font-size: 0.9em;">📞 ${location.phone}</p>` : ''}
            </div>
        `;
    }

    getMarkerIcon(color) {
        return {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: color,
            fillOpacity: 0.8,
            strokeColor: 'white',
            strokeWeight: 2,
        };
    }

    clearMarkers() {
        this.markers.forEach((marker) => marker.setMap(null));
        this.markers = [];
        this.infoWindows.forEach((iw) => iw.close());
        this.infoWindows = [];
    }

    fitMapBounds() {
        if (this.markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        this.markers.forEach((marker) => bounds.extend(marker.getPosition()));
        this.map.fitBounds(bounds);

        // Add padding
        const listener = google.maps.event.addListener(this.map, 'idle', () => {
            this.map.setZoom(Math.max(this.map.getZoom() - 1, 15));
            google.maps.event.removeListener(listener);
        });
    }

    showLoading(show) {
        const loading = document.getElementById('loadingMessage');
        if (show) {
            loading.style.display = 'flex';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('successMessage').style.display = 'none';
        } else {
            loading.style.display = 'none';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'flex';
        document.getElementById('successMessage').style.display = 'none';
    }

    showSuccess(message) {
        const successDiv = document.getElementById('successMessage');
        successDiv.textContent = message;
        successDiv.style.display = 'flex';
        document.getElementById('errorMessage').style.display = 'none';
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.clinicLocator = new ClinicLocator();
});
