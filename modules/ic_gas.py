import exceptions
from pymucal import muro,atomic_data
import math
__icgases=["He","N2","Ne","Ar","Kr"]
#I miss data for Kr, I use that of Ar
__w_gases={"He":32.5,"N":35.8,"Ne":35.8,"Ar":27,"Kr":27}
#R=8.314472 kg m^2 / K mol s^2
#R=8.314472e7 g cm^2 /K mol s^2
__gas_constant=8.314472e7
#To set the pressure from mbar to cgi
__mbar_conv=1.e3

def ic_abs(energy=9000.,gas1="N2",p1=100.,gas2="He",p2=None,l=30.,T=294.,):
	"""Returns the absorption 1-exp(-mux) of the chamber of given lenght. 
	Pressures are in mbars, lenght in cm, energy in eV, temperature in K.
	Default total pressure=2000 mbar, default length is 30 cm"""
	if p2==None:
		p2=2000.-p1
	return 1.-math.exp(-(gas_mux(energy,gas1,p1,T,l)+gas_mux(energy,gas2,p2,T,l)))

def gas_mux(energy,gas,pressure,temperature=294.,l=1.):
	polyatomic=1
	if gas in __icgases:
		if gas=="N2":
			polyatomic=2
			gas="N"
		gab=muro(gas,energy)*polyatomic
		gdata=atomic_data(gas)
	else:
		raise exceptions.Exception("Unknown Chamber Gas")
	return gab*pressure*__mbar_conv/(__gas_constant*temperature)*gdata.weight*l

def xbpm_abs(energy=9000.,gas1="N2",p1=100.,gas2="He",p2=None,l=10.,T=294.,):
	"""Returns the absorption 1-exp(-mux) of the chamber of given lenght. 
	Pressures are in mbars, lenght in cm, energy in eV, temperature in K.
	Default total pressure=1000 mbar, default length is 10 cm"""
	if p2==None:
		p2=1000.-p1
	return 1.-math.exp(-(gas_mux(energy,gas1,p1,T,l)+gas_mux(energy,gas2,p2,T,l)))


def flux(energy,gas,pressure,gain,cps,l=30):
	"""Calcul le flux en ph/s mesure dans une chambre a ionisation de longueur l (cm) avec gaz et pression donns"""
	return (cps*1e-5/gain/1.6e-19)*32./energy/(ic_abs(energy,gas,pressure,l=l))
