#!/usr/bin/python3
import argparse
import requests
import re

REQUEST_TYPES = set(["get", "post"])

def error_exit(msg):
	print(f"Error: {msg}")
	exit(1)

class Vaccine:
	def __init__(self, url, file, method):
		self.url = url
		self.file = file
		self.method = method

		field = self.get_field_names()
		if len(field) > 1:
			self.username_field_name = field[0]
			self.password_field_name = field[1]
		else:
			self.password_field_name = field[0]

	def __str__(self):
		return f'''- url: {self.url}
- method: {self.method}
- username-field: {self.username_field_name}
- password-field: {self.password_field_name}'''

	def get_field_names(self):
		txt = self.request()
		forms = re.findall(r'<form((.|\s)*?)</form>', txt)
		if not forms:
			error_exit("form block does not exist")
		fields = []
		for form in forms:
			method_match = re.search(r'method="(.*?)"', form[0])
			if not method_match:
				continue
			if method_match.group(1) != self.method:
				continue
			ids = re.findall(r'<input[^>]+id="(.*?)"', form[0])
			fields.append(ids)
		if not fields:
			error_exit("input field not found")
		if len(fields) > 1:
			error_exit("multiple fields exist, cannot determin")
		return fields[0]

	def request(self):
		try:
			response = requests.get(self.url)
		except requests.exceptions.ConnectionError:
			error_exit(f"ERROR: connection refused - {self.url}")
		except:
			error_exit(f"invalid URL - {self.url}")

		if response.status_code != 200:
			error_exit(f"{self.url} - {response}")
		return response.text

	def post(self, username, password):
		data = {
			self.username_field_name: username,
			self.password_field_name: password
		}
		res = requests.post(self.url, json=data)
		print(res)

	def Vaccine():
		post("admin", "admin")


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
	print(vaccine)
	print(args)

if __name__ == '__main__':
	main()
