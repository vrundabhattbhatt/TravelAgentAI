#!/usr/bin/env python3
"""
Accommodation Suggestions Module
Handles accommodation recommendations based on user preferences
"""


class AccommodationSuggester:
    """Handles accommodation suggestions based on user preferences."""
    
    def __init__(self):
        pass
    
    def get_accommodation_suggestions(self, preferences):
        """Generate accommodation suggestions based on user preferences."""
        destination = preferences.get('destination', '').lower()
        budget = preferences.get('budget', '').lower()
        travel_style = preferences.get('travel_style', '').lower()
        duration = preferences.get('duration', '')
        
        suggestions = []
        
        # Budget-based recommendations
        if any(word in budget for word in ['budget', 'cheap', 'low', 'affordable', '$']):
            suggestions.extend([
                "🏠 Budget-Friendly Options:",
                "- Hostels with private rooms or dorms",
                "- Budget hotels or motels",
                "- Airbnb shared spaces or private rooms",
                "- Guesthouses and B&Bs",
                "- Youth hostels (if applicable)"
            ])
        elif any(word in budget for word in ['luxury', 'high', 'premium', 'expensive']):
            suggestions.extend([
                "🏖️ Luxury Accommodations:",
                "- 5-star hotels and resorts",
                "- Luxury villas and penthouses",
                "- Boutique hotels with premium amenities",
                "- All-inclusive resorts",
                "- High-end vacation rentals"
            ])
        else:
            suggestions.extend([
                "🏨 Mid-Range Options:",
                "- 3-4 star hotels with good amenities",
                "- Well-reviewed Airbnb entire places",
                "- Business hotels with modern facilities",
                "- Serviced apartments for longer stays"
            ])
        
        # Travel style-based recommendations
        suggestions.append("")
        if travel_style == 'adventure':
            suggestions.extend([
                "🏔️ Adventure-Focused Stays:",
                "- Mountain lodges and cabins",
                "- Eco-lodges near nature activities",
                "- Camping sites and glamping options",
                "- Adventure hostels with gear rental"
            ])
        elif travel_style == 'relaxation':
            suggestions.extend([
                "🧘 Relaxation-Oriented:",
                "- Spa resorts and wellness retreats",
                "- Beachfront hotels with pools",
                "- Quiet countryside accommodations",
                "- Hotels with fitness and wellness facilities"
            ])
        elif travel_style == 'cultural':
            suggestions.extend([
                "🏛️ Cultural Immersion:",
                "- Hotels in historic districts",
                "- Traditional guesthouses or ryokans",
                "- Accommodations near museums and landmarks",
                "- Locally-owned boutique hotels"
            ])
        elif travel_style == 'business':
            suggestions.extend([
                "💼 Business-Friendly:",
                "- Business hotels with conference facilities",
                "- Hotels near business districts",
                "- Extended stay hotels for longer trips",
                "- Accommodations with reliable WiFi and workspaces"
            ])
        
        # Duration-based suggestions
        suggestions.append("")
        try:
            days = int(duration)
            if days >= 7:
                suggestions.extend([
                    "📅 Extended Stay Tips:",
                    "- Consider vacation rentals for better weekly rates",
                    "- Look for accommodations with kitchen facilities",
                    "- Extended stay hotels with laundry services"
                ])
        except ValueError:
            pass
        
        return suggestions
    
    def display_accommodation_suggestions(self, preferences):
        """Display accommodation suggestions with booking tips."""
        # Generate accommodation suggestions
        accommodation_suggestions = self.get_accommodation_suggestions(preferences)
        print("\n🏨 Accommodation Suggestions:")
        for suggestion in accommodation_suggestions:
            if suggestion:  # Skip empty strings used for spacing
                print(f"  {suggestion}")
            else:
                print()  # Add spacing
        
        # Add booking tips
        print("\n💡 Booking Tips:")
        print("  - Compare prices on multiple booking platforms")
        print("  - Read recent reviews from verified guests")
        print("  - Check cancellation policies before booking")
        print("  - Look for accommodations with good location ratings")
        
        # Popular booking platforms
        print("\n🔗 Recommended Booking Platforms:")
        print("  - Booking.com, Expedia, Hotels.com")
        print("  - Airbnb for unique stays and apartments")
        print("  - Agoda for Asia-Pacific destinations")
        print("  - Hostelworld for budget backpacker accommodations")
