for i in pymucal.atomic_data.atoms.keys():
	exec("%s=pymucal.atomic_data(i)"%(i))
