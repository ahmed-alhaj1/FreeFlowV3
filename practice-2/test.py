from models import User
from models import prepare_info
from driver import db


x = prepare_info('ahmedx', '123456', 'ahmed', 'alhaj1', 'alhaj1@umbc.edu')
db.create_all()
db.session.add(x)
db.session.commit()

user = User
for x in user.query.all():
	print(x.repr())

