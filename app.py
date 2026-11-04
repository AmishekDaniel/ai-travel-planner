import streamlit as st
from rag import Planner

@st.cache_resource(show_spinner="Loading AI model (first time only)...")
def get_planner():
    return Planner()
from datetime import date, timedelta

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b132b, #1c2541, #3a506b);
   }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #02040f, #0b132b);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("✈️ Travel Planner")

with st.sidebar:
    st.header("Plan Your Trip")
    destination = st.selectbox("Destination",["Goa", "Kerala", "Rajasthan", "Delhi", "Himachal", "Tamil Nadu", "Kashmir"])
    days = st.selectbox("Number of Days", [1,2,3,4,5,6,7])
    trip_type = st.selectbox("Trip Type",["Relaxation", "Adventure", "Couple", "Family", "Solo"])
    budget = st.slider("Budget", 5000, 50000, 15000, step=1000)
    start_date = st.date_input("Start Date", date.today())
    end_date = start_date + timedelta(days=days-1)
    st.date_input("End Date", end_date, disabled=True)
    generate = st.button("Generate Itinerary")

if generate:
    query = f"""
You are a professional travel planner.
Plan a {days} day {trip_type} trip to {destination}
with a budget of ₹{budget}.
Travel dates from {start_date} to {end_date}.

STRICTLY include these fields at the top:
Best Time to Visit: <Month> to <Month>
Estimated Budget: ₹<number>
Best Time to Visit MUST be in this format:Month to Month
Example: October to February
No extra words.

STRICTLY use this format:
Day 1:
- Morning:
- Afternoon:
- Evening:
Day 2:
- Morning:
- Afternoon:
- Evening:
Day 3:


- Trip Budget:
- Accommodation: ₹<number>
- Food & Activities: ₹<number>
- Transportation: ₹<number>
-------------------------------
- Total Estimated: ₹<number>
- Your Budget: ₹{budget} 
-------------------------------
Tips:
- Tip 1
- Tip 2 
- Tip 3
- Tip 4
(Give four to five tips)
Hotels: 
Example-
(- Luxury: Taj
- Mid: Radisson)

EMOJI RULES:
- Use at most ONE emoji per line.
- Place emoji ONLY at the END of the line.
- Do NOT use emojis in headings.
- Do NOT use emojis in Trip Budget numbers.
- Use only relevant travel emojis.

"""

    with st.spinner("Planning your trip..."):
        try:
            answer = get_planner().answer(query)
        except Exception as e:
            st.error(f"Could not generate the plan: {e}")
            st.stop()

    try:
        best_time = answer.split("Best Time to Visit:")[1].split("\n")[0].strip()
        estimated_budget = answer.split("Total Estimated:")[1].split("\n")[0].replace("₹", "").strip()
        budget_only = answer.split("Trip Budget:")[1].split("Tips:")[0].strip()
        if "Hotels:" in answer:
            tips_text = answer.split("Tips:")[1].split("Hotels:")[0].strip()
            hotel_text = answer.split("Hotels:")[1].strip()
        else:
            tips_text = answer.split("Tips:")[1].strip()
            hotel_text = ""

        main_part = answer.split("Trip Budget:")[0]
        day_contents = main_part.split("Day ")[1:]
        day_contents = ["Day " + d.strip() for d in day_contents]

        colA, colB = st.columns(2)

        with colA:
            st.info(f"📅 Best Time to Visit: {best_time}")

        with colB:
            st.success(f"💰 Estimated Budget: ₹{estimated_budget}")


        tab1, tab2, tab3, tab4= st.tabs(["🗺️ Itinerary", "💰 Budget", "🏨 Hotels", "📝 Tips"])

        with tab1:
            st.subheader(f"{days}-Day {destination} Itinerary")
            for day in day_contents:
                st.markdown("### " + day)

        with tab2:
            st.subheader("Trip Budget")
            if budget_only:
                st.write(budget_only)
                st.markdown("*Note: Budget may vary slightly depending on the number of persons.*")
            else:
                st.info("No budget details found.")

        with tab3:
            st.subheader("Hotel Suggestions")
            if hotel_text:
                st.write(hotel_text)
                st.markdown("*Hotel availability and pricing may vary depending on season and demand.*")
            else:
                st.info("No Hotel suggestions found.")

        with tab4:
            st.subheader("Travel Tips")
            if tips_text: 
                st.write(tips_text)
            else:
                st.info("No tips found.")
    except Exception:
        st.warning("Showing the raw result (format was unexpected):")
        st.markdown(answer)
