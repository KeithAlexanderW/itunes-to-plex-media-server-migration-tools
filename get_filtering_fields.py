import argparse

from plexapi.server import PlexServer
from read_config import read_config

parser = argparse.ArgumentParser(description="Imports your iTunes track ratings into your Plex server.")
parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
args = parser.parse_args()
CONFIG = read_config(args.config)

# log_file = 'last_run.log'
plex_ip = CONFIG['plex']['ip']
plex_token = CONFIG['plex']['token']
lib_name = CONFIG['plex']['library']

plex_server = PlexServer(plex_ip, plex_token)

plex_lib = plex_server.library.section(lib_name)


def get_artist_filtering_fields():

    fields = plex_lib.listFields( libtype = 'artist' )

    print( "\nArtist Filtering Fields:\n" )

    for field in fields:
        print( field )
    
    print( "\n" )


def get_album_filtering_fields():

    fields = plex_lib.listFields( libtype = 'album' )

    print( "\nAlbum Filtering Fields:\n" )

    for field in fields:
        print( field )

    print( "\n" )


def get_track_filtering_fields():

    fields = plex_lib.listFields( libtype = 'track' )

    print( "\nTrack Filtering Fields:\n" )

    for field in fields:
        print( field )

    # operators = plex_lib.listOperators( libtype = 'track' )

    # print( "Filtering Operators\n" )

    # for operator in operators:
    #     print( operator )

    # filter_choices = plex_lib.listFilterChoices( libtype = 'track' )

    # print( "Filter Choices\n" )

    # for filter_choice in filter_choices:
    #     print( filter_choice )    
    
    print( "\n" )


if __name__ == '__main__':
    get_artist_filtering_fields()
    get_album_filtering_fields()
    get_track_filtering_fields()
