from django.shortcuts import render
from datetime import datetime
import os
import requests

def index(request):
	return render(request, "tmc/index.html", {})

def tmc(request):
	due_date = request.GET['due_date']
	query_date = request.GET['query_date']
	amount = float(request.GET['amount'])
	time = datetime.strptime(query_date, '%Y-%m-%d') - datetime.strptime(due_date, '%Y-%m-%d')
	
	total_tmc = 1
	tmcs = sbif_tmcs(request)
	for tmc in tmcs:
		tmc_factor = (100+float(tmc["Valor"]))/100
		print(tmc_factor)
		total_tmc = total_tmc * tmc_factor

	debt =  "%.2f" % (amount * total_tmc)

	args = {
		"due_date": due_date,
		"query_date": query_date,
		"amount": amount,
		"days": time.days,
		"debt": debt,
		"total_tmc": "%.2f" % (total_tmc),
	}

	return render(request, "tmc/tmc.html", args)

def sbif_tmcs(request): 
	# Consume la API de TMC, arregla el formato, asumiendo que son tipo 41 o 42
	# Retorna un listado con todos los TMCs
	### 41: Operaciones expresadas en moneda extranjera Inferiores o iguales al equivalente de 2.000 unidades de fomento
	### 42: Operaciones expresadas en moneda extranjera Superiores al equivalente de 2.000 unidades de fomento

	# Build params
	api_key = os.environ.get('SBIF_API_KEY')
	due_date = request.GET['due_date']
	query_date = request.GET['query_date']
	date_range_param = f"{due_date[0:4]}/{due_date[5:7]}/{query_date[0:4]}/{query_date[5:7]}/" 

	# Get api request
	url = f"https://api.sbif.cl/api-sbifv3/recursos_api/tmc/periodo/{date_range_param}?apikey={api_key}&formato=json" 
	r = requests.get(url).json()

	# Format response into tmc array
	tmcs = r["TMCs"]
	tipo_tmc = "41" if float(request.GET["amount"]) <= 2000 else "42"
	tmcs = [n for n in tmcs if n["Tipo"] == tipo_tmc]

	return tmcs
