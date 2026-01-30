import re
from pathlib import Path
from typing import Dict, List, Set
import subprocess

class SimpleCodeKnowledgeGraph:
	""" CKG don gian chi cho libpng thoi ! - chua trien khai tree-sitter"""

	def __init__(self, libpng_path : str):
		self.libpng_path = Path(libpng_path)
		self.functions = {}
		self.headers = {}

	def build(self, target_functions : List[Dict]):
		""" Tao CKG cho target functions """

		for func_info in target_functions:
			func_name = func_info["name"]
			file_path = func_info["file"]

			# 1. Lay source code cua function
			func_source = self.get_function_source(file_path, func_name)

			# 2. Tim header file
			headers = self._find_headers(file_path)

			# 3. Tim related functions (duoc goi boi chinh function nay)
			called_funcs = self._find_called_functions(func_source)

			self.functions[func_name] = {
				"source" : func_source,
				"file" : file_path,
				"headers" : headers,
				"calls" : called_funcs,
				"signature" : self._extract_function_signature(func_source, func_name)
			}

			return self

	def _get_function_source(self, file_path : str, func_name : str) -> str:
		""" Lay source code cua function bang len grep """

		try :
			# Tim line chua dinh nghia ham
			grep_result = subprocess.run(
				['grep', '-n', f'^{func_name}\\s*(', file_path],
				capture_output=True,
				text=True
			)

			if not grep_result.stdout:
				# Thu pattern khac
				grep_result = subprocess.run(
					['grep', '-n', func_name, file_path],
					capture_output=True,
					text=True
				)

			if grep_result.stdout:
				line_num = int(grep_result.stdout.split(":")[0])

				# Doc 100 dong
				with open(file_path, 'r') as f:
					lines = f.readlines()
					start = max(0, line_num - 5)
					end = min(len(lines), line_num + 100)
					return ''.join(lines[start:end])

			return ""
		except Exception as e:
			print(f"[!] Error for {func_name} : {e}")
			return ""


	def _find_headers(self, file_path : str) -> List[str]:
		""" Tim cac header duoc include trong file"""

		headers = []
		try:
			with open(file_path, 'r') as f:
				for line in f:
					if line.strip().startswith("#include"):
						match = re.search(r'#include\s+[<"]([^>"]+)[>"]', line)
						if match:
							headers.append(match.group(1))
		except:
			pass

		return headers

	def _find_called_functions(self, source_code : str) -> List[str]:
		""" Tim cac function duoc goi trong source """

		# Pattern: function_name(
		pattern = r'\b([a-z_][a-z0-9_]*)\s*\('
		matches = re.findall(pattern, source_code, re.IGNORECASE)

		keywords = {'if', 'while', 'for', 'switch', 'return', 'sizeof'}
		funcs = [m for m in matches if m not in keywords]

		#Unique
		return list(set(funcs))

	def _extract_signature(self, source_code : str, func_name : str) -> str:
		""" Lay signature """

		lines = source_code.split("\n")
		for i, line in enumerate(lines):
			if _func_name in line and '(' in line:
				# Lay den khi gap '{'
				sig_lines = []
				for j in range(i, min(i + 10, len(lines))):
					sig_lines.append(lines[j])
					if '{' in lines[j]:
						break

				signature = ' '.join(sig_lines).split('{')[0].strip()
				return signature

		return f"<unknown> {func_name}(...)"

	def get_context(self, func_name : str) -> Dict:
		""" Lay noi dung ngu canh cua ham """

		if func_name not in self.functions:
			return None

		return self.functions[func_name]

	def get_related_functions(self, func_name : str) -> List[str]:
		""" Lay cac function co lien quan """

		if func_name not in self.functions:
			return []

		return self.functions[func_name]['calls'][:5]
	