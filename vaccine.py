#!/usr/bin/python3
import argparse
import requests
import re
import os

REQUEST_TYPES = set(["get", "post"])

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
			token = os.environ.get('TOKEN')
			cookies = {'PHPSESSID': token}
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

	def post(self, username, password):
		if self.username_field_name:
			data = {
				self.username_field_name: username,
				self.password_field_name: password
			}
		else:
			data = {
				self.password_field_name: password
			}

		res = requests.post(self.request_url, data=data)
		print(res)

	def vaccine(self):
		self.post("admin", "aaa")


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
