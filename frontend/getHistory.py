# from asyncio.base_subprocess import ReadSubprocessPipeProto
import streamlit as st
import pandas as pd
# import json
from streamlit_option_menu import option_menu
from request import getHistory


# main function for get past prediction
def main():
    html_temp = """
                   <div style="background-color:orange;padding:10px">
                   <h3 style="color:white;text-align:center;"> House Price prediction history </h3>
                   </div>
                   """
    st.markdown(html_temp, unsafe_allow_html=True)
    response = getHistory() # call the getHistory function from request.py
    history = pd.DataFrame(response) # create a dataframe for the result to display
    st.dataframe(history) # display the dataframe


if __name__ == '__main__':
    main()