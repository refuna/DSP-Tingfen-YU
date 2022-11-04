from cgitb import html
import streamlit as st
from PIL import Image

# first page of the app

def main():
    # webapp title
    html_temp = """
                  <div style="background-color:orange;padding:10px">
                  <h2 style="color:white;text-align:center;">Welcome to House Price Prediction  ML App </h2>
                  </div>
                  """
    st.markdown(html_temp, unsafe_allow_html=True)

    background = Image.open("HousePrice.jpg")
    col1, col2, col3 = st.columns([0.2, 5, 0.2])
    col2.image(background, use_column_width=True)

if __name__ == '__main__':
    main()
