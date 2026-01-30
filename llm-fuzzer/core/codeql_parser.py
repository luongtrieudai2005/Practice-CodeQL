import csv
import re
from pathlib import Path
from typing import List, Dict

class CodeQLResultParser:
	""" Parse ket qua tu CodeQL Query """

	def __init__(self, results_csv: str, libpng_path: str):
		self.results_csv = Path(results_csv)
		self.libpng_path = Path(libpng_path)
		self.functions = []

	def parse(self) -> List[Dict]:
		""" Parse CSV va extract function """

		if not self.results_csv.exists():
			raise FileNotFoundError(f"Result file not found : {self.results_csv}")

		with open(self.results_csv, "r", encoding='utf-8') as f:
			reader = csv.DictReader(f)

			for row in reader:
				func_info = self._extract_function_info(row)
				if func_info:
					self.functions.append(func_info)

		return self.functions

	def _extract_function_info(self, row: Dict) -> Dict:
		""" Extract moi hang trong file result"""

		start_line_text = row["Start Line"]

		func_match = re.search(r"function '([^']+)'", start_line_text)
		if not func_match:
			return None

		func_name = func_match.group(1)

		# Extract line number
		line_match = re.search(r"line (\d+)", start_line_text)
		line_num = int(line_match.group(1)) if line_match else None

		# Extract path
		file_path = row['Path']
		full_path = self.libpng_path / file_path.lstrip('/')

		return {
			'name' : func_name,
			'file' : str(full_path),
			'line' : line_num,
			'description' : start_line_text,
			'category' : 'memory_leak'
		}

	def get_unique_functions(self) -> List[Dict]:
		""" Lay danh sach unique function """

		seen = set()
		unique_funcs = []

		for func in self.functions:
			if func['name'] not in seen:
				seen.add(func['name'])
				unique_funcs.append(func)

		print(f"[+] Found {len(unique_funcs)} unique functions")
		return unique_funcs

	def filter_core_functions(self) -> List[Dict]:
		""" Filter cac core functions (not test/contrib) """

		unique = self.get_unique_functions()
		core_funcs = [
			f for f in unique if not any(x in f['file'] for x in ['/contrib/', '/test', 'pngtest'])
		]

		return core_funcs
	