# Import python packages
import streamlit as st
import requests
import pandas
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits for your smoothie
    """
)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)


customer_name = st.text_input('Your Name')
ingredients_list = st.multiselect('Choose up to 5 ingredients', my_dataframe,
                                 max_selections = 5)

if ingredients_list and customer_name:
    ingredients_string = ''
    for fruit in ingredients_list:
        ingredients_string += fruit + ' '
        st.subheader(fruit + ' Nutrition Information')
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        
    
    my_insert_stmt = """insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string +"""',
                '"""+ customer_name +"""')"""

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+ customer_name +'!', icon="✅")
        
