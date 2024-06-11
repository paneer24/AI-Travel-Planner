import os
import google.generativeai as genai
import streamlit as st
from datetime import date, timedelta
import re

# Initialize the application's title and subtitle
st.title('AI Travel Planner')
st.subheader('Plan your next trip with AI')

# User input section in the sidebar
st.sidebar.header('Enter details to generate a travel plan:')
api_key = st.sidebar.text_input('Enter Your Google API Key', type="password")
source = st.sidebar.text_input('Source', 'Tamilnadu')
destination = st.sidebar.text_input('Destination', 'Kerala')
date_input = st.sidebar.date_input('Travel Start Date', min_value=date.today())
date = date_input.strftime('%Y-%m-%d')
budget = st.sidebar.number_input('Budget', min_value=100, value=1000, step=100)
duration = st.sidebar.slider('Duration (days)', 1, 90, 7)

# Currency selector
currencies = ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'AUD']  # Add more currencies as needed
selected_currency = st.sidebar.selectbox('Select Currency', currencies)

# Additional user preferences
st.sidebar.subheader('Your Preferences:')
language_preference = st.sidebar.selectbox('Language Preference', ['English', 'Tamil', 'Hindi', 'French', 'German', 'Japanese'], index=0)
interests = st.sidebar.text_input('Interests', 'historical sites, nature')
past_travel = st.sidebar.text_input('Past Travel Destinations', 'Coimbatore')
dietary_restrictions = st.sidebar.text_input('Dietary Restrictions', 'None')
activity_level = st.sidebar.selectbox('Activity Level', ['Low', 'Moderate', 'High'])
specific_interests = st.sidebar.text_input('Specific Interests', 'art museums, hiking trails')
accommodation_preference = st.sidebar.selectbox('Accommodation Preference', ['Hotel', 'Hostel', 'Apartment', 'No Preference'])
travel_style = st.sidebar.selectbox('Travel Style', ['Relaxed', 'Fast-Paced', 'Adventurous', 'Cultural', 'Family-Friendly'])
must_visit_landmarks = st.sidebar.text_input('Must-Visit Landmarks', 'e.g., Bekal fort, Arakkal Museum')

# Function to create a detailed message for the AI
def get_personalized_travel_plan(user_preferences, trip_details, api_key, selected_currency):
    genai.configure(api_key=api_key)
    
    # Calculate daily budget breakdown
    daily_budget = trip_details['budget'] // trip_details['duration']
    accommodation_budget = daily_budget * 4 // 10  # 40% for accommodation
    food_budget = daily_budget * 3 // 10  # 30% for food
    transportation_budget = daily_budget * 2 // 10  # 20% for transportation
    activities_budget = daily_budget * 1 // 10  # 10% for activities
    
    message = (
        f"Create a detailed travel itinerary in {user_preferences['language_preference']} focused on attractions, restaurants, and activities for a trip from "
        f"{trip_details['source']} to {trip_details['destination']}, starting on {trip_details['date']}, lasting for "
        f"{trip_details['duration']} days, within a budget of {selected_currency} {trip_details['budget']}. This should include daily timings, "
        f"preferences for {user_preferences['accommodation_preference']} accommodations, a {user_preferences['travel_style']} travel style, "
        f"and interests in {user_preferences['interests']}. Past travel includes {user_preferences['past_travel']}, dietary restrictions include "
        f"{user_preferences['dietary_restrictions']}, and the activity level is {user_preferences['activity_level']}. "
        f"Must-visit landmarks include {user_preferences['must_visit_landmarks']}. Also, provide a travel checklist relevant to the destination and duration. "
        f"Include a budget breakdown for each day with {selected_currency} {accommodation_budget} for accommodation, {selected_currency} {food_budget} for food, "
        f"{selected_currency} {transportation_budget} for transportation, and {selected_currency} {activities_budget} for activities."
    )
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    
    # Parse the response to include Google Maps links for each day
    travel_plan = response.text
    travel_plan_with_maps = ""
    start_date = date_input
    
    # Split the travel plan by days
    days = travel_plan.split("Day ")
    
    # Iterate over each day and add Google Maps link
    for day in range(1, trip_details['duration'] + 1):
        current_date = start_date + timedelta(days=day - 1)
        day_text = f"**Day {day} ({current_date.strftime('%Y-%m-%d')})**\n"
        
        # Extract the content for the current day
        if day < trip_details['duration']:
            day_content = days[day].split(f"Day {day + 1}:")[0]
        else:
            day_content = days[day]

        day_content = day_content.replace("[View on Google Maps]", "")  # Remove the unwanted Google Maps link
        day_text += day_content
        day_text += (
            f"\n**Budget for the day:**\n"
            f"- Accommodation: {selected_currency} {accommodation_budget}\n"
            f"- Food: {selected_currency} {food_budget}\n"
            f"- Transportation: {selected_currency} {transportation_budget}\n"
            f"- Activities: {selected_currency} {activities_budget}\n"
        )
        day_text += f"\n[View on Google Maps](https://www.google.com/maps/dir/?api=1&origin={trip_details['source']}&destination={trip_details['destination']}&travelmode=driving)\n\n"
        travel_plan_with_maps += day_text
    
    return travel_plan_with_maps

# Collecting user preferences and trip details for travel planning
user_preferences = {
    'language_preference': language_preference,
    'interests': interests,
    'past_travel': past_travel,
    'dietary_restrictions': dietary_restrictions,
    'activity_level': activity_level,
    'specific_interests': specific_interests,
    'accommodation_preference': accommodation_preference,
    'travel_style': travel_style,
    'must_visit_landmarks': must_visit_landmarks
}
trip_details = {
    'source': source,
    'destination': destination,
    'date': date,
    'budget': budget,
    'duration': duration
}

# Button to generate the travel plan
if st.sidebar.button('Generate Travel Plan'):
    if api_key and source and destination and date and budget and duration:
        with st.spinner('Generating Travel Plan...'):
            response = get_personalized_travel_plan(user_preferences, trip_details, api_key, selected_currency)
        st.success('Here is your personalized travel plan in ' + language_preference + ':')
        st.markdown(response)
    else:
        st.error('Please fill in all the fields to generate the travel plan.')
