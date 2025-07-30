#!/usr/bin/env python3
"""
User Preference Extraction Module
Handles natural language processing and preference extraction using OpenAI API
"""

import json
import re
from openai import OpenAI


class PreferenceExtractor:
    """Handles extraction of user travel preferences from natural language."""
    
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.required_preferences = {
            'destination': 'Where would you like to travel?',
            'budget': 'What is your budget range for this trip?',
            'duration': 'How many days are you planning to travel?',
            'travel_style': 'What type of travel experience are you looking for? (adventure, relaxation, cultural, business, etc.)',
            'group_size': 'How many people will be traveling?',
            'accommodation_type': 'What type of accommodation do you prefer?'
        }
    
    def extract_preference_from_response(self, user_response, preference_key):
        """Extract specific preference from user's natural language response using OpenAI."""
        if not self.client:
            # Fallback to basic keyword extraction if OpenAI is not available
            return self.basic_preference_extraction(user_response, preference_key)
        
        try:
            prompt = f"""
            You are a travel preference extraction assistant. Extract the {preference_key} information from the user's response.
            
            User's response: "{user_response}"
            
            Extract the {preference_key} and return it in this exact JSON format:
            {{"extracted_value": "value", "confidence": "high/medium/low", "needs_clarification": true/false}}
            
            Guidelines:
            - For destination: Extract city, country, or region names. Only extract if explicitly mentioned.
            - For budget: Extract amounts, ranges, or descriptors like "budget", "luxury", "moderate". Only if clearly specified.
            - For duration: Extract number of days, weeks, or time periods. Only if explicitly mentioned.
            - For travel_style: Extract adventure, relaxation, cultural, business, romantic, family, etc. Only if clearly indicated.
            - For group_size: Extract numbers or descriptors like "solo", "couple", "family", "group". Only if explicitly mentioned.
            - For accommodation_type: Extract hotel, hostel, airbnb, resort, camping, etc. Only if specifically mentioned.
            
            IMPORTANT: Do NOT infer or assume information. Only extract what is explicitly stated.
            If the information is unclear, missing, or not explicitly mentioned, set needs_clarification to true and extracted_value to null.
            Be conservative - when in doubt, ask for clarification rather than making assumptions.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            print(f"Error extracting preference: {e}")
            return {"extracted_value": None, "confidence": "low", "needs_clarification": True}
    
    def basic_preference_extraction(self, user_response, preference_key):
        """Basic keyword-based preference extraction when OpenAI is not available."""
        response_lower = user_response.lower()
        
        # Basic keyword matching patterns - made more strict to avoid false positives
        patterns = {
            'destination': r'(?:to|visit|go\s+to)\s+([a-zA-Z\s,]+?)(?:\s+for|\s+in|\s*$)',
            'budget': r'(?:budget.*?is|spend|cost.*?is)\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)|(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|bucks?|\$)|(?:budget.*?)?(luxury|moderate|cheap|expensive)',
            'duration': r'(\d+)\s*(?:days?|nights?|weeks?|months?)',
            'travel_style': r'(?:travel|style|experience|trip).*?\b(adventure|relaxation|cultural|business|romantic|family)\b|\b(adventure|relaxation|cultural|business|romantic|family)\b(?:\s+(?:travel|style|experience|trip))?',
            'group_size': r'(\d+)\s*(?:people|person|travelers?)|(?:\b(solo|couple|family|group)\b)(?:\s+(?:travel|trip|vacation))?',
            'accommodation_type': r'(?:stay|staying|accommodation).*?\b(hotel|hostel|airbnb|resort|camping|motel|guesthouse|boutique)\b|\b(hotel|hostel|airbnb|resort|camping|motel|guesthouse|boutique)\b'
        }
        
        if preference_key in patterns:
            match = re.search(patterns[preference_key], response_lower)
            if match:
                # Get the first non-empty group
                extracted_value = None
                for group in match.groups():
                    if group and group.strip():
                        extracted_value = group.strip()
                        break
                
                if not extracted_value:
                    return {"extracted_value": None, "confidence": "low", "needs_clarification": True}
                
                # Clean up destination extraction
                if preference_key == 'destination':
                    # Remove common prefixes
                    extracted_value = re.sub(r'^(go to|visit|to)\s+', '', extracted_value.strip())
                
                # Additional validation to avoid false positives
                if preference_key == 'travel_style' and extracted_value not in ['adventure', 'relaxation', 'cultural', 'business', 'romantic', 'family']:
                    return {"extracted_value": None, "confidence": "low", "needs_clarification": True}
                if preference_key == 'group_size' and extracted_value not in ['solo', 'couple', 'family', 'group'] and not extracted_value.isdigit():
                    return {"extracted_value": None, "confidence": "low", "needs_clarification": True}
                if preference_key == 'destination' and len(extracted_value) < 2:
                    return {"extracted_value": None, "confidence": "low", "needs_clarification": True}
                
                return {
                    "extracted_value": extracted_value,
                    "confidence": "medium",
                    "needs_clarification": False
                }
        
        return {"extracted_value": None, "confidence": "low", "needs_clarification": True}

    def generate_followup_question(self, preference_key, previous_response):
        """Generate a natural follow-up question for clarification."""
        if not self.client:
            # Fallback to predefined questions
            return self.required_preferences[preference_key]
        
        try:
            prompt = f"""
            You are a friendly travel agent. The user gave this response: "{previous_response}"
            
            I need to clarify their {preference_key} for trip planning. Generate a natural, conversational follow-up question to get more specific information about their {preference_key}.
            
            Make it sound friendly and helpful, not robotic. Keep it concise and focused on getting the missing {preference_key} information.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating follow-up question: {e}")
            return self.required_preferences[preference_key]  # Fallback to default question

    def get_user_preferences(self):
        """Get travel preferences from user using natural language conversation with OpenAI."""
        preferences = {}
        
        print("\nHi! I'm excited to help you plan your perfect trip! 🌍")
        print("Just tell me about your travel plans in your own words, and I'll ask follow-up questions as needed.\n")
        
        # Start with an open-ended question
        print("Let's start with the basics - tell me about the trip you're planning!")
        initial_response = input("You: ").strip()
        
        # Try to extract all preferences from the initial response
        for key in self.required_preferences:
            extraction_result = self.extract_preference_from_response(initial_response, key)
            
            if not extraction_result["needs_clarification"] and extraction_result["extracted_value"]:
                preferences[key] = extraction_result["extracted_value"]
                print(f"✓ Got it! {key.replace('_', ' ').title()}: {extraction_result['extracted_value']}")
        
        # Loop through missing preferences and ask for clarification
        max_attempts_per_preference = 3
        
        for key in self.required_preferences:
            if key in preferences:
                continue
                
            attempts = 0
            while key not in preferences and attempts < max_attempts_per_preference:
                attempts += 1
                
                if attempts == 1:
                    # First attempt - use the initial response context
                    question = self.generate_followup_question(key, initial_response)
                else:
                    # Subsequent attempts - use default question
                    question = self.required_preferences[key]
                
                print(f"\n{question}")
                user_response = input("You: ").strip()
                
                if not user_response:
                    print("I didn't get a response. Let me try asking differently...")
                    continue
                
                # Extract preference from the response
                extraction_result = self.extract_preference_from_response(user_response, key)
                
                if not extraction_result["needs_clarification"] and extraction_result["extracted_value"]:
                    preferences[key] = extraction_result["extracted_value"]
                    print(f"✓ Perfect! {key.replace('_', ' ').title()}: {extraction_result['extracted_value']}")
                    break
                else:
                    if attempts < max_attempts_per_preference:
                        print("I need a bit more specific information about that...")
            
            # If still no preference after max attempts, use a default or skip
            if key not in preferences:
                print(f"No worries, we can work with what we have for {key.replace('_', ' ')}!")
                preferences[key] = "Not specified"
        
        # Confirmation summary
        print(f"\n🎉 Great! Here's what I understood about your trip:")
        for key, value in preferences.items():
            if value != "Not specified":
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        confirm = input("\nDoes this look correct? (yes/no): ").strip().lower()
        if confirm.startswith('n'):
            preferences = self.handle_preference_corrections(preferences)
        
        return preferences
    
    def handle_preference_corrections(self, preferences):
        """Handle user corrections to extracted preferences."""
        print("Let me know what needs to be corrected, and I'll update it!")
        correction_input = input("What would you like to change? ").strip()
        
        if not correction_input:
            return preferences
        
        # Try to extract what the user wants to change using OpenAI or basic parsing
        if self.client:
            try:
                prompt = f"""
                The user wants to correct their travel preferences. They said: "{correction_input}"
                
                Current preferences:
                {preferences}
                
                Identify what specific preference(s) they want to change and extract the new values.
                Return a JSON object with the corrections in this format:
                {{"preference_key": "new_value", "another_key": "another_new_value"}}
                
                Only include preferences that are being changed. Possible keys are:
                destination, budget, duration, travel_style, group_size, accommodation_type
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200
                )
                
                corrections = json.loads(response.choices[0].message.content.strip())
                
                # Apply corrections
                for key, new_value in corrections.items():
                    if key in preferences:
                        old_value = preferences[key]
                        preferences[key] = new_value
                        print(f"✓ Updated {key.replace('_', ' ').title()}: {old_value} → {new_value}")
                
            except Exception as e:
                print(f"Error processing corrections: {e}")
                # Fallback to manual correction
                preferences = self.manual_preference_correction(preferences)
        else:
            # Fallback to manual correction when OpenAI is not available
            preferences = self.manual_preference_correction(preferences)
        
        # Show updated preferences and confirm again
        print(f"\n📝 Updated preferences:")
        for key, value in preferences.items():
            if value != "Not specified":
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        final_confirm = input("\nDoes this look correct now? (yes/no): ").strip().lower()
        if final_confirm.startswith('n'):
            # Allow one more round of corrections
            return self.handle_preference_corrections(preferences)
        
        return preferences
    
    def manual_preference_correction(self, preferences):
        """Handle manual preference corrections when AI extraction fails."""
        print("\nWhich preference would you like to change?")
        for i, (key, value) in enumerate(preferences.items(), 1):
            if value != "Not specified":
                print(f"{i}. {key.replace('_', ' ').title()}: {value}")
        
        try:
            choice = input("\nEnter the number of the preference to change (or press Enter to skip): ").strip()
            if not choice:
                return preferences
            
            choice_idx = int(choice) - 1
            preference_keys = [k for k, v in preferences.items() if v != "Not specified"]
            
            if 0 <= choice_idx < len(preference_keys):
                key_to_change = preference_keys[choice_idx]
                print(f"\nCurrent {key_to_change.replace('_', ' ')}: {preferences[key_to_change]}")
                new_value = input(f"Enter new {key_to_change.replace('_', ' ')}: ").strip()
                
                if new_value:
                    old_value = preferences[key_to_change]
                    preferences[key_to_change] = new_value
                    print(f"✓ Updated {key_to_change.replace('_', ' ').title()}: {old_value} → {new_value}")
            else:
                print("Invalid choice number. Keeping current preferences.")
                
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number. Keeping current preferences.")
        
        return preferences
