import urllib.request
import json
import datetime
import os

data = {}
token = os.environ.get('BCRA_TOKEN', '')

# UVA desde argentinadatos.com (publica, sin token, sin SSL issues)
try:
    url = 'https://api.argentinadatos.com/v1/finanzas/indices/uva'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        arr = json.loads(r.read())
        # devuelve [{fecha, valor}], tomamos el ultimo
        ultimo = arr[-1]
        data['uva_hoy'] = ultimo['valor']
        data['uva_fecha'] = ultimo['fecha']
        print('UVA argentinadatos:', data['uva_hoy'], data['uva_fecha'])
except Exception as e:
    print('UVA argentinadatos fallo:', str(e))
    # Fallback: estadisticasbcra con token, filtramos solo datos >= 2026
    try:
        req2 = urllib.request.Request(
            'https://api.estadisticasbcra.com/uva',
            headers={'Authorization': 'BEARER ' + token}
        )
        with urllib.request.urlopen(req2, timeout=15) as r:
            arr = json.loads(r.read())
            recientes = [x for x in arr if x.get('d', '') >= '2026-01-01']
            if not recientes:
                recientes = [x for x in arr if x.get('d', '') >= '2025-01-01']
            ultimo = recientes[-1] if recientes else arr[-1]
            data['uva_hoy'] = ultimo['v']
            data['uva_fecha'] = ultimo['d']
            print('UVA fallback BCRA:', data['uva_hoy'], data['uva_fecha'])
    except Exception as e2:
        print('UVA fallback fallo:', str(e2))
        data['uva_hoy'] = None
        data['uva_fecha'] = None

# Dolar oficial desde argentinadatos.com
try:
    url2 = 'https://api.argentinadatos.com/v1/cotizaciones/dolares/oficial'
    req3 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req3, timeout=15) as r:
        arr = json.loads(r.read())
        # devuelve [{fecha, compra, venta}]
        ultimo = arr[-1]
        data['oficial_compra'] = ultimo.get('compra')
        data['oficial_venta'] = ultimo.get('venta')
        data['oficial_fecha'] = ultimo.get('fecha')
        print('USD oficial argentinadatos:', data['oficial_venta'], data['oficial_fecha'])
except Exception as e:
    print('USD argentinadatos fallo:', str(e))
    # Fallback: estadisticasbcra
    try:
        req4 = urllib.request.Request(
            'https://api.estadisticasbcra.com/usd_of',
            headers={'Authorization': 'BEARER ' + token}
        )
        with urllib.request.urlopen(req4, timeout=15) as r:
            arr = json.loads(r.read())
            recientes = [x for x in arr if x.get('d', '') >= '2026-01-01']
            ultimo = recientes[-1] if recientes else arr[-1]
            data['oficial_venta'] = ultimo['v']
            data['oficial_compra'] = round(ultimo['v'] * 0.985, 2)
            data['oficial_fecha'] = ultimo['d']
            print('USD fallback BCRA:', data['oficial_venta'])
    except Exception as e2:
        print('USD fallback fallo:', str(e2))
        data['oficial_compra'] = None
        data['oficial_venta'] = None
        data['oficial_fecha'] = None

data['rem'] = {'mar_26':3.4,'abr_26':3.1,'may_26':2.3,'jun_26':1.9,'jul_26':1.8}
data['updated_at'] = datetime.datetime.utcnow().isoformat() + 'Z'

f = open('data.json', 'w')
json.dump(data, f, indent=2)
f.close()
print('DONE - UVA:', data['uva_hoy'], '| USD:', data['oficial_venta'])
