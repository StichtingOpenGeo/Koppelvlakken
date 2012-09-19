#!/usr/bin/env python2

import codecs
import sys
from datetime import date, timedelta

charset = 'cp1252' # yes, this isn't what the documentation suggests

path = sys.argv[1] + '/'

def parse_date(day):
	return date(int(day[4:8]), int(day[2:4]), int(day[0:2]))

def parse_time(time):
	return time[0:2] + ':' + time[2:4] + ':00'

def open_iff(filename, delivery):
	l_content  = codecs.open(path + filename + '.dat', 'r', charset).read().split('\r\n')
	if l_content[0] == delivery:
		print "%s.dat matches delivery" % (filename)

	return l_content[1:-1]

def simple_list_writer(filename, arguments, data):
	f = codecs.open('/tmp/'+filename+'.tsv', 'w', 'UTF-8')
	f.write('\t'.join(arguments) + '\n')
	for y in data:
		f.write('\t'.join([unicode(y[z] or '') for z in arguments]) + '\n')
	f.close()

def simple_dict_writer(filename, arguments, data):
	f = codecs.open('/tmp/'+filename+'.tsv', 'w', 'UTF-8')
	f.write('\t'.join(arguments) + '\n')
	for x, y in data.items():
		f.write('\t'.join([unicode(x)] + [unicode(y[z] or '') for z in arguments[1:]]) + '\n')
	f.close()

def simple_dict_list_writer(filename, arguments, data):
	f = codecs.open('/tmp/'+filename+'.tsv', 'w', 'UTF-8')
	f.write('\t'.join(arguments) + '\n')
	for x, y in data.items():
		for u in y:
			f.write('\t'.join([unicode(x)] + [unicode(u[z] or '') for z in arguments[1:]]) + '\n')
	f.close()

def parse_timetables(delivery):
	l_timetables = open_iff('timetbls', delivery)

	timetables = {}
	current_id = None
	current_record = {}
	s_stationshort = None
	s_index = 0

	for x in l_timetables:
		if x[0] == '#':
			if current_id is not None:
				timetables[current_id] = current_record
			s_index = 0
			current_id = int(x[1:])
			current_record = {'service': [], 'validity': [], 'transport': [], 'attribute': [], 'stop': [], 'platform': []}
		elif x[0] == '%':
			s_companynumber, s_servicenumber, s_variant, s_firststop, s_laststop, s_servicename = x[1:].split(',')
			current_record['service'].append({'company': int(s_companynumber), 'service': int(s_servicenumber), 'variant': s_variant.strip(), 'first': int(s_firststop), 'last': int(s_laststop), 'name': s_servicename.strip()})
		elif x[0] == '-':
			v_footnote, v_firststop, v_laststop = x[1:].split(',')
			current_record['validity'].append({'footnote': int(v_footnote), 'first': int(v_firststop), 'last': int(v_laststop)})
		elif x[0] == '&':
			t_mode, t_firststop, t_laststop = x[1:].split(',')
			current_record['transport'].append({'mode': t_mode.strip(), 'first': int(t_firststop), 'last': int(t_laststop)})
		elif x[0] == '*':
			t_code, t_firststop, t_laststop, t_unknown = x[1:].split(',')
			current_record['attribute'].append({'code': t_code.strip(), 'first': int(t_firststop), 'last': int(t_laststop), 'unknown': int(t_unknown)})
		elif x[0] == '>':
			s_index += 1
			s_stationshort, s_departuretime = x[1:].split(',')
			s_stationshort = s_stationshort.strip()
			current_record['stop'].append({'station': s_stationshort, 'index': s_index, 'arrivaltime': None, 'departuretime': parse_time(s_departuretime)})
		elif x[0] == '.':
			s_index += 1
			s_stationshort, s_arrivaldeparturetime = x[1:].split(',')
			s_stationshort = s_stationshort.strip()
			both = parse_time(s_arrivaldeparturetime)
			current_record['stop'].append({'station': s_stationshort, 'index': s_index, 'arrivaltime': both, 'departuretime': both})
		elif x[0] == ';':
			s_index += 1
			s_stationshort = x[1:].split(',')
			s_stationshort = s_stationshort.strip()
			current_record['stop'].append({'station': s_stationshort, 'index': s_index, 'arrivaltime': None, 'departuretime': None})
		elif x[0] == '+':
			s_index += 1
			s_stationshort, s_arrivaltime, s_departuretime = x[1:].split(',')
			s_stationshort = s_stationshort.strip()
			current_record['stop'].append({'station': s_stationshort, 'index': s_index, 'arrivaltime': parse_time(s_arrivaltime), 'departuretime': parse_time(s_departuretime)})
		elif x[0] == '?':
			s_arrivalplatform, s_departureplatform, footnote = x[1:].split(',')
			current_record['platform'].append({'index': s_index,'station': s_stationshort,'arrival': s_arrivalplatform.strip(), 'departure': s_departureplatform.strip(), 'footnote': int(footnote)})
			if s_arrivalplatform[0] <> s_departureplatform[0]:
				print current_id, s_stationshort, x
		elif x[0] == '<':
			s_index += 1
			s_stationshort, s_arrivaltime = x[1:].split(',')
			s_stationshort = s_stationshort.strip()
			current_record['stop'].append({'station': s_stationshort, 'index': s_index, 'arrivaltime': parse_time(s_arrivaltime), 'departuretime': None})
	
	if current_id is not None:
		timetables[current_id] = current_record
	
	return timetables

def sql_timetables(data):
	f = {}
	a = {}
	f['service'] = codecs.open('/tmp/timetable_service.tsv', 'w', 'UTF-8')
	f['validity'] = codecs.open('/tmp/timetable_validity.tsv', 'w', 'UTF-8')
	f['transport'] = codecs.open('/tmp/timetable_transport.tsv', 'w', 'UTF-8')
	f['attribute'] = codecs.open('/tmp/timetable_attribute.tsv', 'w', 'UTF-8')
	f['stop'] = codecs.open('/tmp/timetable_stop.tsv', 'w', 'UTF-8')
	f['platform'] = codecs.open('/tmp/timetable_platform.tsv', 'w', 'UTF-8')

	a['service'] = ['company', 'service', 'variant', 'first', 'last', 'name']
	a['validity'] = ['footnote', 'first', 'last']
	a['transport'] = ['mode', 'first', 'last']
	a['attribute'] = ['code', 'first', 'last']
	a['stop'] = ['index', 'station', 'arrivaltime', 'departuretime']
	a['platform'] = ['index','station','arrival', 'departure', 'footnote']

	for x in f.keys():
		f[x].write('\t'.join(['serviceid'] + a[x]) + '\n')

	for x, y in data.items():
		for z in f.keys():
			for u in y[z]:
				f[z].write('\t'.join([unicode(x)] + [unicode(u[w] or '') for w in a[z]]) + '\n')
	
	for x in f.keys():
		f[x].close()

def parse_timezones(delivery):
	l_timezones = open_iff('timezone', delivery)

	timezones = {}
	current_id = None
	current_values = []

	for x in l_timezones:
		if x[0] == '#':
			if current_id is not None:
				timezones[current_id] = current_values
			current_id = int(x[1:])
			current_values = []
		else:
			difference, firstday, lastday = x[1:].split(',')
			if x[0] == '-':
				difference = int(difference) * -1
			elif x[0] == '+':
				difference = int(difference)

			current_values.append({'difference': difference, 'firstday': parse_date(firstday), 'lastday': parse_date(lastday)})
	
	if current_id is not None:
		timezones[current_id] = current_values

	return timezones

def sql_timezones(data):
	simple_dict_list_writer('timezone', ['tznumber', 'difference', 'firstday', 'lastday'], data)

def parse_transattributequestions(delivery):
	l_aq = open_iff('trnsaqst', delivery)

	aq = {}
	current_id = None
	current_record = {}

	for x in l_aq:
		if x[0] == '#':
			if current_id is not None:
				aq[current_id] = current_record
			q_code, q_type, q_question = x[1:].split(',')
			current_id = q_code.strip()
			current_record = {'attributes': [], 'inclusive': bool(q_type == '1'), 'question': q_question.strip()}
		elif x[0] == '-':
			current_record['attributes'].append(x[1:].strip())
	
	if current_id is not None:
		aq[current_id] = current_record

	return aq


def sql_transattributequestions(data):
	f = codecs.open('/tmp/trnsaqst.tsv', 'w', 'UTF-8')
	f.write('\t'.join(['code', 'inclusive', 'question', 'transattr']) + '\n')
	for x, y in data.items():
		for z in y['attributes']:
			f.write('\t'.join([unicode(u or '') for u in [x, y['inclusive'], y['question'], z]]) + '\n')
	f.close()

def parse_footnotes(delivery):
	l_footnotes = open_iff('footnote', delivery)

	footnotes = {}
	current_id = None

	for x in l_footnotes:
		if x[0] == '#':
			current_id = int(x[1:])
		else:
			footnotes[current_id] = [y == '1' for y in x]

	return footnotes

def sql_footnotes(delivery, data):
	f = codecs.open('/tmp/footnote.tsv', 'w', 'UTF-8')
	f.write('\t'.join(['footnote', 'servicedate']) + '\n')
	for x, y in data.items():
		for z in range(0, len(y)):
			if y[z] == True:
				f.write('\t'.join([unicode(x), unicode(delivery['firstday'] + timedelta(days=z))]) + '\n')
	f.close()

def parse_changes(delivery):
	l_changes = open_iff('changes', delivery)

	changes = {}
	current_id = None
	current_records = []

	for x in l_changes:
		if x[0] == '#':
			if current_id is not None:
				changes[current_id] = current_records
			current_id = x[1:].strip()
		else:
			c_from, c_to, c_change = [int(y) for y in x[1:].split(',')]
			current_records.append({'from': c_from, 'to': c_to, 'change': c_change})

	return changes

def sql_changes(data):
	simple_dict_list_writer('changes', ['station', 'from', 'to', 'change'], data)

def parse_countries(delivery):
	l_countries = open_iff('country', delivery)

	countries = {}
	for country in l_countries:
		c_code, c_inland, c_name = country.split(',')
		countries[c_code.strip()] = {'inland': bool(c_inland), 'name': c_name.strip()}

	return countries


def sql_countries(countries):
	simple_dict_writer('country', ['code', 'inland', 'name'], countries)

def parse_transattributes(delivery):
	l_transattributes = open_iff('trnsattr', delivery)

	transattributes = {}
	for attribute in l_transattributes:
		a_code, a_pcode, a_description = attribute.split(',')
		transattributes[a_code.strip()] = {'processingcode': int(a_pcode), 'description': a_description.strip()}

	return transattributes

def sql_transattributes(data):
	simple_dict_writer('trnsattr', ['code', 'processingcode', 'description'], data)

def parse_companies(delivery):
	l_companies = open_iff('company', delivery)

	companies = {}
	for company in l_companies:
		c_number, c_code, c_name, c_time = company.split(',')
		companies[int(c_number)] = {'code': c_code.strip(), 'name': c_name.strip(), 'timeturn': parse_time(c_time)}

	return companies

def sql_companies(data):
	simple_dict_writer('company', ['number', 'code', 'name', 'timeturn'], data)

def parse_connectionmodes(delivery):
	l_cms = open_iff('connmode', delivery)

	cms = {}
	for cm in l_cms:
		c_code, c_type, c_description = cm.split(',')
		cms[c_code.strip()] = {'type': int(c_type), 'description': c_description.strip()}

	return cms

def sql_connectionmodes(data):
	simple_dict_writer('connmode', ['code', 'type', 'description'], data)

def parse_continuousconnections(delivery):
	l_ccs = open_iff('contconn', delivery)

	ccs = []
	for cc in l_ccs:
		c_from, c_to, c_time, c_mode = cc.split(',')
		ccs.append({'from': c_from.strip(), 'to': c_to.strip(), 'time': int(c_time) * 60, 'mode': c_mode.strip()})

	return ccs

def sql_continuousconnections(data):
	simple_list_writer('contconn', ['from', 'to', 'time', 'mode'], data)


def parse_transmodes(delivery):
	l_transmode = open_iff('trnsmode', delivery)

	transmodes = {}
	for transmode in l_transmode:
		t_code, t_description = transmode.split(',')
		transmodes[t_code.strip()] = {'description': t_description.strip()}

	return transmodes

def sql_transmodes(data):
	simple_dict_writer('trnsmode', ['code', 'description'], data)

def parse_stations(delivery):
	l_stations = open_iff('stations', delivery)

	stations = {}
	for station in l_stations:
		changes, shortname, mintime, _maxtime, country, timezone, attribute, x, y, name = station.split(',')
		stations[shortname.strip()] = {'changes': int(changes), 'layovertime': int(mintime) * 60, 'country': country.strip(), 'timezone': int(timezone), 'x': int(x) * 10, 'y': int(y) * 10, 'name': name.strip()}

		# Multiply the RD coordinate by 10
		# Multiply the minimum transfer time by 60s
	
	return stations

def sql_stations(data):
	simple_dict_writer('station', ['shortname', 'changes', 'layovertime', 'country', 'timezone', 'x', 'y', 'name'], data)

def sql_delivery(delivery):
	f = codecs.open('/tmp/delivery.tsv', 'w', 'UTF-8')
	f.write('\t'.join(['companynumber', 'firstday', 'lastday', 'versionnumber', 'description']) + '\n')
	f.write('\t'.join([unicode(delivery[x] or '') for x in ['companynumber', 'firstday', 'lastday', 'versionnumber', 'description']]) + '\n')
	f.close()

def parse_delivery():
	delivery = codecs.open(path + 'delivery.dat', 'r', charset).read().split('\r\n')[0]
	number, firstday, lastday, versionnumber, description = delivery[1:].split(',')

	delivery = {'companynumber': int(number), 'firstday': parse_date(firstday), 'lastday': parse_date(lastday), 'versionnumber': int(versionnumber), 'description': description.strip()}

	countries = parse_countries(delivery)
	companies = parse_companies(delivery)
	transmodes = parse_transmodes(delivery)
	transattributes = parse_transattributes(delivery)
	timezones = parse_timezones(delivery)
	transattributequestions = parse_transattributequestions(delivery)
	footnotes = parse_footnotes(delivery)
	continuousconnections = parse_continuousconnections(delivery)
	connectionmodes = parse_connectionmodes(delivery)
	changes = parse_changes(delivery)
	timetables = parse_timetables(delivery)

	print "Received file from %s for period %s to %s (%s)" % (companies[delivery['companynumber']]['name'], delivery['firstday'], delivery['lastday'], delivery['description'])

	stations = parse_stations(delivery)

	#return {'delivery': delivery, 'companies': companies, 'countries': countries, 'transmodes': transmodes, 'transattributes': transattributes, 'timezones': timezones, 'transattributequestions': transattributequestions, 'footnotes': footnotes, 'continuousconnections': continuousconnections, 'connectionmodes': connectionmodes, 'changes': changes, 'timetables': timetables}

	sql_countries(countries)
	sql_timezones(timezones)
	sql_footnotes(delivery, footnotes)
	sql_stations(stations)
	sql_companies(companies)
	sql_delivery(delivery)
	sql_transattributequestions(transattributequestions)
	sql_transattributes(transattributes)
	sql_transmodes(transmodes)
	sql_continuousconnections(continuousconnections)
	sql_connectionmodes(connectionmodes)
	sql_changes(changes)
	sql_timetables(timetables)

parse_delivery()
