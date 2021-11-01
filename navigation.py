import streamlit as st
import base64


def navigation(nav, df_crimi2):

    if nav == "Home":
        st.image("Afbeeldingen/Home page.gif", width=1400,)


    elif nav == "results":
        st.title('Results List')
        for item in range(25):
            st.write(f'Results {item}')

    elif nav == "Dataframe":
        st.title("Het gedownloade dataframe")
        st.write("Dit dataframe word automatisch dagelijks geupdate. De data waarmee dit gecreerd word heeft een tragere interval. ")
        st.dataframe(df_crimi2)

