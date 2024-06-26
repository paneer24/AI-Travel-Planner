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
source = st.sidebar.text_input('Source', 'Chennai')
destination = st.sidebar.text_input('Destination', 'Kerala')
date_input = st.sidebar.date_input('Travel Start Date', min_value=date.today())
date = date_input.strftime('%Y-%m-%d')
duration = st.sidebar.slider('Duration (days)', 1, 90, 7)


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
def get_personalized_travel_plan(user_preferences, trip_details, api_key):
    genai.configure(api_key=api_key)
    
    message = (
        f"Create a detailed travel itinerary in {user_preferences['language_preference']} focused on attractions, restaurants, and activities for a trip from "
        f"{trip_details['source']} to {trip_details['destination']}, starting on {trip_details['date']}, lasting for "
        f"{trip_details['duration']} days. This should include daily timings, preferences for {user_preferences['accommodation_preference']} accommodations, "
        f"a {user_preferences['travel_style']} travel style, and interests in {user_preferences['interests']}. Past travel includes {user_preferences['past_travel']}, "
        f"dietary restrictions include {user_preferences['dietary_restrictions']}, and the activity level is {user_preferences['activity_level']}. "
        f"Must-visit landmarks include {user_preferences['must_visit_landmarks']}. Also, provide a travel checklist relevant to the destination and duration."
    )
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    
    # Parse the response to include Google Maps links for each day
    travel_plan = response.text
    travel_plan_with_maps = ""
    start_date = date_input
    
    # Split the travel plan by days
    days = travel_plan.split("Day ")
    
    # Check if there's a travel checklist and separate it
    if "Travel Checklist:" in travel_plan:
        travel_plan, travel_checklist = travel_plan.split("Travel Checklist:")
        travel_checklist = "Travel Checklist:" + travel_checklist
    else:
        travel_checklist = ""
    
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
        day_text += f"\n[View on Google Maps](https://www.google.com/maps/dir/?api=1&origin={trip_details['source']}&destination={trip_details['destination']}&travelmode=driving)\n\n"
        travel_plan_with_maps += day_text
    
    travel_plan_with_maps += travel_checklist  # Add the travel checklist at the end
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
    'duration': duration
}

# Button to generate the travel plan
if st.sidebar.button('Generate Travel Plan'):
    if api_key and source and destination and date and duration:
        with st.spinner('Generating Travel Plan...'):
            response = get_personalized_travel_plan(user_preferences, trip_details, api_key)
        st.success('Here is your personalized travel plan in ' + language_preference + ':')
        st.markdown(response)
    else:
        st.error('Please fill in all the fields to generate the travel plan.')
