import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from request import postMultiRequest,postJsonRequest


# upload file
def uplaod_file():
    uploaded_file = st.empty() # create a empty space
    uploaded_file = uploaded_file.file_uploader(label="Upload your csv file", type=['csv']) # upload file
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


# main function
def main():
    st.title("Loading data option")
    upload_file_display = st.empty() # create a empty space for the upload file display

    alert_message = st.sidebar.empty() # create a empty space for the alert message
    predict_button = st.sidebar.button("Predict", key="predict button") # create a button for the prediction
    contact_button = st.sidebar.button("Contact", key="contact button") # create a button for the contact
    # create a horizontal sidebar for the user input
    selected = option_menu(None,
                           ["Upload_file", "Input_data"],
                           icons=['cloud-upload', 'edit'],
                           menu_icon="app-indicator",
                           default_index=0,
                           orientation="horizontal",)

    # if the user select the upload file option
    if selected == "Upload_file":
        uploaded_file = uplaod_file()

        # if the user upload a file
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            upload_file_display.write(df) # display the file

        # if the user click on the predict button
        if predict_button and uploaded_file is not None:
            result = postMultiRequest(uploaded_file) # call the postMultiRequest function from request.py
            # create a dataframe for the result to display
            col = df.columns.to_list()
            col.append("SalePrcie")
            display = pd.DataFrame(result, columns= col)
            print(display)
            upload_file_display.table(display) # display the result in a table

        # if the user click on the predict button and no file is uploaded
        if predict_button and uploaded_file is None:
            alert_message.warning("Please upload the file first")

    # if the user select the input data option
    elif selected == 'Input_data':
        data = user_input()
        # print(data)
        if predict_button:
            result = postJsonRequest(data) # call the postJsonRequest function from request.py
            print(result)
            st.success("The HousePrice prediction is: {}".format(result[0][-1])) # display the result


if __name__ == '__main__':
    main()







