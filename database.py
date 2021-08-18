import datetime
from pymongo import MongoClient
from datetime import timedelta

class Database:

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://pipa:pipa@pipaelection.kmcel.mongodb.net/PipaElection?retryWrites=true&w=majority")
        self.db = self.client["pipa-election"]
        self.schedule = self.db.elections
        self.votes = self.db.votes
        self.voters = self.db.voters
        self.candidates = self.db.candidates
        self.recount = self.db.recount
        self.votesRecount = self.db.votesRecount
        self.admins = self.db.admins
    
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    
    def getSchedule(self):
        try:
            election_schedule = self.schedule.find_one(
                {"realm_id": "123"},
            )
        except Exception as e:
            print(e)
        return election_schedule

    def electionTime(self):
        try:
            schedule = self.schedule.find_one(
                {"realm_id": "123"},
            )
            
            election_start = schedule['electionStart'] - timedelta(hours=3, minutes=0)
            election_finish = schedule['electionFinish'] - timedelta(hours=3, minutes=0)
            
            before = election_start > datetime.datetime.now()
            after = election_finish < datetime.datetime.now()

            return before, after
        except Exception as e:
            print(e)

    def insertVote(self, ballot, candidate, vote_type):
        inserted_vote = None
        try:
            self.votes.insert_one(
                {"ballotId": str(ballot),
                 "candidateName": candidate,
                 "type": str(vote_type)}
            )
            inserted_vote = self.votes.find_one(
                {"ballotId": ballot},
            )
        except Exception as e:
            print(e)
        return inserted_vote
    
    def setVoterStatus(self, voter, status):
        status_return = None
        try:
            self.voters.find_one_and_update(
                {"userId":voter}, {'$set':{"status":status}}
            )
            status_return = self.voters.find_one(
                {"userId":voter},
            )
        except Exception as e:
            print(e)
        return status_return
    

    def getVoter(self, user_id):
        try:
            voter = self.voters.find_one(
                {"userId": user_id},
            )
        except Exception as e:
            print(e)
        return voter

    def getVoters(self):
        try:
            countVoters = self.voters.find({'status': "pending"}).count()
        except Exception as e:
            print(e)
        return countVoters

    def getCandidates(self):
        candidates = None
        try:
            cl = list(self.candidates.find({}, {"name":1, "_id":0}))
            candidates = [d['name'] for d in cl]
        except Exception as e:
            print(e)
            
        return candidates

    def getVotes(self):
        return self.votes.count()

    def findBallotId(self,id):
        found = None
        try:
            found = self.votes.find_one({'ballotId':id})
        except Exception as e:
            print(e)
        return found

    def getRecountStatus(self):
        mode = None
        alreadyRecounted = None
        try:
            recount = self.recount.find_one({'realm_id':'123'})            
            if recount is not None:
                mode = recount["recountModeOn"]
                alreadyRecounted = recount["alreadyRecounted"]
        except Exception as e:
            print(e)
        return mode, alreadyRecounted  

    def finishRecount(self):
        recount_return = None
        try:
            self.recount.find_one_and_update({'realm_id':'123'},{'$set':{"recountModeOn":False,"alreadyRecounted":True}})

            recount_return = self.recount.find_one({'realm_id':'123'})   
        except Exception as e:
            print(e)
        return recount_return 

    def votesRecountEmpty(self):
        success = False
        try:
            self.votesRecount.remove({})
            success = True
        except Exception as e:
            print(e)
        return success

    def insertVoteRecount(self, ballot, candidate, vote_type):
        inserted_vote = None
        try:
            self.votesRecount.insert_one(
                {"ballotId": str(ballot),
                 "candidateName": candidate,
                 "type": str(vote_type)}
            )
            inserted_vote = self.votesRecount.find_one(
                {"ballotId": ballot},
            )
        except Exception as e:
            print(e)
        return inserted_vote

    def findRecountBallotId(self,id):
        found = None
        try:
            found = self.votesRecount.find_one({'ballotId':id})
        except Exception as e:
            print(e)
        return found


    def votesEmpty(self):
        success = False
        try:
            self.votes.remove({})
            success = True
        except Exception as e:
            print(e)
        return success
    
    def setVotersPending(self):
        success = False
        try:
            self.voters.update_many({},{'$set':{"status":"pending"}})
            success = True
        except Exception as e:
            print(e)
        return success

    def setAuthVotersAsPending(self):
        success = False
        try:
            self.voters.update_many({"status":"auth"},{'$set':{"status":"pending"}})
            success = True
        except Exception as e:
            print(e)
        return success

    def getAdmin(self,user_id):
        try:
            admin = self.admins.find_one(
                {"userId": user_id},
            )
        except Exception as e:
            print(e)
        return admin

#dt = Database()
# schedule = dt.getSchedule('Election0')
# schedule
# dt.electionTime('Election0')
# dt.insertVote('1000', 'Fofa')
# dt.getVoter('0')
