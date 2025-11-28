# Harvest Assemblies of Christ Global Church Website (Dynamic Version)

This is the **dynamic web application** for Harvest Assemblies of Christ Global Church, built with **Flask** and **Jinja2 templates**.  
It provides a structured, maintainable platform for sermons, events, leadership profiles, and contact forms, powered by Python on the backend.

---

## ✨ Features

- **Dynamic Templates**  
  Pages extend from a shared `base.html` layout using Jinja2 blocks.

- **Navbar & Footer**  
  Unified navigation and sticky footer included in `base.html`.

- **Home Page**  
  Welcome message, mission, vision, and quick links.

- **About Page**  
  Church history, mission, vision, and values with Google Maps embed.

- **Sermons Page**  
  Dynamic section for recent sermons.

- **Events Page**  
  Dynamic listing of upcoming events.

- **Leaders Page**  
  Profiles of Apostle Malesela and leadership team.

- **Contact Page**  
  Contact form with POST handling (name, email, subject, urgency, message).

- **Admin Pages**  
  Login and dashboard routes for administrative use.

---

## 📂 Project Structure


---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+  
- pip (Python package manager)  
- Virtual environment recommended

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/harvest-church-dynamic.git
   cd harvest-church-dynamic
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py
