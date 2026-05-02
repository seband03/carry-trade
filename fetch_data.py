import urllib.request
import json
import datetime
import os

data = {}
token = os.environ.get('BCRA_TOKEN', '')
today = str(datetime.date.today())
yesterday = str(datetime.date.today() - datetime.timedelta(days=3))

try:
    url = 'https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/uva?desde=' + yesterday + '&hasta=' + today + '&limit=5'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())
        resultados = resp.get('results', [])
        if not resultados:
            raise Exception('sin resultados UVA')
        ultimo = resultados[-1]
        data['uva_hoy'] = ultimo.get('valor', ultimo.get('value'))
        data['uva_fecha'] = ultimo.get('fecha', ultimo.get('date'))
        print('UVA:', data['uva_hoy'], data['uva_fecha'])
except Exception as e:
    print('UVA BCRA publica fallo:', str(e))
    try:
        req2 = urllib.request.Request(
            'https://api.estadisticasbcra.com/uva',
            headers={'Authorization': 'BEARER ' + token}
        )
        with urllib.request.urlopen(req2, timeout=15) as r:
            arr = json.loads(r.read())
            recientes = [x for x in arr if x.get('d', '') >= '2025-01-01']
            ultimo = recientes[-1] if recientes else arr[-1]
            data['uva_hoy'] = ultimo['v']
            data['uva_fecha'] = ultimo['d']
            print('UVA fallback:', data['uva_hoy'], data['uva_fecha'])
    except Exception as e2:
        print('UVA fallback fallo:', str(e2))
        data['uva_hoy'] = None
        data['uva_fecha'] = None

try:
    req3 = urllib.request.Request(
        'https://api.estadisticasbcra.com/usd_of',
        headers={'Authorization': 'BEARER ' + token}
    )
    with urllib.request.urlopen(req3, timeout=15) as r:
        arr = json.loads(r.read())
        recientes = [x for x in arr if x.get('d', '') >= '2026-01-01']
        ultimo = recientes[-1] if recientes else arr[-1]
        data['oficial_venta'] = ultimo['v']
        data['oficial_compra'] = round(ultimo['v'] * 0.985, 2)
        data['oficial_fecha'] = ultimo['d']
        print('USD oficial:', data['oficial_venta'], data['oficial_fecha'])
except Exception as e:
    print('USD oficial fallo:', str(e))
    data['oficial_compra'] = None
    data['oficial_venta'] = None
    data['oficial_fecha'] = None

data['rem'] = {'mar_26':3.4,'abr_26':3.1,'may_26':2.3,'jun_26':1.9,'jul_26':1.8}
data['updated_at'] = datetime.datetime.utcnow().isoformat() + 'Z'

f = open('data.json', 'w')
json.dump(data, f, indent=2)
f.close()
print('OK:', data['uva_hoy'], data['oficial_venta'])
