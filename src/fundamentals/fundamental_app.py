import streamlit as st
import degiroapi


def authentication(degiro, user, password, topt=None):
    try:
        degiro.login(user, password, topt)
        return True
    except:
        return False

# --- Payload code of each page


def home():
    st.write('Welcome to home page')
    link = '[GitHub](http://github.com)'
    st.markdown(link, unsafe_allow_html=True)
    st.checkbox('Check me', key='check1')
    if st.button('Click Home'):
        st.write('Welcome to home page')


def slider():
    st.write('Welcome to the slider page')
    slide1 = st.slider('this is a slider', min_value=0, max_value=15, key='slider1')
    st.write('Slider position:', slide1)


def contact():
    st.title('Welcome to contact page')
    st.write(f'Multipage app. Streamlit {st.__version__}')
    if st.button('Click Contact'):
        st.write('Welcome to contact page')


# --- Callback functions
def CB_HomeButton():
    st.session_state.active_page = 'Home'


def CB_SliderButton():
    st.session_state.active_page = 'Slider'


def CB_ContactButton():
    st.session_state.active_page = 'Contact'


def main():
    # --- Page selection buttons
    col1, col2, col3 = st.columns(3)
    col1.button('Home', on_click=CB_HomeButton)
    col2.button('Slider', on_click=CB_SliderButton)
    col3.button('Contact', on_click=CB_ContactButton)
    st.write('____________________________________________________________________')

    # --- Run the active page
    if st.session_state.active_page == 'Home':
        home()
    elif st.session_state.active_page == 'Slider':
        slider()
    elif st.session_state.active_page == 'Contact':
        contact()


if __name__ == "__main__":
    # Initialization
    st.session_state.update(st.session_state)
    degiro = degiroapi.DeGiro()
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'Home'
        st.session_state.slider1 = 0
        st.session_state.check1 = False
        st.session_state.auth = False
        st.session_state.totp = False

    if not st.session_state.auth:
        if not st.session_state.totp:
            col1, col2, col3 = st.columns([1, 3.5, 1])
            col2.subheader("Bienvenido. Por favor, inicie sesión.")
            user = col2.text_input('User', key='user', value="")
            password = col2.text_input('Password', type="password", value="")
            login_button = col2.button("Login")
            if 'login_button' not in locals():
                login_button = False
            if login_button and user and password:
                if authentication(degiro, user, password):
                    st.success(f'Logged as {user}')
                    st.session_state.auth = True
                else:
                    st.session_state.totp = True
            st.experimental_rerun()
        else:
            col1, col2, col3 = st.columns([1, 3.5, 1])
            col2.subheader("Por favor, introduzca el código-GA")
            totp = col2.text_input('Code_verification', value="")
            login_button = col2.button("Verification code")
            if 'login_button' not in locals():
                login_button = False
            if login_button:
                if authentication(degiro, st.session_state.user, st.session_state.password, totp):
                    st.session_state.auth = True
                    st.experimental_rerun()
                else:
                    st.error('Incorrect user/password')
                    st.session_state.totp = False
                    st.experimental_memo.clear()
                    st.experimental_rerun()

    else:
        main()
