# Travel Agent AI

A simple travel planning assistant that uses AI to help users find travel packages through natural conversation.

## What It Does

This is a command-line application that:
- Asks users about their travel preferences in natural language
- Uses OpenAI's API to understand what they want
- Searches through a database of travel packages
- Shows the best matches based on compatibility scoring
- Lets users ask follow-up questions about the recommendations

## How to Run It

### Prerequisites
- Python 3.7 or higher
- OpenAI API key (optional but recommended)

### Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. (Optional) Add your OpenAI API key:
   - Create a file called `openai_api_key.txt` in the project folder
   - Paste your API key in the file
   - The app will work without this, but with limited functionality

3. Run the application:
```bash
python main.py
```

## How It Works

### Main Components

**Preference Extractor** (`preference_extractor.py`)
- Asks users 6 key questions about their trip
- Uses AI to understand natural language responses
- Has fallback patterns for when AI isn't available

**Package Recommender** (`package_recommender.py`)
- Searches through CSV database of 20 sample packages
- Calculates compatibility scores for each package
- Only shows packages that score 50+ out of 100 points

**Accommodation Suggester** (`accommodation_suggester.py`)
- Gives hotel/accommodation advice based on budget and style
- Simple rule-based recommendations

**Conversation Handler** (`conversation_handler.py`)
- Handles chat after showing initial recommendations
- Uses AI to answer questions about specific packages
- Has basic fallback responses when AI isn't working

### Sample Conversation Flow

```
Welcome to Travel Agent AI v1.0.0!

Where would you like to travel?
> I want to go somewhere romantic in Europe

What is your budget range for this trip?
> Around ₹200000-300000 for both of us

How many days are you planning to travel?
> Maybe 10 days

[... more questions ...]

TOP PACKAGE RECOMMENDATIONS FOR YOU:
1. Romantic Getaway 9 - Zurich, Switzerland
   Price: ₹200000-500000 | Duration: 21 days | Rating: 4.1 stars
   Compatibility: 75%

Your question: Tell me more about the Zurich package
> [AI provides detailed response about the package]
```

## Project Structure

```
├── main.py                      # Main application
├── preference_extractor.py      # User preference collection
├── package_recommender.py       # Package search and matching
├── accommodation_suggester.py   # Hotel recommendations
├── conversation_handler.py      # Post-recommendation chat
├── travel_packages.csv          # Sample package database
├── openai_api_key.txt          # API key (create this yourself)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Features

- **Natural Language Processing**: Users can describe preferences conversationally
- **Compatibility Scoring**: Only shows relevant packages (50+ compatibility score)
- **Fallback System**: Works even when OpenAI API is unavailable
- **Interactive Chat**: Ask follow-up questions about packages
- **Simple Setup**: Just needs Python and optionally an API key

## Limitations

- Only has 20 sample packages in the database
- Command-line interface only (no web UI)
- Booking links go to search pages, not direct bookings
- AI features require internet connection and API key

## Technologies Used

- **Python 3.7+**: Main programming language
- **OpenAI API**: For natural language understanding
- **CSV files**: For storing package data
- **Standard libraries**: For file handling and basic operations

## Future Improvements

- Add more realistic travel packages to the database
- Build a web interface instead of command line
- Connect to real booking sites for live data
- Add user accounts to save preferences
- Improve the compatibility scoring algorithm

## License

This is a student project created for educational purposes.
