print "Loading Periodic Table: usage type help(Fe) or other chemical symbol for information"
for i in pymucal.atomic_data.atoms.keys():
	exec("%s=pymucal.atomic_data(i)"%(i))
