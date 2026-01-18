# Raven Football Jersey Website by Josh and Bob

A web application for selling and auctioning football jerseys.

## Features

- Browse football jerseys for sale
- Search functionality
- Sort by price, date, or seller rating
- Detailed product pages
- (Coming soon) Auction functionality

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/raven_website.git
cd raven_website
```

2. Install required dependencies:
```
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask server:
```
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
  - `index.html` - Home page
  - `sell.html` - Jersey listing page
  - `jersey_detail.html` - Individual jersey page
  - `auction.html` - Auction page (coming soon)
- `static/` - Static files
  - `css/style.css` - Stylesheet
  - `js/script.js` - JavaScript functionality
  - `images/` - Jersey images
- `jerseys.json` - Database file storing jersey information

## Usage

1. Browse jerseys on the "Buy Jerseys" page
2. Use the search bar to find specific jerseys
3. Sort jerseys by different criteria using the dropdown
4. Click on a jersey to view its details

## Future Enhancements

- User authentication system
- Shopping cart and checkout functionality
- Auction bidding system
- User reviews and ratings
- Admin dashboard for managing jersey listings 