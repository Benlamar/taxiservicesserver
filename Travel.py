from datetime import datetime
from time import sleep
from Database import Database

class Travel:
    def __init__(self):
        self.taxi_col = Database("TaxisandCustomers", "taxis").getCollection()
        self.booking_col = Database("TaxisandCustomers", "booking").getCollection()
        self.customer_col = Database("TaxisandCustomers", "customers").getCollection()

    def deletePendingTaxi(self, pending_taxi):
        for taxi in pending_taxi:
            self.taxi_col.update_one({'id':taxi['taxi_id']}, {'$set':{'status':'Available'}})
            self.booking_col.delete_one({'taxi_id':taxi['taxi_id'], 'customer':taxi['customer']})
        return "Deleted"

    def updateLocation(self, taxi_id, customer,location):
        current_location = list(map(lambda x:x/100000,location))
        self.taxi_col.update_one({'id':taxi_id}, 
                    {'$set':{'timestamp':datetime.now(), 
                    'location':{'type':'Point','coordinates':current_location}}})
        
        self.customer_col.update_one({'name':customer}, 
                    {'$set':{'location':{'type':'Point','coordinates':current_location}}})

        self.booking_col.update_one({'customer':customer, 'taxi_id':taxi_id}, 
                    {'$set':{'source':{'type':'Point','coordinates':current_location}}})

        self.booking_col.update_one({'customer':customer, 'taxi_id':taxi_id}, 
                    {'$set':{'taxi_location':{'type':'Point','coordinates':current_location}}})
        return "Updating"


    def startTrip(self, booking_id):
        print(booking_id['booking_id'])
        book = list(self.booking_col.find({'booking_id':booking_id['booking_id'], 'status':'Accepted'}))
        data = book[0]
        data.pop('_id')
        
        start = list(map(lambda x:int(x*100000),data['source']['coordinates']))
        stop = list(map(lambda x:int(x*100000),data['destination']['coordinates']))
        
        while True:
            if start[0] > stop[0]:
                start[0] -= 1
            elif start[0] < stop[0]:
                start[0] += 1
            if start[1] > stop[1]:
                start[1] -= 1
            elif start[1] < stop[1]:
                start[1] += 1
            update_res = self.updateLocation(data['taxi_id'], data['customer'], start)
            print(update_res)
            if start[0] == stop[0] and start[1] == stop[1]:
                break
            print('travelling ... ')
            
        print("Done")
        self.customer_col.update_one({'name':data['customer']}, {'$set':{'status':'Available'}})
        self.taxi_col.update_one({'id':data['taxi_id']}, {'$set':{'status':'Available'}})
        self.booking_col.update_one({'booking_id':data['booking_id']}, {'$set':{'status':'Completed'}})
        print('Passed')
        return {'statusCode':200,'msg':"You have completed your journey"}

