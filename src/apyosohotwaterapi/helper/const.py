# HTTP return codes.
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_MOVED_PERMANENTLY = 301
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503

OSOTOHA = {
    "Hotwater": {
        "HeaterState": { "on": "ON", "off": "OFF" },
        "DeviceConstants": { "minTemp": 10, "maxTemp": 80 },
        "HeaterConnection": { None: False, "Connected": True },
        "HeaterMode": { None: "Off", "auto": "Auto","manual": "Manual","off": "Off", "Legionella": "Legionella","PowerSave": "PowerSave", "ExtraEnergy": "ExtraEnergy", "Voltage": "Voltage" },
        "HeaterOptimizationMode": { None: "Off" },
        "HeaterSubOptimizationMode": { None: None }
    }
}