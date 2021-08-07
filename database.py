from pymongo import MongoClient


class Database:

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://pipa:pipa@pipaelection.kmcel.mongodb.net/PipaElection?retryWrites=true&w=majority")
        self.db = self.client["pipa-election"]
        self.schedule = self.db.elections
        self.votes = self.db.votes
        self.voters = self.db.voters

    def getSchedule(self, election):
        try:
            election_schedule = self.schedule.find_one(
                {"electionName": election},
            )
        except Exception as e:
            print(e)
        return election_schedule

    def insertVote(self, ballot, candidate):
        inserted_vote = None
        try:
            self.votes.insert_one(
                {"ballotId": ballot,
                 "candidateName": candidate}
            )
            inserted_vote = self.votes.find_one(
                {"ballotId": ballot},
            )
        except Exception as e:
            print(e)
        return inserted_vote

    def getVoter(self, user_id):
        try:
            voter = self.voters.find_one(
                {"userId": user_id},
            )
        except Exception as e:
            print(e)
        return voter


# dt = Database()
# dt.getSchedule('Election0')
# dt.insertVote('1000', 'Fofa')
# dt.getVoter('0')
