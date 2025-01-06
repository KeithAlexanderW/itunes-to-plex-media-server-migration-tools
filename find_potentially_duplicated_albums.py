import argparse
import os
import plexapi.audio
import plexapi.exceptions
import plexapi.library

from plexapi.server import PlexServer
from read_config import read_config

parser = argparse.ArgumentParser(description="Imports your iTunes track ratings into your Plex server.")
parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
args = parser.parse_args()
CONFIG = read_config(args.config)

plex_ip = CONFIG['plex']['ip']
plex_token = CONFIG['plex']['token']
lib_name = CONFIG['plex']['library']

plex_server = PlexServer(plex_ip, plex_token)

plex_lib = plex_server.library.section(lib_name)


class object_with_tracks:
    tracks: dict[str,plexapi.audio.Track] = dict() 


class object_with_albums:
    tracks: dict[str,str] = dict() 


def find_potentially_duplicated_albums():

    print()

    all_tracks: list[plexapi.audio.Track] = plex_lib.all( libtype = 'track' )
    #all_albums: list[plexapi.audio.Album] = plex_lib.all( libtype = 'album' )

    tracks_dict: dict[str,object_with_tracks] = dict()
    albums_dict: dict[str,object_with_albums] = dict()

    total_track_count = len( all_tracks )
    track_count = 0

    for track in all_tracks:

        track_count = track_count + 1

        if( track_count % 1000 == 0 ):
            print( f"Processed {track_count/total_track_count:.0%} of tracks..." )

        for track_location in track.locations: 

            track_guid = track.guid

            album_fullpath = os.path.dirname( track_location )
            album_key = track.parentKey
            album_guid = track.parentGuid

            # if track_key != '1-01 Fanfare For The Common Man.m4a':
            #     break

            if track_guid in tracks_dict:
                tracks_dict[track_guid].tracks[track.key] = track
            else:
                tracks: dict[str,plexapi.audio.Track] = dict()
                tracks[track.key] = track
                
                tracks_dict[track_guid] = object_with_tracks()
                tracks_dict[track_guid].tracks = tracks

            if album_guid in albums_dict:
                albums_dict[album_guid].albums[album_key] = album_fullpath
            else:
                albums: dict[str,plexapi.audio.album] = dict()
                albums[album_key] = album_fullpath
                
                albums_dict[album_guid] = object_with_albums()
                albums_dict[album_guid].albums = albums      
    
    print()
    print()

    potential_duplicate_uniques = 0
    potential_duplicates = 0

    # track_object: object_with_tracks
    # for track_guid, track_object in tracks_dict.items():
        
    #     if len( track_object.tracks ) > 1:

    #         potential_duplicate_uniques = potential_duplicate_uniques + 1
    #         print( f"{len( track_object.tracks )} track(s) in \"{track_guid}\" " ) 

    #         track: plexapi.audio.Track
    #         for track_key, track in track_object.tracks.items():
    #             potential_duplicates = potential_duplicates + 1
    #             print( f"  {track_key} {track.locations}")

    album_object: object_with_albums
    for album_guid, album_object in albums_dict.items():
        
        if len( album_object.albums ) > 1:

            potential_duplicate_uniques = potential_duplicate_uniques + 1
            print( f"{len( album_object.albums )} album(s) in \"{album_guid}\" " ) 

            album: plexapi.audio.album
            for album_key, album_fullpath in album_object.albums.items():
                potential_duplicates = potential_duplicates + 1
                print( f"  {album_key} {album_fullpath}")

    print()
    print( f"Potential Duplicates (unique): {potential_duplicate_uniques}" )
    print( f"Potential Duplicates: {potential_duplicates}" )
    print( f"Potential Duplicates (average): {potential_duplicates/potential_duplicate_uniques}")
    print()


if __name__ == '__main__':
    find_potentially_duplicated_albums()

