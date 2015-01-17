CREATED = 0
CHARGED = 1

charges = db.charges

def charge(_id):
	update = {}

	#this would be where we charge the card if it worked
	#imagine some code

	update['status'] = CHARGED

	charges.update({'_id' : _id}, {'$set', update})

	return True

def create_charge(amount, buyer_id, seller_email, cl_id):
	charge = {}
	charge['_id'] = uuid.uuid4()
	charge['amount'] = amount
	charge['buyer_id'] = buyer_id
	charge['seller_email'] = seller_email
	charge['cl_id'] = cl_id
	charge['status'] = CREATED
	
	charges.insert(charge)

	return True

def set_charge_amount(_id, amount):
	update = {'amount' : amount}
	charges.update({'_id' : _id}, {'$set', update})

	return True