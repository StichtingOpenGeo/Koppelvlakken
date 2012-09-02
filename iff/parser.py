#!/usr/bin/env python2

import codecs
import sys
from datetime import date

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

def parse_timetables(delivery):
	l_timetables = open_iff('timetbls', delivery)

	timetables = {}
	current_id = None
	current_record = {}
	s_stationshort = None

	for x in l_timetables:
		if x[0] == '#':
			if current_id is not None:
				timetables[current_id] = current_record
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
			current_record['transport'].append({'mode': t_mode.strip(), 'first': int(v_firststop), 'last': int(v_laststop)})
		elif x[0] == '*':
			t_code, t_firststop, t_laststop, t_unknown = x[1:].split(',')
			current_record['attribute'].append({'code': t_code.strip(), 'first': int(t_firststop), 'last': int(t_laststop), 'unknown': int(t_unknown)})
		elif x[0] == '>':
			s_stationshort, s_departuretime = x[1:].split(',')
			current_record['stop'].append({'station': s_stationshort, 'arrivaltime': None, 'departuretime': parse_time(s_departuretime)})
		elif x[0] == '.':
			s_stationshort, s_arrivaldeparturetime = x[1:].split(',')
			both = parse_time(s_departuretime)
			current_record['stop'].append({'station': s_stationshort, 'arrivaltime': both, 'departuretime': both})
		elif x[0] == ';':
			s_stationshort = x[1:].split(',')
			current_record['stop'].append({'station': s_stationshort, 'arrivaltime': None, 'departuretime': None})
		elif x[0] == '+':
			s_stationshort, s_arrivaltime, s_departuretime = x[1:].split(',')
			current_record['stop'].append({'station': s_stationshort, 'arrivaltime': parse_time(s_arrivaltime), 'departuretime': parse_time(s_departuretime)})
		elif x[0] == '?':
			s_arrivalplatform, s_departureplatform, footnote = x[1:].split(',')
			current_record['platform'].append({'station': s_stationshort, 'arrival': s_arrivalplatform, 'departure': s_departureplatform, 'footnote': int(footnote)})
			if s_arrivalplatform[0] <> s_departureplatform[0]:
				print current_id, s_stationshort, x
		elif x[0] == '<':
			s_stationshort, s_arrivaltime = x[1:].split(',')
			current_record['stop'].append({'station': s_stationshort, 'arrivaltime': parse_time(s_arrivaltime), 'departuretime': None})
	
	if current_id is not None:
		timetables[current_id] = current_record
	
	return timetables

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
			current_record = {'attributes': [], 'type': bool(q_type == '1'), 'question': q_question.strip()}
		elif x[0] == '-':
			current_record['attributes'].append(x[1:].strip())
	
	if current_id is not None:
		aq[current_id] = current_record

	return aq

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

def parse_countries(delivery):
	l_countries = open_iff('country', delivery)

	countries = {}
	for country in l_countries:
		c_code, c_inland, c_name = country.split(',')
		countries[c_code.strip()] = {'inland': bool(c_inland), 'name': c_name.strip()}

	return countries

def parse_transattributes(delivery):
	l_transattributes = open_iff('trnsattr', delivery)

	transattributes = {}
	for attribute in l_transattributes:
		a_code, a_pcode, a_description = attribute.split(',')
		transattributes[a_code.strip()] = {'processing': int(a_pcode), 'description': a_description.strip()}

	return transattributes

def parse_companies(delivery):
	l_companies = open_iff('company', delivery)

	companies = {}
	for company in l_companies:
		c_number, c_code, c_name, c_time = company.split(',')
		companies[int(c_number)] = {'code': c_code.strip(), 'name': c_name.strip(), 'time': int(c_time)}

	return companies

def parse_connectionmodes(delivery):
	l_cms = open_iff('connmode', delivery)

	cms = {}
	for cm in l_cms:
		c_code, c_type, c_description = cm.split(',')
		cms[c_code.strip()] = {'type': int(c_type), 'description': c_description.strip()}

	return cms

def parse_continuousconnections(delivery):
	l_ccs = open_iff('contconn', delivery)

	ccs = []
	for cc in l_ccs:
		c_from, c_to, c_time, c_mode = cc.split(',')
		ccs.append({'from': c_from.strip(), 'to': c_to.strip(), 'time': int(c_time) * 60, 'mode': c_mode.strip()})

	return ccs


def parse_transmodes(delivery):
	l_transmode = open_iff('trnsmode', delivery)

	transmodes = {}
	for transmode in l_transmode:
		t_code, t_description = transmode.split(',')
		transmodes[t_code] = {'description': t_description.strip()}

	return transmodes

def parse_stations(delivery):
	l_stations = open_iff('stations', delivery)

	stations = {}
	for station in l_stations:
		changes, shortname, mintime, _maxtime, country, timezone, attribute, x, y, name = station.split(',')
		stations[shortname.strip()] = {'changes': int(changes), 'mintime': int(mintime) * 60, 'country': country.strip(), 'timezone': int(timezone), 'x': int(x) * 10, 'y': int(y) * 10, 'name': name.strip()}

		# Multiply the RD coordinate by 10
		# Multiply the minimum transfer time by 60s
	
	return stations

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
	continousconnections = parse_continuousconnections(delivery)
	connectionmodes = parse_connectionmodes(delivery)
	changes = parse_changes(delivery)
	timetables = parse_timetables(delivery)

	print "Received file from %s for period %s to %s (%s)" % (companies[delivery['companynumber']]['name'], delivery['firstday'], delivery['lastday'], delivery['description'])

	stations = parse_stations(delivery)

	return {'delivery': delivery, 'companies': companies, 'countries': countries, 'transmodes': transmodes, 'transattributes': transattributes, 'timezones': timezones, 'transattributequestions': transattributequestions, 'footnotes': footnotes, 'continousconnections': continousconnections, 'connectionmodes': connectionmodes, 'changes': changes, 'timetables': timetables}

# parse_delivery()
