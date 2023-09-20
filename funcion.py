
import pandas as pd
import requests
import googlemaps
from datetime import datetime


def localizar( data, lugares, API_KEY ):

    data[ 'distancia_km' ] = 0.0
    data[ 'direccion' ]    = ''

    for index, row in data.iterrows():
        
        per_lat = row[ 'latitud' ] 
        per_lng = row[ 'longitud' ]

        distancias  = []
        direcciones = []

        for lugar in lugares:
            
            lugar_endpoint = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            lugar_params   = {
                'location' : f'{ per_lat },{ per_lng }',
                'radius'   : 50000,
                'keyword'  : lugar,
                'key'      : API_KEY
            }

            response_lugar = requests.get( lugar_endpoint, params = lugar_params )
            data_lugar     = response_lugar.json()

            if 'results' in data_lugar:
                centros_localizados = data_lugar[ 'results' ]

                for centro in centros_localizados:
                    
                    centro_lat = centro[ 'geometry' ][ 'location' ][ 'lat' ]
                    centro_lng = centro[ 'geometry' ][ 'location' ][ 'lng' ]

                    centro_endpoint = 'https://maps.googleapis.com/maps/api/distancematrix/json'
                    centro_params   = {
                        'origins'      : f'{ per_lat },{ per_lng }',
                        'destinations' : f'{ centro_lat },{ centro_lng }',
                        'mode'         : 'driving',
                        'units'        : 'metric',
                        'key'          : API_KEY
                    }

                    response_centro = requests.get( centro_endpoint, params = centro_params )
                    data_centro     = response_centro.json()

                    if  'distance' in data_centro[ 'rows' ][ 0 ][ 'elements' ][ 0 ]:
                        
                        direccion = data_centro[ 'destination_addresses' ]                            
                        distancia = data_centro[ 'rows' ][ 0 ][ 'elements' ][ 0 ][ 'distance' ][ 'text' ]
                        distancia = float( distancia.split()[ 0 ] )
                        
                        direcciones.append( direccion )
                        distancias.append( distancia )
                        
        if distancias:

            distancia_min         = min( distancias )
            index_min             = distancias.index( distancia_min )
            direccion_mas_cercana = direcciones[ index_min ]

            data.at[ index, 'distancia_km' ] = distancia_min
            data.at[ index, 'direccion' ]    = direccion_mas_cercana
            
        else:
            
            data.at[ index, 'distancia_km' ] = None
            data.at[ index, 'direccion' ]    = None            

    return data