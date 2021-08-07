from pymongo import MongoClient


class Database:

    def __init__(self):

        client = MongoClient("mongodb+srv://pipaelection.kmcel.mongodb.net/myFirstDatabase")

    
    def getElectionSchedule(company):
        companies.find_one_and_update(
            {"company" : company},
            {"$inc":
                {'actual_occup': 1}
            },upsert=False
        )
        updatedCompany = companies.find_one(
            {"company" : company},
        )
        return updatedCompany


    def clientOut(company):
        companies.find_one_and_update(
            {"company" : company},
            {"$inc":
                {'actual_occup': -1}
            },upsert=False
        )
        updatedCompany = companies.find_one(
            {"company" : company},
        )
        return updatedCompany

