import streamlit as st
import base64


def navigation(nav):

    if nav == "Home":
        # # st.markdown("Afbeeldingen/Home page.gif")
        # """### gif from local file"""
        # file_ = open("Afbeeldingen/Home page.gif", "rb")
        # contents = file_.read()
        # data_url = base64.b64encode(contents).decode("utf-8")
        # file_.close()
        #
        # st.markdown(
        #     f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        #     unsafe_allow_html=True,
        # )

        st.image("Afbeeldingen/Home page.gif", width=1400,)


        # st.title('Home')
        #
        # st.write('Dit dashboard bevat informatie over criminaliteit in Nederland. '
        #         'De gegevens word wekelijks geupdate en is het beste te zien op een 1920x1080 scherm. '
        #         '\nGemaakt door Sjoerd Fijnje en Mirko Bosch in opdracht van de HvA minor Data Science.')

    elif nav == "results":
        st.title('Results List')
        for item in range(25):
            st.write(f'Results {item}')

    elif nav == "analysis":
        st.title('Analysis')
        x, y = st.number_input('Input X'), st.number_input('Input Y')
        st.write('Result: ' + str(x+y))

    elif nav == "examples":
        st.title('Examples Menu')
        st.write('Select an example.')


    elif nav == "logs":
        st.title('View all of the logs')
        st.write('Here you may view all of the logs.')


    elif nav == "verify":
        st.title('Data verification is started...')
        st.write('Please stand by....')


    elif nav == "config":
        st.title('Configuration of the app.')
        st.write('Here you can configure the application')