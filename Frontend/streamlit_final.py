
import pandas as pd

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

from request import postMultiRequest, postJsonRequest, getHistory


def uplaod_file():
    uploaded_file = st.empty()  # create a empty space
    uploaded_file = uploaded_file.file_uploader(
        label="Upload your csv file", type=['csv'])  # upload file
    return uploaded_file


# user input
def user_input():
    # create a dictionary to store the user input that will be passed to json request
    data = {"OverallQual": st.number_input("OverallQual"),
            "GrLivArea": st.number_input("GrLivArea"),
            "GarageArea": st.number_input("GarageArea"),
            "TotalBsmtSF": st.number_input("TotalBsmtSF"),
            "Street": st.selectbox("Street", ["Pave", "Grvl"]),
            "LotShape": st.selectbox("LotShape", ["Reg", "IR1", "IR2", "IR3"])}

    return data


def main():

    html_temp1 = """
                      <div style="background-color:orange;padding:10px">
                      <h2 style="color:white;text-align:center;">Welcome to House Price Prediction </h2>
                      </div>

                      """
    st.markdown(html_temp1, unsafe_allow_html=True)
    st.write("---")
    background = Image.open("Frontend/HousePrice.jpg")
    col1, col2, col3 = st.columns([0.2, 5, 0.2])
    col2.image(background, use_column_width=True)


    st.title("Loading data option")
    # create a empty space for the upload file display
    upload_file_display = st.empty()

    alert_message = st.sidebar.empty()  # create a empty space for the alert message
    # create a button for the prediction
    predict_button = st.sidebar.button("Predict", key="predict button")
    # contact_button = st.sidebar.button("Contact", key="contact button")  # create a button for the contact
    # create a horizontal sidebar for the user input
    selected = option_menu(None,
                           ["Upload_file", "Input_data"],
                           icons=['cloud-upload', 'edit'],
                           menu_icon="app-indicator",
                           default_index=0,
                           orientation="horizontal", )

    # if the user select the upload file option
    if selected == "Upload_file":
        uploaded_file = uplaod_file()

        # if the user upload a file
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            upload_file_display.write(df)  # display the file

        # if the user click on the predict button
        if predict_button and uploaded_file is not None:
            # call the postMultiRequest function from request.py
            result = postMultiRequest(uploaded_file)
            # create a dataframe for the result to display
            col = df.columns.to_list()
            col.append("SalePrcie")
            display = pd.DataFrame(result, columns=col)
            print(display)
            upload_file_display.table(display)  # display the result in a table

        # if the user click on the predict button and no file is uploaded
        if predict_button and uploaded_file is None:
            alert_message.warning("Please upload the file first")

    # if the user select the input data option
    if selected == 'Input_data':
        data = user_input()
        # print(data)
        if predict_button:
            # callddd the postJsonRequest function from request.py
            result = postJsonRequest(data)
            print(result)
            st.success("The HousePrice prediction is: {}".format(
                result[0][-1]))  # display the result


    #  create a button for the history
    history_button = st.sidebar.button("History", key="history button")
    if history_button:
        html_temp = """
                       <div style="background-color:red;padding:10px">
                       <h3 style="color:white;text-align:center;"> House Price Prediction History </h3>
                       </div>
                       """
        st.markdown(html_temp, unsafe_allow_html=True)
        # create empty space between the html_temp and the pciure
        st.write("---")
        background2 = Image.open("Frontend/hp.jpg")
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(background2, use_column_width=True)

        response = getHistory()  # call the getHistory function from request.py
        history = pd.DataFrame(response)  # create a dataframe for the result to display
        st.dataframe(history)  # display the dataframe


    # contact form
    # create a button for the contact
    contact_button = st.sidebar.button("Contact", key="contact button")
    # contact_button = st.button("Contact", key="contact button")
    contact_form = ""

    if contact_button:
        st.header(":mailbox: Get in Touch With Me!")
        # make sure to add ur maill id
        contact_form = """
        <form action="https://formsubmit.co/tingfen.yu@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="your name" required>
        <input type="email" name="email" placeholder="your mail" required>
        <button type="submit">Send</button>
        </form>
        """

    st.markdown(contact_form, unsafe_allow_html=True)



if __name__ == '__main__':
    main()
