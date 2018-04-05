import sys,os
import pprint
import pandas as pd
import optparse
import re
from fuzzywuzzy import fuzz, process
import pdb;

if __name__ == "__main__":
	ofp = sys.stdout
	mko = optparse.make_option
	usage = """Check the city slot\n%s --ocsv out.csv *""" % (sys.argv[0])
	cmdOptions = [
		mko('-i', '--icsv', metavar='IN_CSV', help='input'),
		mko('-o', '--ocsv', metavar='OUT_CSV', help='output'),
		mko('-p', '--population', metavar='POPULATION_CSV', help='population'),
		mko('-s', '--stopwords', metavar='STOP_WORDS', help='stop words'),
		mko('--config', default= None)
	]

	parser = optparse.OptionParser(option_list=cmdOptions, usage=usage)
	options, args = parser.parse_args(sys.argv[1:])

	# stop_words = [line.strip() for line in open(options.stopwords, 'r')]

	data = pd.read_csv(options.icsv)
	ofp.write('Before norm: number of rows %i, number of columns %i\n' % (len(data.index), len(data.columns)))

#################################################################################

#################################################################################


	#### location info -- need to get data and put them in the columns

	# load population csv
	pop = pd.read_csv(options.population, encoding = 'latin-1')
	#list of columns to drop from population csv
	dropColums = ["Geographic code", "Population, 2006", "2006 adjusted population flag",
					"Incompletely enumerated Indian reserves and Indian settlements, 2006",
					"Population, % change", "Private dwellings occupied by usual residents, 2011",
					]
	pop = pop.drop(dropColums, 1)

	#### normalize costs info  -- gunna need to readjust db table since no longer int
	data['PROVINCIAL DEPARTMENT PAYMENTS'] = data['PROVINCIAL DEPARTMENT PAYMENTS'].fillna('unknown')
	data['PROVINCIAL DFAA PAYMENTS'] = data['PROVINCIAL DFAA PAYMENTS'].fillna('unknown')
	data['ESTIMATED TOTAL COST'] = data['ESTIMATED TOTAL COST'].fillna('unknown')
	data['NORMALIZED TOTAL COST'] = data['NORMALIZED TOTAL COST'].fillna('unknown')
	data['MUNICIPAL COSTS'] = data['MUNICIPAL COSTS'].fillna('unknown')
	data['OGD COSTS'] = data['OGD COSTS'].fillna('unknown')
	data['INSURANCE PAYMENTS'] = data['INSURANCE PAYMENTS'].fillna('unknown')
	data['NGO PAYMENTS'] = data['NGO PAYMENTS'].fillna('unknown')
	data['FEDERAL DFAA PAYMENTS'] = data['FEDERAL DFAA PAYMENTS'].fillna('unknown')
	data['FATALITIES'] = data['FATALITIES'].fillna('unknown')
	# data['UTILITY PEOPLE AFFECTED'] = data['UTILITY PEOPLE AFFECTED'].fillna('unknown')
	# data['MAGNITUDE'] = data['MAGNITUDE'].fillna('unknown')
	data['INJURED / INFECTED'] = data['INJURED / INFECTED'].fillna('unknown')
	data['EVACUATED'] = data['EVACUATED'].fillna('unknown')

	#drop rows where still nan
	data = data.dropna(subset=['EVENT CATEGORY'])
	data = data.dropna(subset=['EVENT GROUP'])
	data = data.dropna(subset=['MAGNITUDE'])
	data = data.dropna(subset=['UTILITY - PEOPLE AFFECTED'])
	data = data.dropna(subset=['EVENT START DATE'])
	#to_drop= ['note', 'Note', '*Note', '*note','*Note:', 'Note:', '*note:', 'note:','request']
	#drop row that contains note in first column
	data = data[~data['EVENT CATEGORY'].str.contains('Note')]


	# extract province 
	pop['Province'] = pop['Geographic name'].str.extract('.*\((.*)\).*', expand = True)

	pop['Province'] = pop['Province'].str.replace('.', '').str.lower()
	pop['Geographic name'] = pop['Geographic name'].str.lower().str.replace(r"\(.*\)","")

	# rows to delete -- if they have division (maybe more?)
	pop = pop[~pop['Geographic name'].str.contains('division', na=False)]

	# write the clean population 
	pop.to_csv('cleanedPop.csv', encoding = 'latin-1')


############################################################################

###########################################################################

	# new disaster columns
	data['CITY']= ''
	data['PROVINCE']= ''
	data['COUNTRY']= ''
	data['ID'] = ''

	# regex for the provinces
	PROVINCES = {
		'AB': r'(( |^|[(])AB(,? |$|[)]))|(?i:ALBERTA)|(?i:PRAIRIE PROVINCES)',
		'BC': r'(( |^|[(])BC(,? |$|[)]))|(?i:BRITISH COLUMBIA)',
		'MB': r'(( |^|[(])MB(,? |$|[)]))|(?i:MANITOBA)|(?i:PRAIRIE PROVINCES)',
		'NB': r'(( |^|[(])NB(,? |$|[)]))|(?i:NEW BRUNSWICK)|(?i:MARITIME PROVINCES)',
		'NL': r'(( |^|[(])NL(,? |$|[)]))|(?i:NEWFOUNDLAND)|(?i:LABRADOR)',
		'NS': r'(( |^|[(])NS(,? |$|[)]))|(?i:NOVA SCOTIA)|(?i:MARITIME PROVINCES)',
		'NT': r'(( |^|[(])NT(,? |$|[)]))|(?i:NORTHWEST TERRITORIES)',
		'NU': r'(( |^|[(])NU(,? |$|[)]))|(?i:NUNAVUT)',
	    'ON': r'(( |^|[(])ON(,? |$|[)]))|(?i:ONTARIO)',
	    'PE': r'(( |^|[(])PE(,? |$|[)]))|(?i:PRINCE EDWARD ISLAND)|(?i:MARITIME PROVINCES)',
	    'QC': r'(( |^|[(])QC(,? |$|[)]))|(?i:QUEBEC)',
	    'SK': r'(( |^|[(])SK(,? |$|[)]))|(?i:SASKATCHEWAN)|(?i:PRAIRIE PROVINCES)',    
	    'YT': r'(( |^|[(])YT(,? |$|[)]))|(?i:YUKON)',                         
	}

	#regex for typical city data
	CITY = r'(?P<city>[a-zA-Z ]+)(?P<province> [A-Z]{2}(,? |$))'

	n= 0
	row = 0 
	trackOfRows = []
	#copy of data set for occurences skipped
	newData = data.copy()

	while(row < len(data.index)):
		# regex to get the multiple occurences of cities
		splits = re.split(" and |,", data['PLACE'].iloc[row])

		multipleRecords = []
		multipleProvinces = []
		if (not len(splits)==1):

			test = 1
			while( test < len(splits)):
				trackOfRows.append(row + test)
				test += 1

		for split in splits:
			searchCity = re.search(CITY, split)
			searchProvince = re.search(CITY, split)

			#check city 
			if( searchCity is not None): 
				city = searchCity.group("city")
				multipleRecords.append(city)
			else:
				multipleRecords.append("OTHER")

			# check province
			if( searchProvince is not None):
				province = searchProvince.group("province")	
				multipleProvinces.append(province)
			else: 
				multipleProvinces.append("OTHER")
			
			
		i = 0
		# create new rows
		for record in multipleRecords:
			data.loc[n] = data.iloc[row] #, ignore_index=False)
			data['PROVINCE'].iloc[n] = multipleProvinces[i]
			data['CITY'].iloc[n] = record
			data['ID'].iloc[n] = row
			if( data['PROVINCE'].iloc[n] == 'OTHER'):
				#if( data['PROVINCE'].iloc[n].str.contains('OTHER').any()):
				data['COUNTRY'].iloc[n] = 'OTHER'
			else:
				data['COUNTRY'].iloc[n] = "CA"
			n+=1
			i+=1

		row = row + len(multipleRecords) 
	
	trackOfRowsComplement =[]
	for rows in range(1100):
		if rows in trackOfRows:
			#print(rows)
			print("my rows")
		else:
			trackOfRowsComplement.append(rows)

	for row in trackOfRows:
		try:
			newData = newData.drop(data.index[trackOfRowsComplement])
			print(newData)
			dataNews = dataNews.append(newData.iloc[row])
			dataNewsto_csv('hello')
		except:
			break

	data = data.dropna(subset=['EVENT START DATE'])

############################################################################

#############################################################################

	## deleted code of attempt to do fuzzy match

	# number of citizens
	# citizens = pop['Population, 2011']

	# # all the poossible cities
	# # should concact with province
	# choices = pop['Geographic name'].tolist()
	# #df[df['A'].str.contains("hello")]
	# quebec = pop[pop['Province'].str.contains('que')==True]
	# quebec = quebec['Geographic name'].tolist()

	# bc = pop[pop['Province'].str.contains('bc')==True]
	# bc = bc['Geographic name'].tolist()
	# #print bc
	# provinces = pop['Geographic name'].tolist()
	
	#for index, row in data.iterrows():
	# for row in range(len(data.index)):	
	# 	if data['PLACE'].iloc[row].find('QC') > 0:
	# 		result = process.extractOne(data['PLACE'].iloc[row], quebec)
	# 	if data['PLACE'].iloc[row].find('BC') > 0:
	# 		result = process.extractOne(data['PLACE'].iloc[row], bc)
	# 	else:
	# 		result = process.extractOne(data['PLACE'].iloc[row], choices)

	# 	if result and result[1] > 70 :

	# 	#	set the row in data
	# 		data['CITY'].iloc[row] = result[0] 
	# 		provinceIndex = [choices.index(i) for i in choices if result[0] in i]
	# 		data['PROVINCE'].iloc[row] = provinces[provinceIndex[0]] 
	# 		data['COUNTRY'].iloc[row] = 'CA'
	# 		#print row, result
	# 	else:
	# 		data['COUNTRY'].iloc[row] = 'OTHER'
	# 		print row, result

############################################################################

#############################################################################

	#write the csv
	data.to_csv(options.ocsv)

	#log results
	ofp.write('After norm: number of rows %i, number of columns %i\n' % (len(data.index), len(data.columns)))
	ofp.close()



