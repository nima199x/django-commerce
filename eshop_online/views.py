from django.shortcuts import render


def home_page(request):
    context = {}
    return render(request, 'home_page.html', context)


#Auth Section

#Auth Section