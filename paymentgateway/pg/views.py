import json
import time
import requests
import razorpay
from requests.auth import HTTPBasicAuth
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.context_processors import csrf

# from .models import Orders
from django.http import HttpResponse


client = razorpay.Client(auth=("rzp_test_vZmsDFpMF5F89l", "zNdyT0tcE5lDFxh8u5fR9YTP")) #basic authentication , without auth , will never pass the gateway, between merchnact and razorpay



key_id ='rzp_test_vZmsDFpMF5F89l'
key_secret='zNdyT0tcE5lDFxh8u5fR9YTP'

# Create your views here.
def index(request):
    return render(request, 'pg/home.html')

def order(request):
    if request.method=='POST':
        name = request.POST.get('name','')
        address = request.POST.get('address','')
        email = request.POST.get('email','')
        contact = request.POST.get('contact','')
        amount = request.POST.get('amount','')
        order = Orders(name=name, address=address, email=email, contact=contact, amount=amount)
        #print(order.__dict__)
        amount_inr = int(amount)*100
        transfers= [
            {
                "account": "acc_G5mEbtU0rtEwnK",
                "amount": 1000,
                "currency": "INR",
                "notes": {
                    "branch": "Acme Corp Bangalore North",
                    "name": "Gaurav Kumar"
                },
                "linked_account_notes": [
                    "branch"
                ],
                "on_hold": 1,
                "on_hold_until": 1671222870
            }
        ]

        # context = RequestContext(request)
        # context_dict = {}
        # context_dict.update(csrf(request))
        # print(context_dict, "----00000-----")

        dict={'order_id':"1", 'adress':address} #15 key value pairs optional, if merchant wants to send anything additional

        #DATA={'amount':amount_inr, 'currency':'INR', 'receipt':order.order_id, 'payment_capture':'1', 'notes':dict}
        DATA = {'amount': amount_inr, 'currency': 'INR', 'receipt': order.order_id,'payment_capture':'1',
                'notes': dict, 'transfers':transfers}
        # DATA = {'amount': amount_inr, 'currency': 'INR', 'receipt': order.order_id, 'payment_capture': '1',
        #                'notes': dict}

        order_created= client.order.create(data=DATA) #dynamic order create

        print(order_created, type(order_created), "-----order created-----")
        global order_id_server, amount_paid
        order_id_server= order_created.get('id')
        #order_id_server = client.order.fetch('id')
        #order.save()
        print(order_id_server, "-----")
        amount_paid = int(order_created.get('amount')) /100
        para={ 'order_id' : order_created.get('id'),
        'amount': order_created.get('amount_due'),
        'currency': order_created.get('currency'),
        'key_id':key_id,
        'key_secret':key_secret}

    #return render(request, 'pg/callback.html', para, context_dict.get('csrf_token'))
    return render(request, 'pg/handlerfunc.html', para)
    #return render(request, 'pg/paymentpage.html', para)
    #return render(request, 'pg/manual_chcekout.html', para)


def payment(request):
    #payment notes, manual chcekout

    if request.method=='POST':
        payment_id = request.POST.get('razorpay_payment_id')
        print(payment_id, "-----")
        signature= request.POST.get('razorpay_signature')
        print(payment_id,order_id_server, signature, "-----")
        params_dict = {
            'razorpay_order_id': order_id_server, #server_side if order id not passed still payment will be done and it will fail in verification step
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        data = {'payment_id':'pay_G7nH5vQ10tl7S7'
                }

        transfers = client.transfer.all(data)
        print(transfers)
        print(dict(transfers), "--------------transfers dict--------")
        data={'payment_id':payment_id,
              'transfers': [
            {
                "account": "acc_G6Arrf7RMyX7Rf",
                "amount": 1000,
                "currency": "INR",
                "notes": {
                    "branch": "Acme Corp Bangalore North",
                    "name": "Gaurav Kumar"
                },
                "linked_account_notes": [
                    "branch"
                ],
                "on_hold": 1,
                "on_hold_until": 1671222870
            }

        ]}
        transfers= client.transfer.create(data)
        print("=====transfer===", transfers)

        verified= client.utility.verify_payment_signature(params_dict) #None
        print(verified, "----Verified---")
        user_details ={
            'order_id_server':order_id_server,
            'amount_paid':amount_paid,
            'payment_id':payment_id
        }

    return render(request, 'pg/done.html', user_details)

def manual(request):
    if request.is_ajax():
        message = "Yes, AJAX!"
    else:
        message = "Not Ajax"
    return HttpResponse(message)

def reverse(request):
    if request.method=='POST':
        payment_id = request.POST.get('payment_id')
        order_id = request.POST.get('order_id')
        data={'payment_id': payment_id}
        print(payment_id,"line 147")
        print(order_id)
        a=client.transfer.all(data)
        print(a,"line 150")
        for i in a['items']:
           if(i['source']==order_id):
               print(i['id'])
               trf_id=i['id']
               data1={'amount':1000}
               b=client.transfer.reverse(trf_id,data1)
               print(b)
               print("reversed")
        # data={"amount": 100,
        #    "reverse_all": 1}
        # a=client.transfer.reverse(payment_id, data)
        # print(a)
        return HttpResponse('<h1>found</h1>')

def create_plan(request):
    data = {
  "period": "weekly",
  "interval": 1,
  "item": {
    "name": "Test plan - Weekly",
    "amount": 69900,
    "currency": "INR",
    "description": "Description for the test plan"
  },
  "notes": {
    "notes_key_1": "Tea, Earl Grey, Hot",
    "notes_key_2": "Tea, Earl Grey… decaf."
  }
}
    create_plan = client.plan.create(data)
    print(create_plan, "plan--------")
    return(create_plan)

def subscription(request):
    #plan = create_plan(request)
    if request.method=='POST':
        name = request.POST.get('name','')
        address = request.POST.get('address','')
        email = request.POST.get('email','')
        contact = request.POST.get('contact','')
        amount = request.POST.get('amount','')
        Data={
                #"plan_id": plan.get('id'), #plan_id dynamic
                "plan_id":"plan_G8rXzSSCxJkf8a",
                "total_count": 6,
                "quantity": 1,
                "customer_notify": 1,
                "addons": [
                    {
                        "item": {
                            "name": "Registration-one time",
                            "amount": 10000,
                            "currency": "INR"
                        }
                    }
                ],
                "notes": {
                    "notes_key_1": "Tea, Earl Grey, Hot",
                    "notes_key_2": "Tea, Earl Grey… decaf."
                }
            }

        subscription_create = client.subscription.create(data=Data)
        print(subscription_create, "=====subscription====")
        para={'order_id' : subscription_create.get('id'),
        'plan_id': subscription_create.get('plan_id'),
        'key_id':key_id,
        'key_secret':key_secret}
        print(para, "para-----")
        return render(request, 'pg/handler_subscription.html', para)

def mandateLinkRegistration(request):
    if request.method=="POST":
        name=request.POST.get("aname")
        email=request.POST.get("aemail")
        phone=request.POST.get("acontact")
        acno=request.POST.get("acno")
        ifsc=request.POST.get("ifsc")
        type=request.POST.get("type")
        auth_type=request.POST.get("auth_type")
        #print(name,email,phone,acno,ifsc,type,auth_type)
        data={
            "customer": {
                "name": str(name),
                "email": str(email),
                "contact": str(phone)
            },
            "type": "link",
            "amount": 0,
            "currency": "INR",
            "description": "12 p.m. Meals",
            "subscription_registration": {
                "method": "emandate",
                "auth_type": str(auth_type),
                "expire_at": 1607936458,
                "max_amount": 90000,
                "bank_account": {
                    "beneficiary_name": str(name),
                    "account_number": str(acno),
                    "account_type": str(type),
                    "ifsc_code": str(ifsc)
                }
            },
            "receipt": "Receipt no. 102",
            "expire_by": 1607936458,
            "sms_notify": 1,
            "email_notify": 1,
            "notes": {
                "note_key 1": "Beam me up Scotty",
                "note_key 2": "Tea. Earl Gray. Hot."
            }
        }
        data_json=json.dumps(data)
        # print("------",json.dump(data))
        # reso=client.invoice.create(data)
        # print(reso)
        # urlr=reso['short_url']
        try:
            res=requests.post('https://api.razorpay.com/v1/subscription_registration/auth_links',auth=HTTPBasicAuth("rzp_test_FsRGzuburmgNQL","9pfZbqM2JRRHoNnfXzYVtOmo"),data=data_json)
            print(res.text)
            urlr=res.body["short_url"]
        except Exception as e:
            print(e)
        # try:
        #     res=requests.post('https://api.razorpay.com/v1/orders',auth=HTTPBasicAuth("rzp_test_FsRGzuburmgNQL","9pfZbqM2JRRHoNnfXzYVtOmo"),data={"amount":"1000","currency":"INR"})
        #     print(res.text)
        #     urlr=res.body["short_url"]
        # except Exception as e:
        #     print(e)
        print(urlr)
        return redirect(urlr)
def mandateregistrationorder(request):
    if request.method=="POST":
        client1 = razorpay.Client(auth=("rzp_test_FsRGzuburmgNQL", "9pfZbqM2JRRHoNnfXzYVtOmo"))
        name = request.POST.get("aname")
        email = request.POST.get("aemail")
        phone = request.POST.get("acontact")
        acno = request.POST.get("acno")
        ifsc = request.POST.get("ifsc")
        type = request.POST.get("type")
        auth_type = request.POST.get("auth_type")
        data={

                "amount": 0,
                "currency": "INR",
                "method": "emandate",
                "payment_capture": "1",
                "customer_id": "cust_GA61O4GncCbw99",
                "receipt": "Receipt No. 1",
                "notes": {
                    "notes_key_1": "Beam me up Scotty",
                    "notes_key_2": "Engage"
                },
                "token": {
                    "auth_type": auth_type,
                    "max_amount": 9999900,
                    "expire_at": 4102444799,
                    "notes": {
                        "notes_key_1": "Tea, Earl Grey, Hot",
                        "notes_key_2": "Tea, Earl Grey… decaf."
                    },
                    "bank_account": {
                        "beneficiary_name":name,
                        "account_number": acno,
                        "account_type": type,
                        "ifsc_code": ifsc
                    }
                }
            }
        order_created = client1.order.create(data=data)
        global order_id_server1
        order_id_server1 = order_created.get('id')
        print("-----------inside mandate order--------")
        print(order_created)
        para1 = {'order_id': order_id_server1}
        print("---para---- ")
        print(para1)
        return render(request, 'pg/handlerfunc.html', para1)

def recurpay(request):
    if request.method=="POST":
        payment_id=request.POST.get('payment_id')
        orders_data = {
            "amount": 200000,
            "currency": "INR",
            "payment_capture": "1",
            "receipt": "Receipt No. 1",
        }
        client1 = razorpay.Client(auth=("rzp_test_FsRGzuburmgNQL", "9pfZbqM2JRRHoNnfXzYVtOmo"))
        res1=client1.order.create(data=orders_data)
        print(payment_id)
        url="https://api.razorpay.com/v1/payments/{}".format(payment_id)
        print(url)
        res=requests.get(url,auth=HTTPBasicAuth("rzp_test_FsRGzuburmgNQL","9pfZbqM2JRRHoNnfXzYVtOmo"))
        response_dict = json.loads(res.text)
        print(response_dict['id'])
        token_id=response_dict['token_id']
        email=response_dict['email']
        contact=response_dict['contact']
        customer_id=response_dict['customer_id']
        print("Token details etc")
        print(token_id,email,contact,customer_id)
        recur_data = {
                "email": email,
                "contact": contact[3:],
                "amount": 200000,
                "currency": "INR",
                "order_id": res1.get("id"),
                "customer_id": customer_id,
                "token": token_id,
                "recurring": "1",
                "description": "Creating recurring payment for Gaurav Kumar",
                # "notes": {
                #     "note_key 1": "Beam me up Scotty",
                #     "note_key 2": "Tea. Earl Gray. Hot."
                # }
            }
        print(recur_data)
        recurpayres=requests.post('https://api.razorpay.com/v1/payments/create/recurring/',auth=HTTPBasicAuth("rzp_test_FsRGzuburmgNQL","9pfZbqM2JRRHoNnfXzYVtOmo"),data=recur_data)
        respon = json.loads(recurpayres.text)
        if(respon['razorpay_payment_id']):
            print("Done")
            print(respon['razorpay_payment_id'])
        else:
            print("Failed")

    return render(request,"pg/done.html")
