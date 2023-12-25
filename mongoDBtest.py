
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

## Initialize MongoDB           
uri = "mongodb+srv://myAtlasDBUser:myatlas-001@myatlasclusteredu.xliqzij.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['Music_Recomendation']
collection= db['user_songs_recomended']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

for db_name in client.list_database_names():
    print(db_name)

# Find the total count of documents in the collection
count = collection.count_documents({})

print(f"Total count in collection '{collection}': {count}")

result = collection.find({ "query_type": "find", "collection_name": "Music_Recomendatio.user_songs_recomended", "filter": { "popularity": { "$gte": 80 } }, "projection": { "song_name": 1, "artist_name": 1, "popularity": 1 } })

print(result)