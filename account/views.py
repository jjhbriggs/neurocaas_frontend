from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import View

# Create your views here.


class AccountDetailView(View):
    model = get_user_model()
    template_name = "account/account_detail.html"

    def get(self, request):
        return render(request, template_name=self.template_name, context={"user": request.user})
