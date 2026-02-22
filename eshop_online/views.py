from django.shortcuts import render


def home_page(request):
    context = {}
    return render(request, 'home_page.html', context)

def contact_us(request):
    context = {}
    return render(request, 'contact_us.html', context)
#Auth Section

#Auth Section