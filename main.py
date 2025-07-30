#!/usr/bin/env python3
"""
Travel Agent AI - Main Application
A simple travel agent AI assistant to help users plan their trips.
"""

import sys
import os
from datetime import datetime
from openai import OpenAI

# Import custom modules
from preference_extractor import PreferenceExtractor
from package_recommender import PackageRecommender
from accommodation_suggester import AccommodationSuggester
from conversation_handler import ConversationHandler


class TravelAgent:
    """A simple travel agent AI assistant."""
    
    def __init__(self):
        self.name = "Travel Agent AI"
        self.version = "1.0.0"
        
        # Initialize OpenAI client by reading API key from file
        api_key = self.read_api_key_from_file()
        if not api_key:
            print("⚠️  Warning: OpenAI API key not found in 'openai_api_key.txt' file.")
            print("Please create an 'openai_api_key.txt' file in the project directory and add your OpenAI API key.")
            print("The application will still work with basic functionality.\n")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
                print("✅ OpenAI API key loaded successfully from file.\n")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                print("The application will work with basic functionality.\n")
                self.client = None
        
        # Initialize modules
        self.preference_extractor = PreferenceExtractor(self.client)
        self.package_recommender = PackageRecommender(self.client)
        self.accommodation_suggester = AccommodationSuggester()
        self.conversation_handler = ConversationHandler(self.client)
    
    def read_api_key_from_file(self):
        """Read OpenAI API key from openai_api_key.txt file."""
        try:
            # Try to read from openai_api_key.txt in the same directory
            with open('openai_api_key.txt', 'r') as file:
                api_key = file.read().strip()
                if api_key:
                    return api_key
                else:
                    print("❌ The 'openai_api_key.txt' file is empty.")
                    return None
        except FileNotFoundError:
            print("❌ File 'openai_api_key.txt' not found in the project directory.")
            return None
        except Exception as e:
            print(f"❌ Error reading API key file: {e}")
            return None
    
    def welcome(self):
        """Display welcome message."""
        print(f"Welcome to {self.name} v{self.version}!")
        print("I'm here to help you plan your perfect trip.")
        print("-" * 50)
    
    def get_user_preferences(self):
        """Get travel preferences from user using the preference extractor module."""
        return self.preference_extractor.get_user_preferences()
    
    def generate_recommendations(self, preferences):
        """Generate travel recommendations based on user preferences."""
        # Display accommodation suggestions
        self.accommodation_suggester.display_accommodation_suggestions(preferences)
        
        # Display top package recommendations and get the packages for later reference
        self.top_packages = self.package_recommender.display_top_packages(preferences)

        if not self.top_packages:
            # Display  recommendations from online sources with booking links
            self.top_packages=self.package_recommender.display_online_recommendations(preferences)

    def run(self):
        """Main application loop."""
        self.welcome()
        
        try:
            preferences = self.get_user_preferences()
            self.generate_recommendations(preferences)
            # Start post-recommendations conversation using the conversation handler
            self.conversation_handler.start_conversation(preferences, self.top_packages)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Feel free to come back anytime for travel planning help.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again or contact support.")


def main():
    """Entry point of the application."""
    agent = TravelAgent()
    agent.run()


if __name__ == "__main__":
    main()
