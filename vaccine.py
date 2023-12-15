#!/usr/bin/python3
import argparse
import requests
import re

REQUEST_TYPES = set(["GET", "POST"])

def error_exit(msg):
	print(f"Error: {msg}")
	exit(1)

class Vaccine:
	def __init__(self, url, file, method):
		self.url = url
		self.file = file
		self.method = method

		self.get_field_names()

	def get_field_names(self):
		txt = self.request()
		print(txt)
		forms = re.findall(r'<form[^>]*>(.*?)</form>', txt)
		print(forms)
		for form in forms:
			fields = re.findall(r'<input[^>]+id="(.*?)"', form)
		print(fields)

	def request(self):
		try:
			r = requests.get(self.url)
		except requests.exceptions.ConnectionError:
			error_exit(f"ERROR: connection refused - {self.url}")
		except:
			error_exit(f"invalid URL - {self.url}")

		if r.status_code != 200:
			error_exit(f"{self.url} - {r}")
		return r.text

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
	print(args)

if __name__ == '__main__':
	main()
