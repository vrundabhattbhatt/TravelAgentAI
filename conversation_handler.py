#!/usr/bin/env python3
"""
Conversation Handler Module
Manages post-recommendations AI-powered conversation with users
"""


class ConversationHandler:
    """Handles AI-powered conversation after travel package recommendations."""
    
    def __init__(self, openai_client=None):
        """Initialize the ConversationHandler."""
        self.client = openai_client
    
    def check_exit_keywords(self, user_input):
        """Check if user wants to exit the conversation."""
        exit_keywords = ['exit', 'close', 'end', 'quit', 'goodbye', 'bye']
        return any(keyword in user_input.lower() for keyword in exit_keywords)
    
    def get_ai_package_recommendation(self, user_question, preferences, top_packages):
        """Use OpenAI to analyze user question and recommend the most suitable package."""
        if not self.client:
            return self.fallback_package_recommendation(user_question, top_packages)
        
        try:
            # Prepare package information for AI analysis
            packages_info = ""
            for i, package in enumerate(top_packages, 1):
                packages_info += f"""
Package {i}: {package['package_name']}
- Destination: {package['destination']}
- Price: {package['price_range']}
- Duration: {package['duration']} days
- Style: {package['travel_style']}
- Group Size: {package['group_size']}
- Accommodation: {package['accommodation_type']}
- Rating: {package['rating']} ({package['reviews_count']} reviews)
- Activities: {package['activities']}
- Includes: {package['includes']}
- Best Time: {package['best_time']}
- Compatibility Score: {package['compatibility_score']:.1f}%
"""
            
            system_prompt = f"""You are a travel expert helping a user choose the best travel package. 
The user has the following preferences:
- Destination: {preferences.get('destination', 'Not specified')}
- Budget: {preferences.get('budget', 'Not specified')}
- Duration: {preferences.get('duration', 'Not specified')} days
- Travel Style: {preferences.get('travel_style', 'Not specified')}
- Group Size: {preferences.get('group_size', 'Not specified')}
- Accommodation: {preferences.get('accommodation_type', 'Not specified')}

Here are the top 3 recommended packages:
{packages_info}

Based on the user's question and their preferences, recommend the most suitable package and explain why. 
Be conversational, helpful, and provide specific reasons for your recommendation. 
If the user asks for general advice or has questions about travel, answer helpfully while relating back to their packages when relevant.
Keep your response concise but informative."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Error getting AI recommendation: {e}")
            return self.fallback_package_recommendation(user_question, top_packages)
    
    def fallback_package_recommendation(self, user_question, top_packages):
        """Fallback recommendation when OpenAI is not available."""
        if any(word in user_question.lower() for word in ['recommend', 'suggest', 'best', 'which', 'choose']):
            if top_packages:
                best_package = top_packages[0]  # Highest compatibility score
                return f"""Based on your preferences, I recommend **{best_package['package_name']}** to {best_package['destination']}.

Here's why it's the best match for you:
- 🎯 Highest compatibility score: {best_package['compatibility_score']:.1f}%
- ⭐ Great rating: {best_package['rating']} stars with {best_package['reviews_count']} reviews
- 💰 Price range matches your budget: {best_package['price_range']}
- 🎨 Perfect for {best_package['travel_style']} travel style
- 🏨 Includes {best_package['accommodation_type']} accommodation

This package offers: {best_package['activities']} and includes {best_package['includes']}.

Would you like more details about this package or have any other questions?"""
        
        return "I'd be happy to help you with more information about the travel packages or answer any questions you have about your trip planning!"
    
    def start_conversation(self, preferences, top_packages):
        """Handle conversation after showing recommendations."""
        print("\n" + "="*80)
        print("💬 PERSONALIZED TRAVEL CONSULTATION")
        print("="*80)
        print("I'm here to help you choose the perfect package or answer any travel questions!")
        print("Ask me anything about the recommended packages, destinations, or travel tips.")
        print("(Type 'exit', 'close', or 'end' to finish the conversation)")
        print("-"*80)
        
        while True:
            try:
                user_input = input("\n🤔 Your question: ").strip()
                
                if not user_input:
                    print("💭 Please ask me anything about your travel packages or type 'exit' to finish.")
                    continue
                
                # Check for exit keywords
                if self.check_exit_keywords(user_input):
                    print("\n👋 Thank you for using Travel Agent AI!")
                    print("Have a wonderful trip! 🌍✈️")
                    break
                
                # Get AI-powered response
                print("\n🤖 Travel Agent AI:")
                ai_response = self.get_ai_package_recommendation(user_input, preferences, top_packages)
                print(ai_response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Feel free to come back anytime for travel planning help.")
                break
            except Exception as e:
                print(f"\n⚠️ Sorry, I encountered an error: {e}")
                print("Please try asking your question again.")
