import urllib.request
import json
import datetime
import os

data = {}
token = os.environ.get('BCRA_TOKEN', '')

try:
    req = urllib.request.Request(
        'https://api.estadisticasbcra.com/uva',
        headers={'Authorization': 'BEARER ' + token}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        arr = json.loads(r.read())
        last = arr[-1]
        data['uva_hoy'] = last['v']
        data['uva_fecha'] = last['d']
        print('UVA:', last['v'], last['d'])
except Exception as e:
    print('UVA fallo:', str(e))
    data['uva_hoy'] = None
    data['uva_fecha'] = None

try:
    url = 'https://dolarapi.com/v1/dolares/oficial'
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
        data['oficial_compra'] = d['compra']
        data['oficial_venta'] = d['venta']
        data['oficial_fecha'] = str(datetime.date.today())
        print('Oficial:', d['compra'], '/', d['venta'])
except Exception as e:
    print('Oficial fallo:', str(e))
    data['oficial_compra'] = None
    data['oficial_venta'] = None
    data['oficial_fecha'] = None

data['rem'] = {'mar_26':3.4,'abr_26':3.1,'may_26':2.3,'jun_26':1.9,'jul_26':1.8}
data['updated_at'] = datetime.datetime.utcnow().isoformat() + 'Z'

f = open('data.json', 'w')
json.dump(data, f, indent=2)
f.close()
print('data.json OK')
