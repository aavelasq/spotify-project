import pandas as pd
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

client_id = "secret" 
client_secret = "also a secret" 

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def genre_check(uri):
    '''
    checks if the genres of the artist contains k-pop in it
    '''
    for genre in sp.artist(uri)['genres']:
        if 'k-pop' in genre: 
            return True
    
    return False

def artist_uris(playlists):
    '''
    gets the uris of all artists within a playlist
    '''
    artists_list = []
    
    for pl_id in playlists: 
        pl = sp.user_playlist_tracks(
            user='spotify:user:spotify', playlist_id=pl_id)['items']
        pl_len = len(pl)

        for x in range(pl_len):
            artist = pl[x]['track']['artists'][0]['uri']
            if artist not in artists_list and genre_check(artist) == True:
                artists_list.append(artist)
        
    return artists_list

def apply_af(df):
    '''
    gets the audio features of all tracks
    '''
    af = sp.audio_features(df['uri'])
    af_df = pd.DataFrame(af)
    af_df = af_df.drop(columns=['id', 'uri', 'track_href', 'analysis_url', 'type'])
    
    return af_df

def playlist_df(artists):
    '''
    given a list of artist uris, returns a dataframe of all the top tracks of that artist,
    excludes any track in which the artist is NOT listed as the main artist of the track 
    '''
    dfs = []
    
    for artist in artists:
        art_name = sp.artist(artist)['name']
        df = pd.DataFrame(sp.artist_top_tracks(artist)['tracks'])
        
        # ensures artist appears only in results
        df['artists'] = df['artists'].apply(lambda x: x[0]['name'])
        result = df[df['artists'] == art_name].copy()
        result['artist_uri'] = artist
        
        dfs.append(result)
        
    combined = dfs[0].append(dfs[1:]).reset_index().drop(columns='index')

    # gets audio features for all tracks
    af = apply_af(combined)
    result = pd.concat([combined, af], axis=1)
    
    return result
    