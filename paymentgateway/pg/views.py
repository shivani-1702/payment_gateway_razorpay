import razorpay
from django.shortcuts import render
from .models import Orders
from django.http import HttpResponse


client = razorpay.Client(auth=("rzp_test_Vg4TId4a7WErvz", "eiTX74Hru52sMVOs2Bp5HPJo")) #basic authentication , without auth , will never pass the gateway, between merchnact and razorpay



key_id ='rzp_test_Vg4TId4a7WErvz'
key_secret='eiTX74Hru52sMVOs2Bp5HPJo'

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
        dict={'order_id':"1", 'adress':address} #15 key value pairs optional, if merchant wants to send anything additional

        #DATA={'amount':amount_inr, 'currency':'INR', 'receipt':order.order_id, 'payment_capture':'1', 'notes':dict}
        DATA = {'amount': amount_inr, 'currency': 'INR', 'receipt': order.order_id,'payment_capture':'0',
                'notes': dict}

        order_created= client.order.create(data=DATA)

        print(order_created, type(order_created), "order created-----")
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
            'razorpay_order_id': order_id_server, # server_side
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
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