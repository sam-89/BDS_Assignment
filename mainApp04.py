import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Client ID and secret for spotify API
client_id = '7a832874ab9243239180d6c34dc02f02'
client_secret = '5a95c79436ee4f90a3d73958b19f2de0'
redirect_uri = 'http://localhost:8881/'
scope = 'user-library-read'

# Initialize the Spotify client
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri=redirect_uri,
                                                       scope=scope))

## Initialize MongoDB           
uri = "mongodb+srv://myAtlasDBUser:myatlas-001@myatlasclusteredu.xliqzij.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['Music_Recomendation']
collection = db['user_songs_recomended']
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)



@st.cache_data(show_spinner=False)

# Function to write song details to the database
def write_song_details_to_db(song_name, artist_name):
    song_details = get_song_details(song_name, artist_name)
    if song_details:
        collection.insert_one(song_details)

# Function to get the song details
def get_song_details(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        
        # Extracting more information
        song_id = track['id']
        song_duration_ms = track['duration_ms']
        release_date = track["album"]["release_date"]
        popularity = track["popularity"]
        explicit = track['explicit']
        album_name = track["album"]["name"]

        # Get audio features
        audio_features = sp.audio_features(song_id)
        if audio_features:
            audio_features = audio_features[0]
            danceability = audio_features['danceability']
            energy = audio_features['energy']
            key = audio_features['key']
            mode = audio_features['mode']
            speechiness = audio_features['speechiness']
            acousticness = audio_features['acousticness']
            instrumentalness = audio_features['instrumentalness']
            liveness = audio_features['liveness']
            valence = audio_features['valence']
            tempo = audio_features['tempo']
            time_signature = audio_features['time_signature']
        
        # Get artist genres
        artist_id = track["artists"][0]["id"]  # Assuming one main artist
        artist_info = sp.artist(artist_id)
        if artist_info:
            genres = artist_info['genres']
        
        # Create a dictionary containing all the information
        # Create a dictionary containing all the information
        song_info = {
            'id': song_id,
            'artists': artist_name,
            'album_name': album_name,
            'track_name': song_name,
            'popularity': popularity,
            'duration_ms': song_duration_ms,
            'explicit': explicit,
            'danceability': danceability,
            'energy': energy,
            'key': key,
            'mode': mode,
            'speechiness': speechiness,
            'acousticness': acousticness,
            'instrumentalness': instrumentalness,
            'liveness': liveness,
            'valence': valence,
            'tempo': tempo,
            'time_signature': time_signature,
            'track_genre': genres
        }
        return song_info
    else:
        # If no results found, return None or an empty dictionary
        return None
    
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        print(album_cover_url)
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"


def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        # fetch the song poster
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        album_cover_url = get_song_album_cover_url(song_name, artist)
        print(artist)
        print(music.iloc[i[0]].song)
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)

        # Write recommended song details to the DB
        write_song_details_to_db(song_name, artist)

        
    return recommended_music_names,recommended_music_posters


## UI - Interface
# Displaying an image and details above the header
st.image('images/BITS_Logo.png', width=200)
st.markdown('''
        #### This Project was done as a part of Big Data and Systems Assignment.
            **Submitted By:**
                1. Sumanta Kumar Patel - 2022OG04032
                2. Rahul Khandpur - 2022OG04037
''')

st.header('Music Recommender System')
music = pickle.load(open('df.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

music_list = music['song'].values
selected_music = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

if st.button('Show Recommendation'):
    recommended_music_names,recommended_music_posters = recommend(selected_music)

    num_columns = 3  # Number of columns in the grid layout
    num_recommendations = len(recommended_music_names)

    # Display recommendations using a grid layout
    col_list = st.columns(num_columns)
    for i in range(num_recommendations):
        col_index = i % num_columns
        with col_list[col_index]:
            st.text(recommended_music_names[i])
            st.image(recommended_music_posters[i])

# OLTP query execution section
st.sidebar.header("Execute OLTP Queries")
query_type = st.sidebar.selectbox("Select Query Type", ["Find One", "Find", "Count"])

if query_type == "Find One" or query_type == "Count":
    query_data = st.sidebar.text_input("Enter Query Data (JSON format)")
else:
    query_data = st.sidebar.text_area("Enter Query Data (JSON format)")

if st.sidebar.button("Execute Query"):
    try:
        query_data = eval(query_data)  # Convert input string to dictionary
        if query_data['query_type'] == "find_one":
            # Extract collection name and filter criteria from query_data
            collection_name = query_data['collection_name']
            filter_criteria = query_data['filter']
            # Execute the find one query based on the filter criteria
            result = collection.find_one(filter_criteria)
            st.write("Query executed:", query_type, "with data:", query_data)
            st.write("Result", result)
            #st.write("Query executed:", query_data['query_type'], "Result:", result)
        elif query_type == "Find":
            # Execute the find query based on query_data
            collection_name = query_data['collection_name']
            print(collection_name)
            filter_criteria = query_data['filter']
            print(filter_criteria)
            result = collection.find(filter_criteria)
            print(result)
            # Convert the cursor to a list to get the actual documents
            documents = list(result)
            st.write("Query executed:", query_type, "with data:", query_data)
            st.write("Result")
            for document in result:
                st.write(document)
        elif query_type == "Count":
            # Execute the count query based on query_data
            #collection_name = query_data['collection_name']
            #filter_criteria = query_data['filter']
            result = collection.count_documents({})
            st.write("Query executed:", query_type, "with data:", query_data)
            st.write("Result", result)
    except Exception as e:
        st.sidebar.error("Invalid input! Provide JSON formatted data.")
        st.sidebar.error(str(e))

