from api import API, HTTPConnector, Entity

connector = HTTPConnector("http://url/api/v0/key")
api = API(connector)

User = Entity("entity-code-1")
Review = Entity("entity-code-2")
Reviewer = Entity("entity-code-3")
Reviewee = Entity("entity-code-4")

session = api.session()
request1 = session.request("1.2.3.4", "mozilla", "/path/foo")
request1.log("User ? performing review ? on user ?",
             entities=(Reviewer(123), Review("abc"), Reviewee(234)),
             tags=["aaa", "bbb"],
             action="review")

## alternative call / idea
request1.log(builder("User ? performing review ? on user ?")
                    .entity(Reviewer(123))
                    .entity(Review("abc"))
                    .entity(Reviewer(234))
                    .tags("aaa", "bbb")
                    .action("review"))
request1.end()

Per entry (max) 1 action
een action heeft een onderwerp en optioneel leidend voorwerp.
User (onderwerp) Logs In (action)
User A (onderwerp) Reviews (action) User B (lv)

Optioneel aan action de positie van de onderwerp/lv entities meegeven?
log("User ? performing review ? on user ?", entities=(A, B), action=Review(0, 1))
vereist ActionInstance in model om relaties vast te leggen.


