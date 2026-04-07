from django.shortcuts import render

STOCK_OPTIONS = ['ABEV3.SA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA', 'MGLU3.SA', 'GGBR4.SA', 'WEGE3.SA', 'LREN3.SA']

def index(request):
    context = {
        'stock_options': STOCK_OPTIONS
    }
    return render(request, "index.html", context)