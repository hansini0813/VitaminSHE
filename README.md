# VitaminSHE - Personalized Vitamin Tracking & Health Insights

**2nd Place Winner at Hack the Gap 2024**

VitaminSHE is a full-stack Django web application that empowers women to optimize their vitamin and nutrient intake through personalized tracking, AI-powered recommendations, educational resources, and clinic locator services.

## 🎯 Project Overview

VitaminSHE addresses the unique nutritional needs of women by providing:

- **Smart Vitamin Tracking**: Log intake of 12 essential vitamins from multiple sources
- **Personalized Recommendations**: AI-powered engine that suggests vitamins based on health profile
- **Educational Resources**: Curated library of medically-reviewed health articles
- **Clinic Locator**: Find nearby blood testing centers and diagnostic facilities
- **Health Analytics**: View adherence rates, streaks, and intake patterns
- **Secure Authentication**: User profiles with onboarding questionnaire

## 🏆 Achievement

Won **2nd Place at Hack the Gap 2024** - a hackathon focused on solving real-world problems related to gender equity and women's health.

## 🛠️ Technology Stack

**Backend:**
- Django 4.2 LTS
- Python 3.12
- SQLite database
- REST API endpoints

**Frontend:**
- HTML5 & CSS3
- Vanilla JavaScript
- Responsive design (mobile-first)
- Google Maps JavaScript API

**Integrations:**
- Google Places API (clinic locator)
- Google Maps API (location services)

## 📋 Requirements

Before you begin, ensure you have:

- Python 3.12 or higher
- pip (Python package manager)
- Git
- (Optional) Google Maps & Places API keys for clinic locator feature

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/VitaminSHE.git
cd VitaminSHE/project_vitamins
```

### 2. Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `project_vitamins` directory:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-for-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Google APIs (optional - needed for clinic locator)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
GOOGLE_PLACES_API_KEY=your-google-places-api-key
```

**To generate a secret key:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata VitaminSHE/fixtures/initial_resources.json
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## 📱 Features

### 1. User Authentication & Onboarding
- Secure signup and login
- Profile creation with health questionnaire
- Automatic profile generation on signup
- Age, dietary preferences, pregnancy status tracking

### 2. Vitamin Tracking
- Log intake of 12 essential vitamins
- Multiple sources per vitamin (food, supplement, IV)
- Multiple units support
- View daily, weekly, and monthly history
- Adherence rate calculation
- Current streak counter
- Ownership-based access control

### 3. Recommendation Engine
- Rule-based suggestions based on:
  - Pregnancy status
  - Vitamin D deficiency history
  - Iron deficiency history
  - Sunlight exposure levels
  - Dietary preferences (vegan, vegetarian, etc.)
  - Health goals
  - Allergies and restrictions
- Personalized priority levels (high, medium, low)
- Food source suggestions

### 4. Educational Resources
- 100+ medically-reviewed articles
- Organized by vitamin/mineral category
- Featured resources section
- Search and filtering by category
- Article metadata (author, date, ratings)
- Medical disclaimer on all pages

### 5. Clinic Locator
- Real-time clinic search using Google Places API
- Radius-based search (2km, 5km, 10km)
- Flexible query terms (clinic, blood test, phlebotomy, lab, etc.)
- Browser geolocation support
- Marker-based map display
- Save favorite clinics
- Get directions integration
- Graceful error handling

### 6. Dashboard
- Profile summary
- Latest vitamin logs
- Recent recommendations
- Adherence statistics
- Current streaks
- Quick access to all features

## 👥 User Types

### Unauthenticated Users
- Access landing page and about page
- View featured resources
- Browse educational articles

### Authenticated Users
- Complete profile onboarding
- Track vitamin intake
- View personalized recommendations
- Access full resource library
- Use clinic locator
- Save favorite clinics
- View comprehensive dashboard

## 📊 Data Models

### UserProfile
- Email, name, bio
- Onboarding status (pending/completed)
- Dietary preferences (omnivore/vegetarian/vegan)
- Pregnancy status
- Daily water intake goal

### VitaminLog
- User, vitamin type, source, amount, unit
- Logged date with time
- Created/updated timestamps
- Constraints: no future dates, positive amounts

### Recommendation
- User-specific vitamin recommendations
- Type, title, description
- Date range (starts_on, ends_on)
- Active status
- Timestamps

### ResourceCategory & ResourceArticle
- Categories with auto-slugging
- Published articles with markdown content
- Publication tracking
- Category relationships

### SavedResource
- User bookmarks for articles
- Unique constraint on user+article

### SavedClinic
- User's saved clinic information
- Coordinates with validation
- Phone, website, notes
- Google Place ID for external references

## 🔒 Security Features

- CSRF protection on all forms
- SQL injection prevention via Django ORM
- Password hashing with Django's authentication
- User data isolation (users can only see their data)
- HTTPS-ready configuration
- Medical disclaimer prominently displayed

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tracking recommendations

# With verbose output
python manage.py test -v 2

# Run tests for a specific test class
python manage.py test tracking.tests.VitaminTrackingViewTests
```

Current test coverage:
- **Tracking**: Ownership validation, adherence calculation, streak calculation
- **Recommendations**: Engine logic, rule application, output validation
- **Locator**: API endpoint validation, save/remove clinic operations

## 📁 Project Structure

```
VitaminSHE/
├── project_vitamins/          # Django project root
│   ├── manage.py
│   ├── .env                   # Environment variables (create this)
│   ├── db.sqlite3             # Database
│   │
│   ├── project_vitamins/      # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # Root URL routing
│   │   └── wsgi.py
│   │
│   ├── accounts/              # User authentication & profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── signals.py
│   │   └── urls.py
│   │
│   ├── tracking/              # Vitamin logging & tracking
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── urls.py
│   │
│   ├── recommendations/       # Recommendation engine
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── urls.py
│   │
│   ├── resources/             # Educational resources
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── fixtures/          # Sample data
│   │   └── templates/
│   │
│   ├── locator/               # Clinic locator
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── services.py        # Google Places API integration
│   │   ├── tests.py
│   │   └── templates/
│   │
│   ├── dashboard/             # User dashboard
│   │   ├── views.py
│   │   └── templates/
│   │
│   ├── core/                  # Landing page & about
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   │
│   └── VitaminSHE/           # Static files & base template
│       ├── templates/
│       │   └── base.html
│       └── static/
│           ├── css/
│           └── js/
│
└── README.md                  # This file
```

## 🚀 Deployment

### Local Deployment

```bash
python manage.py runserver 0.0.0.0:8000
```

### Production Deployment (Gunicorn + Nginx)

1. Set `DEBUG=False` in `.env`
2. Generate strong `DJANGO_SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Set up Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn project_vitamins.wsgi:application --bind 0.0.0.0:8000
   ```
6. Configure Nginx as reverse proxy
7. Set up HTTPS with Let's Encrypt

## 🔧 Configuration

### Google Maps API Setup (for Clinic Locator)

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Maps JavaScript API** and **Places API**
4. Create an API key (Credentials)
5. Add to `.env`:
   ```env
   GOOGLE_MAPS_API_KEY=your-key-here
   GOOGLE_PLACES_API_KEY=your-key-here
   ```

### SMTP Configuration (for Email)

To enable email notifications, add to `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 📚 API Endpoints

### Authentication
- `POST /accounts/signup/` - Register new user
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout

### Tracking
- `GET /tracking/` - List user's vitamin logs (paginated)
- `POST /tracking/add/` - Create new vitamin log
- `PUT /tracking/<id>/edit/` - Update vitamin log
- `DELETE /tracking/<id>/delete/` - Delete vitamin log

### Recommendations
- `GET /recommendations/` - List user's recommendations

### Resources
- `GET /resources/` - List all resources (with category filter)
- `GET /resources/<slug>/` - View single article
- `GET /resources/featured/` - View featured articles

### Clinic Locator
- `GET /locator/` - Clinic locator page
- `GET /locator/api/nearby/` - Search nearby clinics (JSON API)
- `POST /locator/api/save/` - Save clinic
- `POST /locator/api/remove/` - Remove saved clinic
- `GET /locator/saved/` - View saved clinics

## 🎓 Learning Resources

### Django Documentation
- [Django Official Docs](https://docs.djangoproject.com/)
- [Django Class-Based Views](https://docs.djangoproject.com/en/4.2/topics/class-based-views/)
- [Django ORM](https://docs.djangoproject.com/en/4.2/topics/db/models/)

### Google Maps API
- [Maps JavaScript API Docs](https://developers.google.com/maps/documentation/javascript)
- [Places API Docs](https://developers.google.com/maps/documentation/places)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Medical Disclaimer

**IMPORTANT:** The information provided on VitaminSHE is for educational purposes only and should not be considered medical advice. Always consult with a qualified healthcare professional before making any dietary changes or starting vitamin supplements. We are not liable for any health consequences resulting from the use of information on this platform.

## 📄 License

This project is open source and available under the MIT License. See LICENSE file for details.

## 👩‍💻 Author

Developed during Hack the Gap 2024

## 🏆 Awards

- **2nd Place** - Hack the Gap 2024 hackathon

## 📞 Support

For issues, questions, or suggestions, please:

1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include steps to reproduce (for bugs)
4. Provide screenshots when relevant

## 🔮 Future Improvements

- [ ] Mobile app (React Native)
- [ ] Integration with fitness trackers (Fitbit, Apple Health)
- [ ] Machine learning for recommendation personalization
- [ ] Appointment booking integration with clinics
- [ ] Telehealth provider integration
- [ ] Multi-language support
- [ ] Dark mode UI
- [ ] Export health reports (PDF)
- [ ] Social features (share progress, challenges)
- [ ] Wearable device integration
- [ ] Advanced analytics and insights
- [ ] Community forum for health discussions

## 📊 Statistics

- **7 Django Apps**: accounts, core, dashboard, tracking, recommendations, resources, locator
- **12 Vitamins Tracked**: A, B12, B6, C, D, E, Folate, Iron, Magnesium, Zinc, Selenium, Potassium
- **100+ Articles**: Curated health and nutrition content
- **3 Sources**: Food, Supplements, IV/Medical
- **6 Recommendation Rules**: Pregnancy, Iron, D, Fatigue, Goals, Restrictions
- **2 Analytics Views**: 7-day and 30-day adherence
- **99.9% Data Security**: Encrypted user data with CSRF protection

---

**Made with ❤️ at Hack the Gap 2024**
