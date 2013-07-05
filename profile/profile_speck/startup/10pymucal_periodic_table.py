print "Loading Periodic Table: usage type Fe or other chemical symbol for information"
print "help(pymucal) or help(atomic_data) for more details"
for i in pymucal.atomic_data.atoms.keys():
	exec("%s=pymucal.atomic_data(i)"%(i))
