import streamlit as st
import pandas as pd
from Generate_Recommendations import Generator
from random import uniform as rnd
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts
from utils.css import load_sidebar_css
load_sidebar_css()
st.set_page_config(page_title="Automatic Diet Recommendation", page_icon="💪", layout="wide")

# ===================== THEME =====================
st.markdown("""
<style>
.stApp { background-color: #000000; }

html, body, p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #000000 !important;
    border: 2px solid #00FFFF !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] span { color: white !important; }
ul[role="listbox"] {
    background-color: #000000 !important;
    border: 2px solid #00FFFF !important;
}
li[role="option"] {
    background-color: #000000 !important;
    color: white !important;
}
li[role="option"]:hover {
    background-color: #00FFFF !important;
    color: black !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background-color: #000000 !important;
    color: white !important;
    border: 2px solid #00FFFF !important;
    border-radius: 8px;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    color: #00FFFF !important;
}
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "generated" not in st.session_state:
    st.session_state.generated = False
if "person" not in st.session_state:
    st.session_state.person = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

nutritions_values = [
    'Calories','FatContent','SaturatedFatContent','CholesterolContent',
    'SodiumContent','CarbohydrateContent','FiberContent',
    'SugarContent','ProteinContent'
]

# ===================== PERSON CLASS =====================
class Person:
    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss

    def calculate_bmr(self):
        if self.gender == 'Male':
            return 10*self.weight + 6.25*self.height - 5*self.age + 5
        else:
            return 10*self.weight + 6.25*self.height - 5*self.age - 161

    def calories_calculator(self):
        activities = [
            'Little/no exercise','Light exercise',
            'Moderate exercise (3-5 days/wk)',
            'Very active (6-7 days/wk)',
            'Extra active (very active & physical job)'
        ]
        weights = [1.2,1.375,1.55,1.725,1.9]
        return self.calculate_bmr() * weights[activities.index(self.activity)]

    def generate_recommendations(self):
        total_calories = self.weight_loss * self.calories_calculator()
        recommendations = []

        for meal in self.meals_calories_perc:
            meal_calories = self.meals_calories_perc[meal] * total_calories
            recommended_nutrition = [
                meal_calories,rnd(10,30),rnd(0,4),rnd(0,30),
                rnd(0,400),rnd(40,75),rnd(4,20),
                rnd(0,10),rnd(30,100)
            ]

            generator = Generator(recommended_nutrition)
            recipes = generator.generate().json()['output']
            recommendations.append(recipes)

        for recommendation in recommendations:
            for recipe in recommendation:
                recipe['image_link'] = find_image(recipe['Name'])

        return recommendations

# ===================== DISPLAY FUNCTION =====================
def display_recommendation(person, recommendations):

    meals = person.meals_calories_perc
    selected_recipes = []

    st.header("🍽 DIET RECOMMENDATOR")

    for meal_name, meal_rec in zip(meals, recommendations):
        recipe_names = [r['Name'] for r in meal_rec]
        choice = st.selectbox(meal_name.upper(), recipe_names, key=f"select_{meal_name}")
        for r in meal_rec:
            if r['Name'] == choice:
                selected_recipes.append(r)
                break

    total_nutrition = {nut: 0 for nut in nutritions_values}

    for index, recipe in enumerate(selected_recipes):

        col1, col2 = st.columns([1,2])

        with col1:
            st.image(recipe['image_link'], width=300)

        with col2:
            st.subheader(recipe['Name'])

            df = pd.DataFrame({val:[recipe[val]] for val in nutritions_values})
            st.dataframe(df, use_container_width=True)

            for nut in nutritions_values:
                total_nutrition[nut] += recipe[nut]

            with st.expander("Full Recipe Details"):

                st.markdown("### Ingredients")
                for ing in recipe['RecipeIngredientParts']:
                    st.write(f"- {ing}")

                st.markdown("### Instructions")
                for inst in recipe['RecipeInstructions']:
                    st.write(f"- {inst}")

                recipe_text = f"""
Recipe Name: {recipe['Name']}

Ingredients:
{chr(10).join(recipe['RecipeIngredientParts'])}

Instructions:
{chr(10).join(recipe['RecipeInstructions'])}
"""
                st.download_button(
                    "Download Recipe",
                    recipe_text,
                    file_name=f"{recipe['Name']}.txt",
                    mime="text/plain",
                    key=f"download_{index}"
                )

        st.markdown("---")

    # ================= CALORIES CHART =================
    target_calories = round(person.calories_calculator() * person.weight_loss)
    selected_calories = total_nutrition['Calories']

    st.subheader("Calories: Selected vs Target")

    options = {
        "backgroundColor": "#000000",
        "xAxis": {
            "type": "category",
            "data": ["Selected","Target"],
            "axisLabel": {"color": "#FFFFFF"}
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": "#FFFFFF"}
        },
        "series": [{
            "type": "bar",
            "data": [
                {"value": selected_calories, "itemStyle": {"color": "#00FFFF"}},
                {"value": target_calories, "itemStyle": {"color": "#FF00FF"}}
            ]
        }]
    }

    st_echarts(options=options, height="400px")

# ===================== MAIN =====================
st.markdown("<h1 style='text-align:center;'>Automatic Diet Recommendation</h1>", unsafe_allow_html=True)

with st.form("recommendation_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", 2, 120)
        gender = st.radio("Gender", ("Male","Female"))

    with col2:
        height = st.number_input("Height (cm)", 50, 300)
        weight = st.number_input("Weight (kg)", 10, 300)

    with col3:
        activity = st.select_slider("Activity", options=[
            'Little/no exercise','Light exercise',
            'Moderate exercise (3-5 days/wk)',
            'Very active (6-7 days/wk)',
            'Extra active (very active & physical job)'
        ])

    plans = ["Maintain weight","Mild weight loss","Weight loss","Extreme weight loss"]
    weights = [1,0.9,0.8,0.6]

    option = st.selectbox("Weight Plan", plans)
    weight_loss = weights[plans.index(option)]

    meals_calories_perc = {'breakfast':0.35,'lunch':0.40,'dinner':0.25}

    submit = st.form_submit_button("Generate Diet Plan 🚀")

    if submit:
        st.session_state.generated = True
        st.session_state.person = Person(
            age,height,weight,gender,activity,
            meals_calories_perc,weight_loss
        )

        with st.spinner("Generating recommendations..."):
            st.session_state.recommendations = (
                st.session_state.person.generate_recommendations()
            )

# ===================== SHOW RESULTS =====================
if st.session_state.generated and st.session_state.recommendations:
    display_recommendation(
        st.session_state.person,
        st.session_state.recommendations
    )