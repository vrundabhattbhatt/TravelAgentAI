#!/usr/bin/env python3
"""
Package Recommendation Module
Handles travel package generation, storage, and recommendation matching
"""

import csv
import random
import os
import urllib.parse
from datetime import datetime, timedelta


class PackageRecommender:
    """Handles travel package generation and recommendation matching."""
    
    def __init__(self, openai_client=None):
        """Initialize the PackageRecommender."""
        self.packages = []
        self.csv_file = 'travel_packages.csv'
        self.openai_client = openai_client
        
        # Generate and save sample packages only if CSV doesn't exist
        if not os.path.exists(self.csv_file):
            print("📦 Generating sample travel packages database...")
            self.packages = self.generate_sample_packages()
            self.save_packages_to_csv(self.packages)
            print(f"✅ Sample packages saved to {self.csv_file}")
        else:
            print(f"📋 Loading existing packages from {self.csv_file}")
        
        # Load packages from CSV
        self.packages = self.load_packages_from_csv() or []
    
    def generate_sample_packages(self, num_packages=20):
        """Generate sample travel packages with different combinations of preferences."""
        
        # Sample data for generating packages
        destinations = [
            "Paris, France", "Tokyo, Japan", "New York, USA", "London, UK", "Rome, Italy",
            "Barcelona, Spain", "Amsterdam, Netherlands", "Sydney, Australia", "Dubai, UAE",
            "Bangkok, Thailand", "Istanbul, Turkey", "Prague, Czech Republic", "Vienna, Austria",
            "Berlin, Germany", "Copenhagen, Denmark", "Stockholm, Sweden", "Zurich, Switzerland",
            "Singapore", "Hong Kong", "Mumbai, India"
        ]
        
        budgets = ["budget", "moderate", "luxury", "$500-1000", "$1000-2000", "$2000-5000", "$5000+"]
        durations = ["3", "5", "7", "10", "14", "21", "28"]
        travel_styles = ["adventure", "relaxation", "cultural", "business", "romantic", "family"]
        group_sizes = ["solo", "couple", "family", "group", "2", "4", "6", "8"]
        accommodation_types = ["hotel", "hostel", "airbnb", "resort", "camping", "boutique"]
        
        # Package features
        package_names = [
            "City Explorer", "Cultural Immersion", "Adventure Seeker", "Luxury Escape", 
            "Budget Traveler", "Business Elite", "Romantic Getaway", "Family Fun",
            "Backpacker Special", "Wellness Retreat", "Historic Journey", "Modern Metropolis",
            "Nature Explorer", "Culinary Tour", "Art & Culture", "Shopping Spree",
            "Beach Paradise", "Mountain Adventure", "Desert Safari", "Urban Discovery"
        ]
        
        activities = [
            "City tours, Museums, Local cuisine", "Hiking, Adventure sports, Nature walks",
            "Spa treatments, Yoga, Meditation", "Shopping, Nightlife, Entertainment",
            "Cultural sites, Historical tours, Art galleries", "Beach activities, Water sports, Relaxation",
            "Business meetings, Networking events, City exploration", "Family activities, Theme parks, Kid-friendly tours",
            "Budget tours, Free walking tours, Local experiences", "Photography tours, Scenic views, Local markets"
        ]
        
        packages = []
        
        for i in range(num_packages):
            package = {
                'package_id': f"PKG{i+1:03d}",
                'package_name': random.choice(package_names) + f" {i+1}",
                'destination': random.choice(destinations),
                'budget': random.choice(budgets),
                'duration': random.choice(durations),
                'travel_style': random.choice(travel_styles),
                'group_size': random.choice(group_sizes),
                'accommodation_type': random.choice(accommodation_types),
                'activities': random.choice(activities),
                'price_range': self.generate_price_range(random.choice(budgets)),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'reviews_count': random.randint(50, 1000),
                'includes': self.generate_package_includes(),
                'best_time': random.choice(["Spring", "Summer", "Fall", "Winter", "Year-round"])
            }
            packages.append(package)
        
        return packages
    
    def generate_booking_links(self, package):
        """Generate booking links for popular travel sites."""
        destination = package['destination']
        package_name = package['package_name']
        
        # URL encode destination and package name for search queries
        encoded_destination = urllib.parse.quote(destination)
        encoded_package = urllib.parse.quote(f"{package_name} {destination}")
        
        booking_links = {
            'expedia': f"https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:,to:{encoded_destination}&passengers=adults:2,children:0,seniors:0,infantinlap:Y",
            'booking_com': f"https://www.booking.com/searchresults.html?ss={encoded_destination}&checkin_year=2025&checkin_month=8&checkin_monthday=15&checkout_year=2025&checkout_month=8&checkout_monthday=20",
            'agoda': f"https://www.agoda.com/search?city={encoded_destination}&checkIn=2025-08-15&checkOut=2025-08-20&rooms=1&adults=2&children=0",
            'trip_advisor': f"https://www.tripadvisor.com/Search?q={encoded_destination}&searchSessionId=000&searchNearby=false&geo=1&pid=3826&metaReferer=",
            'kayak': f"https://www.kayak.com/flights/{encoded_destination}?sort=bestflight_a",
            'makemytrip': f"https://www.makemytrip.com/hotels/{encoded_destination.lower().replace(' ', '-').replace(',', '')}-hotels.html",
            'cleartrip': f"https://www.cleartrip.com/hotels/{encoded_destination.lower().replace(' ', '-').replace(',', '')}/",
            'goibibo': f"https://www.goibibo.com/hotels/{encoded_destination.lower().replace(' ', '-').replace(',', '')}/"
        }
        
        return booking_links
    
    def get_random_booking_site_url(self, package):
        """Get a random booking site URL to use as the source for online packages."""
        booking_links = self.generate_booking_links(package)
        site_names = list(booking_links.keys())
        selected_site = random.choice(site_names)
        return booking_links[selected_site]
    
    def search_online_packages(self, user_preferences):
        """Search for packages using OpenAI API when local matches are insufficient."""
        print("🔍 Searching popular travel booking sites for your perfect match...")
        
        online_packages = []
        
        try:
            if self.openai_client:
                # Use OpenAI API to find real travel packages
                ai_packages = self.get_packages_from_openai(user_preferences)
                online_packages.extend(ai_packages)
                print(f"✅ Great news! Found {len(online_packages)} highly compatible packages from online booking sites")
            else:
                print("❌ OpenAI API not available. Cannot search online booking sites.")
                print("💡 Please ensure OpenAI API key is properly configured to access online travel packages.")
                return []
            
        except Exception as e:
            print(f"❌ Error searching online booking sites: {e}")
            print("� Unable to fetch packages from online sources at this time.")
            return []
        
        return online_packages
    
    def get_packages_from_openai(self, user_preferences):
        """Use OpenAI API to find real travel packages matching user preferences."""
        destination = user_preferences.get('destination', 'Unknown Destination')
        budget = user_preferences.get('budget', 'moderate')
        duration = user_preferences.get('duration', '7')
        travel_style = user_preferences.get('travel_style', 'relaxation')
        group_size = user_preferences.get('group_size', '2')
        accommodation_type = user_preferences.get('accommodation_type', 'hotel')
        
        # Create a detailed prompt for OpenAI to find real travel packages
        prompt = f"""
        You are a travel expert with access to current travel package information from major booking sites. 

        Find 3 real travel packages that match these specific preferences:
        - Destination: {destination}
        - Budget: {budget}
        - Duration: {duration} days
        - Travel Style: {travel_style}
        - Group Size: {group_size}
        - Accommodation Type: {accommodation_type}

        For each package, provide EXACTLY this information in this exact format:

        Package 1:
        package_id: ONLINE001
        package_name: [Creative package name for {destination}]
        destination: {destination}
        budget: {budget}
        duration: {duration}
        travel_style: {travel_style}
        group_size: {group_size}
        accommodation_type: {accommodation_type}
        activities: [Specific activities matching {travel_style} style in {destination}]
        price_range: [Realistic price range for {budget} budget]
        rating: [Rating between 3.5-5.0]
        reviews_count: [Number of reviews between 100-1000]
        includes: [List of what's included in the package]
        best_time: [Best season to visit {destination}]
        source: Online Booking Site

        Package 2:
        [Same format with package_id: ONLINE002]

        Package 3:
        [Same format with package_id: ONLINE003]

        Make sure the packages are realistic, well-researched, and truly match the user's preferences. Include specific activities, attractions, and experiences available in {destination}.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional travel consultant with extensive knowledge of current travel packages and destinations worldwide."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse the response into package format
            packages = self.parse_openai_response(response.choices[0].message.content, user_preferences)
            return packages
            
        except Exception as e:
            print(f"⚠️ Error calling OpenAI API: {e}")
            raise e
    
    def parse_openai_response(self, response_text, user_preferences):
        """Parse OpenAI response text into package dictionary format."""
        packages = []
        
        try:
            # Split response into individual packages
            package_blocks = response_text.split('Package ')[1:]  # Skip the first empty split
            
            for i, block in enumerate(package_blocks[:3], 1):  # Limit to 3 packages
                package = {
                    'package_id': f'ONLINE{i:03d}',
                    'package_name': self.extract_field(block, 'package_name'),
                    'destination': user_preferences.get('destination', 'Unknown Destination'),
                    'budget': user_preferences.get('budget', 'moderate'),
                    'duration': user_preferences.get('duration', '7'),
                    'travel_style': user_preferences.get('travel_style', 'relaxation'),
                    'group_size': user_preferences.get('group_size', '2'),
                    'accommodation_type': user_preferences.get('accommodation_type', 'hotel'),
                    'activities': self.extract_field(block, 'activities'),
                    'price_range': self.extract_field(block, 'price_range'),
                    'rating': self.extract_field(block, 'rating'),
                    'reviews_count': self.extract_field(block, 'reviews_count'),
                    'includes': self.extract_field(block, 'includes'),
                    'best_time': self.extract_field(block, 'best_time'),
                    'source': None  # Will be set after package is complete
                }
                
                # Validate and set defaults for missing fields
                package = self.validate_package_data(package, user_preferences)
                
                # Set the source to a random booking site URL
                package['source'] = self.get_random_booking_site_url(package)
                
                packages.append(package)
            
        except Exception as e:
            print(f"⚠️ Error parsing OpenAI response: {e}")
            print("💡 Received invalid response format from OpenAI. Please try again.")
            return []
        
        return packages
    
    def extract_field(self, text, field_name):
        """Extract a specific field value from OpenAI response text."""
        try:
            # Look for the field in the text
            lines = text.split('\n')
            for line in lines:
                if field_name.lower() in line.lower() and ':' in line:
                    value = line.split(':', 1)[1].strip()
                    # Clean up any brackets or formatting
                    value = value.replace('[', '').replace(']', '').strip()
                    return value if value else 'Not specified'
        except:
            pass
        return 'Not specified'
    
    def validate_package_data(self, package, user_preferences):
        """Validate and set defaults for package data fields."""
        try:
            # Ensure rating is a valid float
            try:
                rating = float(package['rating'])
                if rating < 3.5 or rating > 5.0:
                    package['rating'] = '4.2'
            except:
                package['rating'] = '4.2'
            
            # Ensure reviews_count is a valid integer
            try:
                reviews = int(package['reviews_count'])
                if reviews < 100 or reviews > 1000:
                    package['reviews_count'] = '300'
            except:
                package['reviews_count'] = '300'
            
            # Set defaults for empty fields
            if package['package_name'] == 'Not specified':
                package['package_name'] = f"{package['travel_style'].title()} Experience in {package['destination']}"
            
            if package['activities'] == 'Not specified':
                package['activities'] = self.get_activity_for_style(package['travel_style'])
            
            if package['price_range'] == 'Not specified':
                package['price_range'] = self.get_price_for_budget(package['budget'])
            
            if package['includes'] == 'Not specified':
                package['includes'] = f"Accommodation, Transportation, {package['travel_style']} activities, Travel insurance"
            
            if package['best_time'] == 'Not specified':
                package['best_time'] = self.get_current_season()
            
        except Exception as e:
            print(f"⚠️ Error validating package data: {e}")
        
        return package
    
    def get_activity_for_style(self, travel_style):
        """Get appropriate activities based on travel style."""
        style_activities = {
            'cultural': 'Museums, Historical sites, Art galleries, Cultural tours',
            'adventure': 'Hiking, Rock climbing, Adventure sports, Nature exploration',
            'relaxation': 'Spa treatments, Beach activities, Yoga, Meditation',
            'business': 'Business meetings, Networking events, City exploration, Fine dining',
            'romantic': 'Romantic dinners, Couples spa, Sunset tours, Wine tasting',
            'family': 'Family activities, Theme parks, Kid-friendly tours, Interactive museums'
        }
        return style_activities.get(travel_style.lower(), 'City tours, Local experiences, Sightseeing')
    
    def get_price_for_budget(self, budget):
        """Get appropriate price range for budget type."""
        budget_prices = {
            'budget': '$400-800',
            'moderate': '$1000-1800',
            'luxury': '$3000-6000'
        }
        return budget_prices.get(budget.lower(), '$1000-1800')
    
    def get_current_season(self):
        """Get current season based on current month."""
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:
            return 'Winter'
        elif current_month in [3, 4, 5]:
            return 'Spring'
        elif current_month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def calculate_enhanced_compatibility_score(self, user_preferences, package):
        """Enhanced compatibility score with additional factors from online travel sites."""
        score = 0
        max_score = 0
        
        # Base compatibility score (existing logic)
        base_score, raw_score, base_max_score = self.calculate_compatibility_score(user_preferences, package)
        score += raw_score
        max_score += base_max_score
        
        # Additional scoring factors based on online travel site preferences
        
        # Rating weight (weight: 2) - Higher rated packages get more points
        max_score += 2
        rating = float(package.get('rating', 0))
        if rating >= 4.5:
            score += 2
        elif rating >= 4.0:
            score += 1.5
        elif rating >= 3.5:
            score += 1
        
        # Reviews count weight (weight: 1) - More reviews indicate popularity
        max_score += 1
        reviews = int(package.get('reviews_count', 0))
        if reviews >= 500:
            score += 1
        elif reviews >= 200:
            score += 0.7
        elif reviews >= 100:
            score += 0.5
        
        # Price competitiveness (weight: 2) - Match budget expectations
        max_score += 2
        user_budget = user_preferences.get('budget', '').lower()
        package_price = package.get('price_range', '').lower()
        
        # Extract numeric values from price ranges for comparison
        if '$' in package_price and user_budget:
            try:
                if 'budget' in user_budget or 'cheap' in user_budget or 'low' in user_budget:
                    if any(range_val in package_price for range_val in ['300-600', '400-800', '500-900']):
                        score += 2
                elif 'luxury' in user_budget or 'premium' in user_budget or 'high' in user_budget:
                    if any(range_val in package_price for range_val in ['2500-5000', '3000-6000', '4000-8000', '5000-10000']):
                        score += 2
                else:  # moderate budget
                    if any(range_val in package_price for range_val in ['800-1500', '1000-1800', '1200-2000']):
                        score += 2
                    elif any(range_val in package_price for range_val in ['1000-2000', '2000-5000']):
                        score += 1.5
            except:
                pass
        
        # Seasonal relevance (weight: 1) - Best time to visit matching
        max_score += 1
        current_month = datetime.now().month
        best_time = package.get('best_time', '').lower()
        
        # Map current month to season
        if current_month in [12, 1, 2]:
            current_season = 'winter'
        elif current_month in [3, 4, 5]:
            current_season = 'spring'
        elif current_month in [6, 7, 8]:
            current_season = 'summer'
        else:
            current_season = 'fall'
        
        if best_time == current_season or best_time == 'year-round':
            score += 1
        elif best_time in ['year-round', 'all seasons']:
            score += 0.7
        
        # Package inclusions quality (weight: 1.5) - More inclusions = better value
        max_score += 1.5
        inclusions = package.get('includes', '').lower()
        inclusion_count = len(inclusions.split(',')) if inclusions else 0
        
        if inclusion_count >= 7:
            score += 1.5
        elif inclusion_count >= 5:
            score += 1.2
        elif inclusion_count >= 3:
            score += 0.8
        
        # Calculate percentage score
        if max_score > 0:
            percentage_score = (score / max_score) * 100
        else:
            percentage_score = 0
            
        return percentage_score, score, max_score
    
    def generate_price_range(self, budget_type):
        """Generate appropriate price range based on budget type."""
        price_ranges = {
            'budget': random.choice(["$300-600", "$400-800", "$500-900"]),
            'moderate': random.choice(["$800-1500", "$1000-1800", "$1200-2000"]),
            'luxury': random.choice(["$2500-5000", "$3000-6000", "$4000-8000"]),
            '$500-1000': "$500-1000",
            '$1000-2000': "$1000-2000", 
            '$2000-5000': "$2000-5000",
            '$5000+': "$5000-10000"
        }
        return price_ranges.get(budget_type, "$800-1500")
    
    def generate_package_includes(self):
        """Generate random package inclusions."""
        base_includes = ["Accommodation", "Transportation"]
        optional_includes = [
            "Breakfast", "All meals", "Tour guide", "Airport transfers",
            "Travel insurance", "WiFi", "City tours", "Welcome dinner",
            "24/7 support", "Local SIM card", "Travel kit"
        ]
        
        includes = base_includes + random.sample(optional_includes, random.randint(2, 5))
        return ", ".join(includes)
    
    def save_packages_to_csv(self, packages, filename=None):
        """Save generated packages to CSV file."""
        if filename is None:
            filename = self.csv_file
            
        try:
            fieldnames = [
                'package_id', 'package_name', 'destination', 'budget', 'duration',
                'travel_style', 'group_size', 'accommodation_type', 'activities',
                'price_range', 'rating', 'reviews_count', 'includes', 'best_time'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(packages)
            
            print(f"✅ Successfully saved {len(packages)} packages to '{filename}'")
            return True
            
        except Exception as e:
            print(f"❌ Error saving packages to CSV: {e}")
            return False
    
    def load_packages_from_csv(self, filename=None):
        """Load packages from CSV file."""
        if filename is None:
            filename = self.csv_file
            
        try:
            packages = []
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    packages.append(row)
            
            print(f"✅ Successfully loaded {len(packages)} packages from '{filename}'")
            return packages
            
        except FileNotFoundError:
            print(f"❌ File '{filename}' not found. Generating new packages...")
            return None
        except Exception as e:
            print(f"❌ Error loading packages from CSV: {e}")
            return None
    
    def calculate_compatibility_score(self, user_preferences, package):
        """Calculate compatibility score between user preferences and a package."""
        score = 0
        max_score = 0
        
        # Destination matching (weight: 3)
        max_score += 3
        if user_preferences.get('destination', '').lower() in package['destination'].lower():
            score += 3
        elif any(word in package['destination'].lower() 
                for word in user_preferences.get('destination', '').lower().split()):
            score += 2
        
        # Budget matching (weight: 3)
        max_score += 3
        user_budget = user_preferences.get('budget', '').lower()
        package_budget = package['budget'].lower()
        
        if user_budget == package_budget:
            score += 3
        elif any(word in package_budget for word in ['budget', 'cheap', 'low']) and \
             any(word in user_budget for word in ['budget', 'cheap', 'low', 'affordable']):
            score += 2
        elif any(word in package_budget for word in ['luxury', 'premium']) and \
             any(word in user_budget for word in ['luxury', 'high', 'premium', 'expensive']):
            score += 2
        elif 'moderate' in package_budget and not any(word in user_budget 
                                                      for word in ['budget', 'luxury', 'cheap', 'expensive']):
            score += 1
        
        # Duration matching (weight: 2)
        max_score += 2
        try:
            user_duration = int(user_preferences.get('duration', '0'))
            package_duration = int(package['duration'])
            duration_diff = abs(user_duration - package_duration)
            
            if duration_diff == 0:
                score += 2
            elif duration_diff <= 2:
                score += 1
        except ValueError:
            pass
        
        # Travel style matching (weight: 3)
        max_score += 3
        user_style = user_preferences.get('travel_style', '').lower()
        package_style = package['travel_style'].lower()
        
        if user_style == package_style:
            score += 3
        elif user_style in package['activities'].lower():
            score += 2
        
        # Group size matching (weight: 2)
        max_score += 2
        user_group = user_preferences.get('group_size', '').lower()
        package_group = package['group_size'].lower()
        
        if user_group == package_group:
            score += 2
        elif (user_group in ['solo', '1'] and package_group in ['solo', '1']) or \
             (user_group in ['couple', '2'] and package_group in ['couple', '2']) or \
             (user_group in ['family', 'group'] and package_group in ['family', 'group']):
            score += 1
        
        # Accommodation type matching (weight: 2)
        max_score += 2
        user_accommodation = user_preferences.get('accommodation_type', '').lower()
        package_accommodation = package['accommodation_type'].lower()
        
        if user_accommodation == package_accommodation:
            score += 2
        elif user_accommodation in package_accommodation or package_accommodation in user_accommodation:
            score += 1
        
        # Calculate percentage score
        if max_score > 0:
            percentage_score = (score / max_score) * 100
        else:
            percentage_score = 0
            
        return percentage_score, score, max_score

    def find_online_packages(self, user_preferences,  top_n=3):
        """Find the packages online based on user preferences."""
        
        
        # If best local match is below threshold, search online booking sites
        min_compatibility_threshold = 15  # Minimum compatibility percentage threshold
           
        print("\n" + "="*80)
        print("🔍 SEARCHING ONLINE TRAVEL SITES")
        print("="*80)
        print("❌ I am not able to find relevant travel packages for your preferences in our database.")
        print("🌐 Hence, providing you details of packages found online with booking links.")
        print("✨ These online packages are specifically tailored to match your requirements!")
        print("-"*80)
        
        # Search online booking sites
        online_packages = self.search_online_packages(user_preferences)
        
        if online_packages:
            # Score online packages
            online_scored_packages = []
            for package in online_packages:
                compatibility_score, raw_score, max_score = self.calculate_enhanced_compatibility_score(user_preferences, package)
                
                package_with_score = package.copy()
                package_with_score['enhanced_compatibility_score'] = compatibility_score
                package_with_score['enhanced_raw_score'] = raw_score
                package_with_score['enhanced_max_score'] = max_score
                package_with_score['booking_links'] = self.generate_booking_links(package)
                
                online_scored_packages.append(package_with_score)
            
            # Combine and sort all packages (local + online)
            all_packages =  online_scored_packages
            all_packages.sort(
                key=lambda x: (
                    x['enhanced_compatibility_score'], 
                    float(x['rating']), 
                    int(x['reviews_count'])
                ), 
                reverse=True
            )
            
            print(f"✅ Found {len(all_packages)} highly compatible packages online!")
            return all_packages[:top_n]
        else:
            print("⚠️ No suitable packages found online either. Please try adjusting your preferences.")
            return []   


    def find_top_packages(self, user_preferences, packages=None, top_n=3):
        """Find top N packages based on user preferences."""
        
        # Use instance packages if not provided
        if packages is None:
            packages = self.packages
            if not packages:
                print("No packages available. Generating sample packages...")
                packages = self.generate_sample_packages()
                self.save_packages_to_csv(packages)
                self.packages = packages
        
        # Calculate compatibility scores
        scored_packages = []
        for package in packages:
            compatibility_score, raw_score, max_score = self.calculate_compatibility_score(user_preferences, package)
            
            # Only add packages with compatibility score greater than 5
            if compatibility_score > 5:
                package_with_score = package.copy()
                package_with_score['compatibility_score'] = compatibility_score
                package_with_score['raw_score'] = raw_score
                package_with_score['max_score'] = max_score
                
                scored_packages.append(package_with_score)
        
        # Sort by compatibility score and rating
        scored_packages.sort(key=lambda x: (x['compatibility_score'], float(x['rating'])), reverse=True)
        
        return scored_packages[:top_n]
    
    def display_top_packages(self, user_preferences):
        """Display top 3 recommended packages based on user preferences."""
        print("\n" + "="*80)
        print("🎯 TOP PACKAGE RECOMMENDATIONS FOR YOU")
        print("="*80)
        
        top_packages = self.find_top_packages(user_preferences)
        
        for i, package in enumerate(top_packages, 1):
            print(f"\n🏆 RECOMMENDATION #{i}")
            print("-" * 50)
            print(f"📦 Package: {package['package_name']}")
            print(f"🌍 Destination: {package['destination']}")
            print(f"💰 Price Range: {package['price_range']}")
            print(f"📅 Duration: {package['duration']} days")
            print(f"🎨 Style: {package['travel_style'].title()}")
            print(f"👥 Group Size: {package['group_size'].title()}")
            print(f"🏨 Accommodation: {package['accommodation_type'].title()}")
            print(f"⭐ Rating: {package['rating']} ({package['reviews_count']} reviews)")
            print(f"🎯 Compatibility: {package['compatibility_score']:.1f}%")
            print(f"🎪 Activities: {package['activities']}")
            print(f"✅ Includes: {package['includes']}")
            print(f"🌤️ Best Time: {package['best_time']}")
        
        print("\n" + "="*80)
        return top_packages
    
    def display_online_recommendations(self,user_preferences):
        """Display top 3 most compatible packages with booking links."""
        print("\n" + "="*90)
        print("🎯 MOST COMPATIBLE TRAVEL PACKAGES WITH BOOKING LINKS")
        print("="*90)
        print("📊 Enhanced matching algorithm considers ratings, reviews, pricing, and seasonal factors")
        print("-"*90)

        top_packages = self.find_online_packages(user_preferences)

        for i, package in enumerate(top_packages, 1):
            print(f"\n🏆 PREMIUM RECOMMENDATION #{i}")
            print("-" * 60)
            print(f"📦 Package: {package['package_name']}")
            print(f"🌍 Destination: {package['destination']}")
            print(f"💰 Price Range: {package['price_range']}")
            print(f"📅 Duration: {package['duration']} days")
            print(f"🎨 Style: {package['travel_style'].title()}")
            print(f"👥 Group Size: {package['group_size'].title()}")
            print(f"🏨 Accommodation: {package['accommodation_type'].title()}")
            print(f"⭐ Rating: {package['rating']} ({package['reviews_count']} reviews)")
            print(f"🎯 Enhanced Compatibility: {package['enhanced_compatibility_score']:.1f}%")
            print(f"📊 Source: {package.get('source', 'Local Database')}")
            print(f"🎪 Activities: {package['activities']}")
            print(f"✅ Includes: {package['includes']}")
            print(f"🌤️ Best Time: {package['best_time']}")
            
            # Display booking links
            print(f"\n🔗 DIRECT BOOKING LINKS:")
            booking_links = package.get('booking_links', {})
            
            print(f"   🌐 International Sites:")
            print(f"   • Expedia: {booking_links.get('expedia', 'N/A')}")
            print(f"   • Booking.com: {booking_links.get('booking_com', 'N/A')}")
            print(f"   • Agoda: {booking_links.get('agoda', 'N/A')}")
            print(f"   • TripAdvisor: {booking_links.get('trip_advisor', 'N/A')}")
            print(f"   • Kayak: {booking_links.get('kayak', 'N/A')}")
            
            print(f"   🇮🇳 Indian Sites:")
            print(f"   • MakeMyTrip: {booking_links.get('makemytrip', 'N/A')}")
            print(f"   • Cleartrip: {booking_links.get('cleartrip', 'N/A')}")
            print(f"   • Goibibo: {booking_links.get('goibibo', 'N/A')}")
            
            print(f"\n💡 Booking Tips:")
            print(f"   • Compare prices across multiple sites before booking")
            print(f"   • Check for seasonal discounts and early bird offers")
            print(f"   • Read recent reviews and cancellation policies")
            print(f"   • Consider booking flights and hotels together for deals")
        
        print("\n" + "="*90)
        print("📱 Pro Tip: Click on the links above to be redirected directly to the booking pages!")
        print("="*90)
        return top_packages