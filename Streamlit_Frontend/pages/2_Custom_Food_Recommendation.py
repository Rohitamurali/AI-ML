import streamlit as st
from Generate_Recommendations import Generator
from ImageFinder.ImageFinder import get_images_links as find_image
import pandas as pd
from streamlit_echarts import st_echarts
from utils.css import load_sidebar_css
load_sidebar_css()

st.set_page_config(page_title="Custom Food Recommendation", page_icon="🔍",layout="wide")
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
.stApp {
    background-color: #000000;
    color: white !important;
}

/* Force all text white */
html, body, p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

/* ===== MAIN CARD ===== */
.main-card {
    background-color: #111111;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #00FFFF;
    box-shadow: 0px 0px 20px rgba(0,255,255,0.3);
    margin-top: 20px;
    margin-bottom: 20px;
}

/* ===== RECIPE CARD ===== */
.recipe-card {
    background-color: #111111;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #00FFFF;
    box-shadow: 0px 0px 15px rgba(0,255,255,0.2);
    margin-bottom: 20px;
    transition: 0.3s ease;
}

.recipe-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 0px 25px #00FFFF;
}
/* ===== GENERATE RECOMMENDATIONS BUTTON ===== */
generated = st.form_submit_button("Generate Recommendations", key="generate_btn")
div[data-testid="stForm"] button[kind="primary"][data-testid="stButton"] {
    background-color: #000000 !important;
    color: #FFFFFF !importants;
    border: 2px solid #00FFFF !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
}

/* Hover effect */
div[data-testid="stForm"] button[kind="primary"][data-testid="stButton"]:hover {
    background-color: #111111 !important;
    color: #00FFFF !important;
    border: 2px solid #00FFFF !important;
}


/* ===== DOWNLOAD RECIPE BUTTON ===== */
.stDownloadButton > button {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #00FFFF !important;
    border-radius: 8px !important;
}

/* Hover effect */
.stDownloadButton > button:hover {
    background-color: #111111 !important;
    color: #00FFFF !important;
    border: 2px solid #00FFFF !important;
}
/* ===== SELECTBOX IN OVERVIEW ===== */
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

</style>
""", unsafe_allow_html=True)




nutrition_values=['Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent']

if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations=None

# -------------------- RECOMMENDATION CLASS --------------------
class Recommendation:
    def __init__(self,nutrition_list,nb_recommendations,ingredient_txt):
        self.nutrition_list=nutrition_list
        self.nb_recommendations=nb_recommendations
        self.ingredient_txt=ingredient_txt

    def generate(self):
        params={'n_neighbors':self.nb_recommendations,'return_distance':False}
        ingredients=self.ingredient_txt.split(';') if self.ingredient_txt else []
        generator=Generator(self.nutrition_list,ingredients,params)
        recommendations=generator.generate()
        recommendations = recommendations.json()['output']
        if recommendations:
            for recipe in recommendations:
                recipe['image_link']=find_image(recipe['Name'])
        return recommendations

# -------------------- DISPLAY CLASS --------------------
class Display:
    def __init__(self):
        self.nutrition_values=nutrition_values

    def display_recommendation(self,recommendations):
        st.subheader('Recommended Recipes:')
        if recommendations:
            for recipe in recommendations:
                with st.container():
                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    st.subheader(recipe['Name'])
                    st.image(recipe['image_link'], width=250)
                    st.markdown("**Nutritional Values:**")
                    df=pd.DataFrame({val:[recipe[val]] for val in self.nutrition_values})
                    st.dataframe(df,use_container_width=True)
                    with st.expander("📋 Ingredients & Instructions"):
                        st.markdown("**Ingredients:**")
                        for ing in recipe['RecipeIngredientParts']:
                            st.markdown(f"- {ing}")
                        st.markdown("**Instructions:**")
                        for ins in recipe['RecipeInstructions']:
                            st.markdown(f"- {ins}")
                        st.markdown(f"**Cook Time:** {recipe['CookTime']}min | **Prep Time:** {recipe['PrepTime']}min | **Total Time:** {recipe['TotalTime']}min")
                        recipe_text = f"""
Recipe Name: {recipe['Name']}

Ingredients:
{chr(10).join(recipe['RecipeIngredientParts'])}

Instructions:
{chr(10).join(recipe['RecipeInstructions'])}

Cook Time: {recipe['CookTime']} min
Prep Time: {recipe['PrepTime']} min
Total Time: {recipe['TotalTime']} min
"""
                        st.download_button(label="Download Recipe", data=recipe_text,
                                           file_name=f"{recipe['Name']}.txt",
                                           mime="text/plain", key=f"download_{recipe['Name']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No recipes found with the specified ingredients.", icon="🙁")

    def display_overview(self,recommendations):
        if recommendations:
            st.subheader("Overview of Selected Recipe:")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                selected_name = st.selectbox("Select a recipe to visualize nutrition:", [r['Name'] for r in recommendations])
            selected_recipe = next((r for r in recommendations if r['Name']==selected_name), None)
            if selected_recipe:
                options = {
                    "title": {"text": "Nutrition Values", "subtext": f"{selected_name}", "left": "center"},
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"},
                    "series": [{
                        "name": "Nutrition Values",
                        "type": "pie",
                        "radius": "50%",
                        "data":[{"value":selected_recipe[n], "name":n} for n in self.nutrition_values],
                        "emphasis": {"itemStyle":{"shadowBlur":10,"shadowOffsetX":0,"shadowColor":"rgba(0,0,0,0.5)"}}
                    }]
                }
                st_echarts(options=options, height="600px")
                st.caption("You can toggle nutrition items from the legend.")

# -------------------- MAIN UI --------------------
st.markdown("<h1 style='text-align:center;'>Custom Food Recommendation</h1>", unsafe_allow_html=True)

display=Display()

# Nutrition Form
st.markdown('<div class="main-card">', unsafe_allow_html=True)
with st.form("recommendation_form"):
    st.header("Specify Nutritional Values:")
    Calories = st.slider('Calories', 0, 2000, 500)
    FatContent = st.slider('FatContent', 0, 100, 50)
    SaturatedFatContent = st.slider('SaturatedFatContent', 0, 13, 0)
    CholesterolContent = st.slider('CholesterolContent', 0, 300, 0)
    SodiumContent = st.slider('SodiumContent', 0, 2300, 400)
    CarbohydrateContent = st.slider('CarbohydrateContent', 0, 325, 100)
    FiberContent = st.slider('FiberContent', 0, 50, 10)
    SugarContent = st.slider('SugarContent', 0, 40, 10)
    ProteinContent = st.slider('ProteinContent', 0, 40, 10)
    nutrition_list=[Calories,FatContent,SaturatedFatContent,CholesterolContent,SodiumContent,CarbohydrateContent,FiberContent,SugarContent,ProteinContent]

    st.header("Recommendation Options (Optional):")
    nb_recommendations = st.slider('Number of recommendations', 5, 20, step=5)
    ingredient_txt = st.text_input('Include Ingredients (separate with ";")', placeholder='Milk;Eggs;Chicken;Butter')
    st.caption('Example: Milk;Eggs;Butter;Chicken...')
    generated = st.form_submit_button("Generate Recommendations")
st.markdown('</div>', unsafe_allow_html=True)

if generated:
    with st.spinner("Generating recommendations..."):
        rec = Recommendation(nutrition_list, nb_recommendations, ingredient_txt)
        recommendations = rec.generate()
        st.session_state.recommendations = recommendations
    st.session_state.generated = True

if st.session_state.generated:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    display.display_recommendation(st.session_state.recommendations)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    display.display_overview(st.session_state.recommendations)
    st.markdown('</div>', unsafe_allow_html=True)