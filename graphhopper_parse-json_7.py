import urllib.parse
import requests

# URL base para routing y API Key de Graphhopper
route_url = "https://graphhopper.com/api/1/route?"
key = "82404574-fc07-481b-9fd0-655d9ad59822"  # token


def geocoding(location, key):
    while location == "":
        location = input("Ingrese la ubicación nuevamente: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode(
        {"q": location, "limit": "1", "key": key, "locale": "es"}
    )

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if len(state) != 0 and len(country) != 0:
            new_loc = f"{name}, {state}, {country}"
        elif len(country) != 0:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(
            f"URL de Geocoding API para {new_loc} (Tipo de ubicación: {value}):\n{url}"
        )
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            msg = json_data.get("message", "No se proporcionó mensaje de error")
            print(f"Estado de Geocode API: {json_status}\nMensaje de error: {msg}")

    return json_status, lat, lng, new_loc


while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículos disponibles en Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car (auto), bike (bicicleta), foot (a pie)")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    vehicle = input("Ingrese un perfil de vehículo de la lista anterior (o 's' / 'salir'): ").strip().lower()

    if vehicle in ["s", "salir", "quit", "q"]:
        print("Saliendo del programa...")
        break

    profile = ["car", "bike", "foot"]
    if vehicle not in profile:
        vehicle = "car"
        print("No se ingresó un perfil válido. Usando el perfil 'car' por defecto.")

    loc1 = input("Ubicación de origen (o 's' / 'salir'): ").strip()
    if loc1.lower() in ["s", "salir", "quit", "q"]:
        print("Saliendo del programa...")
        break
    orig = geocoding(loc1, key)

    loc2 = input("Ubicación de destino (o 's' / 'salir'): ").strip()
    if loc2.lower() in ["s", "salir", "quit", "q"]:
        print("Saliendo del programa...")
        break
    dest = geocoding(loc2, key)

    print("=================================================")

    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"

        paths_url = (
            route_url
            + urllib.parse.urlencode({"key": key, "vehicle": vehicle, "locale": "es"})
            + op
            + dp
        )
        
        paths_response = requests.get(paths_url)
        paths_status = paths_response.status_code
        paths_data = paths_response.json()

        print(f"Estado de Routing API: {paths_status}\nURL de Routing API:\n{paths_url}")
        print("=================================================")
        print(f"Indicaciones desde {orig[3]} hasta {dest[3]} mediante {vehicle}")
        print("=================================================")

        if paths_status == 200:
            distance_m = paths_data["paths"][0]["distance"]
            km = distance_m / 1000
            miles = km / 1.60934

            time_ms = paths_data["paths"][0]["time"]
            sec = int(time_ms / 1000 % 60)
            min = int(time_ms / 1000 / 60 % 60)
            hr = int(time_ms / 1000 / 60 / 60)

            print(f"Distancia recorrida: {km:.2f} km / {miles:.2f} millas")
            print(f"Duración del viaje: {hr:02d}:{min:02d}:{sec:02d}")
            print("=================================================")

            print("Narrativa del viaje paso a paso:")
            for step in paths_data["paths"][0]["instructions"]:
                path_text = step["text"]
                step_dist_m = step["distance"]
                step_km = step_dist_m / 1000
                step_miles = step_km / 1.60934
                print(f"- {path_text} ({step_km:.2f} km / {step_miles:.2f} millas)")
            
            print("=================================================")
        else:
            msg = paths_data.get("message", "Error de enrutamiento desconocido")
            print(f"Mensaje de error: {msg}")
            print("*************************************************")