import streamlit as st
import spotipy
import spotipy.util as util

# Client ID and secret for your application
client_id = 'your_client_id'
client_secret = 'your_client_secret'
redirect_uri = 'http://localhost:8881/'

scope = 'user-library-read'
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri=redirect_uri,
                                                       scope=scope))

@st.cache_data(show_spinner=False)
def get_user_playlists():
    return sp.current_user_playlists()

# Use Streamlit components to display results
st.title("My Spotify Playlists")
resp = get_user_playlists()

if resp:
    for playlist in resp['items']:
        st.write(f"Playlist Name: {playlist['name']}")
        st.write(f"Owner: {playlist['owner']['display_name']}")
        st.write(f"Total Tracks: {playlist['tracks']['total']}")
        
        if playlist['images']:
            st.image(playlist['images'][0]['url'], caption='Playlist Image')
        else:
            st.write("No playlist image available")
        
        st.markdown('---')  # Separator between playlists
else:
    st.write("Couldn't fetch playlists. Please check your authentication.")